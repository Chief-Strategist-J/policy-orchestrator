"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API CONTRACT & EXECUTION TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests HTTP REST endpoints for:
   - Layer 1 Algorithm Contracts & G4 Adapters
   - Dynamic Pipeline Composition
   - Direct Algorithm Execution (`POST /api/v1/algos/execute/{algo_id}`)
   - Dedicated Vector Algorithm REST Endpoints
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
    assert json_data["meta"]["status"] == "success"
    assert json_data["data"]["total_contracts"] == 33


def test_api_filter_contracts_by_category(client):
    response = client.get("/api/v1/algos/contracts?category=search")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["total_contracts"] == 15


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
