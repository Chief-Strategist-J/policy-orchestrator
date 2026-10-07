"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API CONTRACT & EXECUTION TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests HTTP REST endpoints for:
   - Layer 1 Algorithm Contracts & G4 Adapters
   - Dynamic Pipeline Composition
   - Direct Universal Algorithm Execution (`POST /api/v1/algos/execute/{algo_id}`)
   - Dedicated Search, Observability, Update & Vector Endpoints
   - Strict adherence to `api-request-response-structure.md` envelope format.
================================================================================
"""

import pytest
from fastapi.testclient import TestClient
from src.api.rest.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_api_list_algorithm_contracts(client):
    response = client.get("/api/v1/algos/contracts")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["statusCode"] == 200
    assert json_data["data"]["total_contracts"] == 268


def test_api_filter_contracts_by_category(client):
    response = client.get("/api/v1/algos/contracts?category=search")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["total_contracts"] == 41


def test_api_get_single_contract(client):
    response = client.get("/api/v1/algos/contracts/ALGO-SRCH-11")
    assert response.status_code == 200
    json_data = response.json()
    data = json_data["data"]
    assert data["id"] == "ALGO-SRCH-11"
    assert data["name"] == "SearchEngineAhoCorasickAlgo"
    assert "text" in data["input_schema"]["properties"]


def test_api_list_adapters(client):
    response = client.get("/api/v1/algos/adapters")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["total_adapters"] >= 5


def test_api_compose_pipeline(client):
    payload = {
        "algo_ids": ["ALGO-SRCH-03", "ALGO-SRCH-11", "ALGO-OBS-16"],
        "strict_check": True,
    }
    response = client.post("/api/v1/algos/compose", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["meta"]["status"] == "success"
    assert json_data["data"]["total_steps"] == 3
    assert json_data["data"]["is_valid"] is True


def test_api_execute_algorithm_direct_vector(client):
    payload = {
        "inputs": {"vector": [3.0, 4.0]},
    }
    response = client.post("/api/v1/algos/execute/ALGO-VEC-01", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["statusCode"] == 200
    assert json_data["data"]["algo_id"] == "ALGO-VEC-01"
    norm = json_data["data"]["result"]["normalized_vector"]
    assert abs(norm[0] - 0.6) < 1e-5
    assert abs(norm[1] - 0.8) < 1e-5


def test_api_execute_algorithm_direct_search(client):
    payload = {
        "inputs": {
            "text": "error occurred in line 42 with fatal crash",
            "patterns": ["error", "fatal"],
        }
    }
    response = client.post("/api/v1/algos/execute/ALGO-SRCH-11", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["result"]["total_matches"] == 2


def test_api_search_dedicated_endpoints(client):
    glob_res = client.post("/api/v1/algos/search/glob-match", json={"pattern": "*.py", "path": "main.py"})
    assert glob_res.status_code == 200
    assert glob_res.json()["data"]["matches"] is True

    trigram_res = client.post("/api/v1/algos/search/trigram-index", json={"text": "hello"})
    assert trigram_res.status_code == 200
    assert trigram_res.json()["data"]["trigrams_count"] > 0

    aho_res = client.post("/api/v1/algos/search/aho-corasick", json={"text": "abcde", "patterns": ["bc", "de"]})
    assert aho_res.status_code == 200
    assert aho_res.json()["data"]["total_matches"] == 2


def test_api_observability_dedicated_endpoints(client):
    span_res = client.post("/api/v1/algos/observability/span-track", json={"content": "line1\nline2\nline3", "offset": 7})
    assert span_res.status_code == 200
    assert span_res.json()["data"]["line"] == 2

    ast_res = client.post("/api/v1/algos/observability/ast", json={"code": "def hello(): pass", "language": "python"})
    assert ast_res.status_code == 200
    assert ast_res.json()["data"]["total_nodes"] >= 1

    sym_res = client.post("/api/v1/algos/observability/symbols", json={"code": "x = 10\ndef foo(): pass"})
    assert sym_res.status_code == 200
    assert sym_res.json()["data"]["total_symbols"] >= 1


def test_api_update_dedicated_endpoints(client):
    cst_res = client.post("/api/v1/algos/update/cst-match", json={"code": "def func(): return 1", "node_type": "function"})
    assert cst_res.status_code == 200
    assert cst_res.json()["data"]["matches_count"] >= 1

    diff_res = client.post("/api/v1/algos/update/diff", json={"original_content": "a\n", "modified_content": "b\n", "file_path": "f.txt"})
    assert diff_res.status_code == 200
    assert diff_res.json()["data"]["has_changes"] is True


def test_api_vector_normalize_endpoint(client):
    payload = {"vector": [1.0, 1.0, 1.0, 1.0], "eps": 1e-12}
    response = client.post("/api/v1/algos/vector/normalize", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["original_dimension"] == 4
    assert len(json_data["data"]["normalized_vector"]) == 4


def test_api_vector_slice_endpoint(client):
    payload = {"vector": [1.0, 2.0, 3.0, 4.0], "target_dim": 2, "renormalize": True}
    response = client.post("/api/v1/algos/vector/slice", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["target_dimension"] == 2
    assert len(json_data["data"]["sliced_vector"]) == 2


def test_api_vector_quantize_scalar_endpoint(client):
    payload = {"vector": [0.1, 0.5, 0.9], "bits": 8}
    response = client.post("/api/v1/algos/vector/quantize/scalar", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]["quantized_values"]) == 3


def test_api_vector_chunk_endpoint(client):
    payload = {
        "text": "First sentence about architecture. Second sentence about design. Third sentence about patterns.",
        "max_chunk_size": 100,
        "overlap": 20,
    }
    response = client.post("/api/v1/algos/vector/chunk", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["total_chunks"] >= 1


def test_api_vector_filter_pre_filter_endpoint(client):
    payload = {
        "vectors": [[0.0, 0.0], [1.0, 1.0]],
        "metadata": [{"tenant": "alpha"}, {"tenant": "beta"}],
        "query": [0.1, 0.1],
        "filters": {"tenant": "alpha"},
        "k": 1,
    }
    response = client.post("/api/v1/algos/vector-filter/pre-filter", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["passed_filter_count"] == 1
    assert len(json_data["data"]["matches"]) == 1


def test_api_vector_filter_post_filter_endpoint(client):
    payload = {
        "vectors": [[0.0, 0.0], [1.0, 1.0]],
        "metadata": [{"lang": "en"}, {"lang": "fr"}],
        "query": [0.1, 0.1],
        "filters": {"lang": "en"},
        "k": 1,
        "oversample_factor": 2.0,
    }
    response = client.post("/api/v1/algos/vector-filter/post-filter", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["surviving_count"] == 1


def test_api_vector_filter_in_graph_endpoint(client):
    payload = {
        "vectors": [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]],
        "metadata": [{"status": "active"}, {"status": "inactive"}, {"status": "active"}],
        "adjacency": {"0": [1], "1": [2], "2": []},
        "entry_point": 0,
        "query": [1.9, 0.0],
        "filters": {"status": "active"},
        "k": 1,
        "ef_search": 4,
    }
    response = client.post("/api/v1/algos/vector-filter/in-graph", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert len(json_data["data"]["neighbors"]) >= 1


def test_api_vector_filter_selectivity_plan_endpoint(client):
    payload = {
        "total_vectors": 5000,
        "metadata_sample": [{"tenant": "T1"}, {"tenant": "T2"}],
        "filters": {"tenant": "T1"},
        "is_security_filter": True,
    }
    response = client.post("/api/v1/algos/vector-filter/selectivity-plan", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["selected_strategy"] == "pre_filter_isolated"


def test_api_vector_filter_partitioned_endpoint(client):
    payload = {
        "partitions": {"tenant_A": [{"id": "doc1", "vector": [1.0, 0.0], "metadata": {}}]},
        "target_partition": "tenant_A",
        "query": [0.9, 0.1],
        "k": 1,
    }
    response = client.post("/api/v1/algos/vector-filter/partitioned", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["partition_size"] == 1


def test_api_search_wu_manber_endpoint(client):
    payload = {"text": "the quick brown fox", "patterns": ["quick", "fox"], "block_size": 2}
    response = client.post("/api/v1/algos/search/wu-manber", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["total_matches"] >= 2


def test_api_search_levenshtein_distance_endpoint(client):
    payload = {"source": "kitten", "target": "sitting", "include_matrix": False}
    response = client.post("/api/v1/algos/search/levenshtein-distance", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["distance"] == 3


def test_api_search_fzf_fuzzy_endpoint(client):
    payload = {"candidates": ["src/service.py", "tests/test.py"], "query": "srv"}
    response = client.post("/api/v1/algos/search/fzf-fuzzy", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["total_matches"] >= 1


def test_api_search_bwt_endpoint(client):
    payload = {"text": "banana", "sentinel": "$"}
    response = client.post("/api/v1/algos/search/burrows-wheeler-transform", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["reconstructed_text"] == "banana"


def test_api_graph_query_plan_endpoints(client):
    # Test BFS query plan
    res = client.post("/api/v1/algos/graph/bfs-query-plan", json={"start_node": "n1", "max_depth": 2})
    assert res.status_code == 200
    assert "BFS_TRAVERSAL" in res.json()["data"]["query_name"]

    # Test PageRank query plan
    res = client.post("/api/v1/algos/graph/pagerank-query-plan", json={"graph_name": "prod_graph"})
    assert res.status_code == 200
    assert "PAGERANK_CENTRALITY" in res.json()["data"]["query_name"]

    # Test Louvain query plan
    res = client.post("/api/v1/algos/graph/louvain-query-plan", json={"graph_name": "social_graph"})
    assert res.status_code == 200
    assert "LOUVAIN_COMMUNITIES" in res.json()["data"]["query_name"]

    # Test Metapath query plan
    res = client.post("/api/v1/algos/graph/metapath-query-plan", json={"start_node": "A", "metapath": ["KNOWS", "WORKS_AT"]})
    assert res.status_code == 200
    assert "METAPATH_TRAVERSAL" in res.json()["data"]["query_name"]



