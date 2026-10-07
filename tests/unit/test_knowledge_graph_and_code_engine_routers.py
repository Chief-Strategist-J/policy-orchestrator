"""
================================================================================
TEST SUITE: KNOWLEDGE GRAPH & CODE ENGINE REST ROUTERS
================================================================================
"""

from fastapi.testclient import TestClient
from src.api.rest.app import app

client = TestClient(app)


def test_knowledge_graph_foundation_router():
    resp = client.post("/api/v1/algos/knowledge-graph/foundation/bitemporal-modeling", json={"payload": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data
    assert data["statusCode"] == 200


def test_knowledge_graph_query_reasoning_router():
    resp = client.post("/api/v1/algos/knowledge-graph/query-reasoning/gql-evaluator", json={"payload": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data


def test_knowledge_graph_embeddings_gnn_router():
    resp = client.post("/api/v1/algos/knowledge-graph/embeddings-gnn/transe", json={"payload": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data


def test_knowledge_graph_ops_observability_router():
    resp = client.post("/api/v1/algos/knowledge-graph/ops-observability/cdc-synchronizer", json={"payload": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data


def test_code_engine_diff_buffer_router():
    resp = client.post("/api/v1/algos/code-engine/diff-buffer/fuzzy-patch", json={"payload": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data


def test_code_engine_mutation_router():
    resp = client.post("/api/v1/algos/code-engine/mutation-classifiers/cas-content-hash", json={"payload": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data
