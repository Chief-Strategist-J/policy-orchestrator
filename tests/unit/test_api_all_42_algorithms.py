import json
import pytest
from fastapi.testclient import TestClient
from src.api.rest.app import create_app
from src.features.code_engine.registry.algorithm_catalog import BUILTIN_ALGORITHM_CONTRACTS


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_api_has_exactly_42_builtin_algorithms(client):
    res = client.get("/api/v1/algos/contracts")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total_contracts"] == 42
    assert len(body["data"]["contracts"]) == 42


def test_api_execute_all_42_algorithms_direct(client):
    test_inputs = {
        "ALGO-SRCH-01": {"root_dir": "src/features"},
        "ALGO-SRCH-02": {"root_dir": "src/features"},
        "ALGO-SRCH-03": {"root_dir": "src/features"},
        "ALGO-SRCH-04": {"pattern": "*.py", "file_paths": ["test.py", "main.rs"]},
        "ALGO-SRCH-05": {"file_path": "pyproject.toml"},
        "ALGO-SRCH-06": {"file_path": "pyproject.toml"},
        "ALGO-SRCH-07": {"file_path": "pyproject.toml", "max_bytes": 1000000},
        "ALGO-SRCH-08": {"file_path": "pyproject.toml"},
        "ALGO-SRCH-09": {"text": "algorithm inverted index test"},
        "ALGO-SRCH-10": {"data": "hello\nworld\ntest\n", "byte": "\n"},
        "ALGO-SRCH-11": {"text": "the quick brown fox", "patterns": ["quick", "fox"]},
        "ALGO-SRCH-12": {"text": "user@example.com", "pattern": r"user@example\.com"},
        "ALGO-SRCH-13": {"file_path": "pyproject.toml", "needle": "policy"},
        "ALGO-SRCH-14": {"text": "line1\nline2 target\nline3", "match_offset": 6},
        "ALGO-SRCH-15": {"file_path": "pyproject.toml", "needle": "name"},
        "ALGO-OBS-16": {"content": "alpha\nbeta\ngamma", "offset": 7},
        "ALGO-OBS-17": {"code": "def foo():\n    return 42", "language": "python"},
        "ALGO-OBS-18": {"code": "x = 10\ndef bar():\n    y = 20\n    return x + y"},
        "ALGO-OBS-19": {"code": "def clean():\n    return 1"},
        "ALGO-OBS-20": {"file_paths": ["src/api/rest/app.py"]},
        "ALGO-OBS-21": {"code": "class Sample:\n    def method(self):\n        pass"},
        "ALGO-UPD-22": {"code": "x = old_fn()", "pattern": "old_fn", "replacement": "new_fn"},
        "ALGO-UPD-23": {"file_path": "/tmp/test_patch.txt", "patches": []},
        "ALGO-UPD-24": {"original_content": "line1\nline2", "modified_content": "line1\nline2_mod"},
        "ALGO-VEC-01": {"vector": [3.0, 4.0]},
        "ALGO-VEC-02": {"vectors": [[1.0, 2.0], [3.0, 4.0]]},
        "ALGO-VEC-03": {"vector": [1.0, 2.0, 3.0, 4.0]},
        "ALGO-VEC-04": {"vector": [1.0, 5.0, 10.0]},
        "ALGO-VEC-05": {"vector": [float(i) for i in range(128)], "target_dim": 32},
        "ALGO-VEC-06": {"vector": [0.1, -0.5, 0.9, -0.2], "bits": 8},
        "ALGO-VEC-07": {"vector": [0.5, -0.2, 0.8, -0.9]},
        "ALGO-VEC-08": {"token_embeddings": [[1.0, 2.0], [3.0, 4.0]]},
        "ALGO-VEC-09": {"text": "Hello world from vector semantic chunker.", "max_chunk_size": 50, "overlap": 10},
        "ALGO-GRAPH-01": {"adjacency_list": {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}, "start_node": "A"},
        "ALGO-GRAPH-02": {"adjacency_list": {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}, "start_node": "A"},
        "ALGO-GRAPH-03": {"weighted_edges": [{"source": "A", "target": "B", "weight": 1.0}], "start_node": "A", "target_node": "B"},
        "ALGO-GRAPH-04": {"weighted_edges": [{"source": "A", "target": "B", "weight": 1.0}], "start_node": "A", "target_node": "B"},
        "ALGO-GRAPH-05": {"adjacency_list": {"A": ["B"], "B": ["A"]}},
        "ALGO-GRAPH-06": {"adjacency_list": {"A": ["B"], "B": ["A"]}},
        "ALGO-GRAPH-07": {"edges": [["A", "B"], ["C", "D"]]},
        "ALGO-GRAPH-08": {"adjacency_list": {"A": ["B"], "B": ["A"]}},
        "ALGO-GRAPH-09": {"target_graph": {"1": ["2"], "2": []}, "pattern_graph": {"A": ["B"], "B": []}},
    }

    for contract in BUILTIN_ALGORITHM_CONTRACTS:
        algo_id = contract.id
        assert algo_id in test_inputs, f"Missing test input for {algo_id}"
        payload = {"inputs": test_inputs[algo_id], "parameters": {}}
        res = client.post(f"/api/v1/algos/execute/{algo_id}", json=payload)
        assert res.status_code == 200, f"Execution failed for {algo_id}: {res.text}"
        body = res.json()
        assert body["success"] is True
        assert body["meta"]["status"].lower() == "success"
        assert body["data"]["algo_id"] == algo_id


