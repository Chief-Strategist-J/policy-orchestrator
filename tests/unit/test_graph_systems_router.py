"""
REST API Tests for Graph Systems Endpoints (#301-320).
"""

import pytest
from fastapi.testclient import TestClient
from src.api.rest.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_api_register_allocation(client):
    payload = {
        "interference_adjacency": {
            "v1": ["v2", "v3"],
            "v2": ["v1", "v3"],
            "v3": ["v1", "v2"],
        },
        "k_registers": 3,
    }
    response = client.post("/api/v1/algos/graph/systems/register-allocation", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["is_successful"] is True


def test_api_critical_path_pert(client):
    payload = {
        "dependency_dag": {"A": ["B"], "B": []},
        "durations": {"A": 5.0, "B": 3.0},
    }
    response = client.post("/api/v1/algos/graph/systems/critical-path-pert", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["project_duration"] == 8.0


def test_api_tracing_garbage_collection(client):
    payload = {
        "references": {"R": ["A"], "A": ["B"], "X": ["Y"]},
        "roots": ["R"],
    }
    response = client.post("/api/v1/algos/graph/systems/tracing-garbage-collection", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "R" in res["data"]["live_objects"]
    assert "X" in res["data"]["garbage_objects"]


def test_api_chandy_misra_haas_deadlock(client):
    payload = {
        "wait_for_graph": {"P1": ["P2"], "P2": ["P1"]},
    }
    response = client.post("/api/v1/algos/graph/systems/chandy-misra-haas-deadlock", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["is_deadlocked"] is True


def test_api_spanning_tree_protocol_stp(client):
    payload = {
        "bridge_priorities": {"SW1": 4096, "SW2": 8192},
        "links": [["SW1", "SW2", 4.0]],
    }
    response = client.post("/api/v1/algos/graph/systems/spanning-tree-protocol-stp", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["root_bridge"] == "SW1"


def test_api_attack_graph_path_analysis(client):
    payload = {
        "initial_facts": ["attacker_on_internet", "vuln_ssh"],
        "derivation_rules": [
            {
                "name": "rce",
                "premises": ["attacker_on_internet", "vuln_ssh"],
                "conclusion": "db_root",
                "difficulty": 1.0,
            }
        ],
        "target_assets": ["db_root"],
    }
    response = client.post("/api/v1/algos/graph/systems/attack-graph-path-analysis", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "db_root" in res["data"]["reachable_targets"]
