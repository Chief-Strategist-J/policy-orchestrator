"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API CONTRACT ENDPOINT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests HTTP REST endpoints for Layer 1 Algorithm Contracts, G4 Adapters,
   and dynamic pipeline composition.
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