def test_api_graph_dedicated_endpoints(client):
    res_bfs = client.post("/api/v1/algos/graph/bfs", json={"adjacency_list": {"A": ["B"]}, "start_node": "A"})
    assert res_bfs.status_code == 200
    assert res_bfs.json()["data"]["total_visited"] >= 1

    res_dfs = client.post("/api/v1/algos/graph/dfs", json={"adjacency_list": {"A": ["B"]}, "start_node": "A"})
    assert res_dfs.status_code == 200
    assert res_dfs.json()["data"]["total_visited"] >= 1

    res_dijkstra = client.post("/api/v1/algos/graph/dijkstra", json={"weighted_edges": [{"source": "A", "target": "B", "weight": 2.5}], "start_node": "A", "target_node": "B"})
    assert res_dijkstra.status_code == 200
    assert res_dijkstra.json()["data"]["target_distance"] == 2.5

    res_astar = client.post("/api/v1/algos/graph/astar", json={"weighted_edges": [{"source": "A", "target": "B", "weight": 1.0}], "start_node": "A", "target_node": "B"})
    assert res_astar.status_code == 200
    assert res_astar.json()["data"]["found"] is True

    res_pr = client.post("/api/v1/algos/graph/pagerank", json={"adjacency_list": {"A": ["B"], "B": ["A"]}})
    assert res_pr.status_code == 200
    assert res_pr.json()["data"]["converged"] is True

    res_dc = client.post("/api/v1/algos/graph/degree-centrality", json={"adjacency_list": {"A": ["B"], "B": ["A"]}})
    assert res_dc.status_code == 200
    assert res_dc.json()["data"]["node_count"] == 2

    res_cc = client.post("/api/v1/algos/graph/connected-components", json={"edges": [["A", "B"], ["C", "D"]]})
    assert res_cc.status_code == 200
    assert res_cc.json()["data"]["component_count"] == 2

    res_scc = client.post("/api/v1/algos/graph/tarjan-scc", json={"adjacency_list": {"A": ["B"], "B": ["A"]}})
    assert res_scc.status_code == 200
    assert res_scc.json()["data"]["scc_count"] == 1

    res_sub = client.post("/api/v1/algos/graph/subgraph-match", json={"target_graph": {"1": ["2"], "2": []}, "pattern_graph": {"A": ["B"], "B": []}})
    assert res_sub.status_code == 200
    assert res_sub.json()["data"]["match_count"] >= 1
