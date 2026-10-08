"""
================================================================================
UNIT TESTS: KNOWLEDGE GRAPH REST API ENDPOINTS & RFC ENVELOPE
================================================================================
"""

import pytest
from fastapi.testclient import TestClient
from src.api.rest.app import create_app
from src.infra.adapters.graph.in_memory_graph_adapter import InMemoryGraphAdapter
from src.api.rest.v1.dependencies import get_graph_store

@pytest.fixture
def client():
    app = create_app()
    adapter = InMemoryGraphAdapter()
    app.dependency_overrides[get_graph_store] = lambda: adapter
    return TestClient(app)

def test_api_scan_repository(client, tmp_path):
    feat_dir = tmp_path / "src" / "features" / "organizations" / "queries"
    feat_dir.mkdir(parents=True)
    (feat_dir / "organizations.queries.sql").write_text("-- name: FLOW_GET_ORGANIZATIONS", encoding="utf-8")

    res = client.post(
        "/api/v1/file-structure/scan-repository",
        json={"root_dir": str(tmp_path)},
        headers={"x-request-id": "req-test-scan-123", "x-correlation-id": "corr-test-scan-123"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["statusCode"] == 200
    assert "meta" in data
    assert data["meta"]["requestId"] == "req-test-scan-123"
    assert data["data"]["status"] == "success"

def test_api_analyze_impact(client, tmp_path):
    feat_dir = tmp_path / "src" / "features" / "organizations" / "queries"
    feat_dir.mkdir(parents=True)
    (feat_dir / "organizations.queries.sql").write_text("-- name: FLOW_GET_ORGANIZATIONS", encoding="utf-8")
    client.post("/api/v1/file-structure/scan-repository", json={"root_dir": str(tmp_path)})

    res = client.post(
        "/api/v1/file-structure/impact-analysis",
        json={"target_id": "queries_organizations", "direction": "UPSTREAM", "max_depth": 6},
        headers={"x-request-id": "req-test-impact-456"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["target_id"] == "queries_organizations"
    assert data["data"]["direction"] == "UPSTREAM"
    assert "required_verification_commands" in data["data"]
