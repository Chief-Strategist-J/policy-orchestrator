"""
REST API Tests for All Graph Algorithm Subdomain Routers (#1-300).
Zero-inline-comment compliance across all test suites.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.rest.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_api_graph_traversal_direction_optimizing_bfs(client):
    payload = {
        "adjacency": {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []},
        "source": "A",
    }
    response = client.post("/api/v1/algos/graph/traversal/direction-optimizing-bfs", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["distances"]["D"] == 2


def test_api_graph_traversal_contraction_hierarchies(client):
    payload = {
        "adjacency": {
            "A": [["B", 1.0], ["C", 5.0]],
            "B": [["C", 2.0]],
            "C": [],
        },
        "source": "A",
        "target": "C",
    }
    response = client.post("/api/v1/algos/graph/traversal/contraction-hierarchies", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["distance"] == 3.0


def test_api_graph_flows_boruvka_mst(client):
    payload = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
            ["A", "B", 1.0],
            ["B", "C", 2.0],
            ["C", "D", 3.0],
            ["A", "D", 10.0],
        ],
    }
    response = client.post("/api/v1/algos/graph/flows/boruvka-mst", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["total_weight"] == 6.0


def test_api_graph_flows_dinic_max_flow(client):
    payload = {
        "edges": [
            ["s", "u", 10.0],
            ["s", "v", 5.0],
            ["u", "v", 15.0],
            ["u", "t", 10.0],
            ["v", "t", 10.0],
        ],
        "source": "s",
        "sink": "t",
    }
    response = client.post("/api/v1/algos/graph/flows/dinic-max-flow", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["max_flow"] == 15.0


def test_api_graph_centrality_betweenness(client):
    payload = {
        "adjacency": {
            "A": [["B", 1.0]],
            "B": [["A", 1.0], ["C", 1.0]],
            "C": [["B", 1.0]],
        },
        "is_directed": False,
        "normalized": True,
    }
    response = client.post("/api/v1/algos/graph/centrality/betweenness", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["vertex_betweenness"]["B"] > res["data"]["vertex_betweenness"]["A"]


def test_api_graph_centrality_densest_subgraph(client):
    payload = {
        "adjacency": {
            "A": ["B", "C"],
            "B": ["A", "C"],
            "C": ["A", "B", "D"],
            "D": ["C"],
        }
    }
    response = client.post("/api/v1/algos/graph/centrality/densest-subgraph", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["max_density"] > 0.0


def test_api_graph_communities_leiden_cpm(client):
    payload = {
        "adjacency": {
            "A": ["B", "C"],
            "B": ["A", "C"],
            "C": ["A", "B"],
            "D": ["E"],
            "E": ["D"],
        },
        "resolution": 0.1,
    }
    response = client.post("/api/v1/algos/graph/communities/leiden-cpm", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["num_communities"] >= 2


def test_api_graph_communities_weisfeiler_lehman(client):
    payload = {
        "graph1": {"A": ["B"], "B": ["A"]},
        "graph2": {"X": ["Y"], "Y": ["X"]},
    }
    response = client.post("/api/v1/algos/graph/communities/weisfeiler-lehman-isomorphism", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["isomorphic"] is True


def test_api_graph_dynamic_incremental_topo_sort(client):
    payload = {
        "initial_nodes": ["A", "B", "C"],
        "edges_to_add": [["A", "B"], ["B", "C"]],
    }
    response = client.post("/api/v1/algos/graph/dynamic/incremental-topo-sort", json=payload)
    assert response.status_code == 200
    res = response.json()
    order = res["data"]["final_topological_order"]
    assert order["A"] < order["B"] < order["C"]


def test_api_graph_dynamic_midas_anomaly(client):
    payload = {
        "edge_stream": [
            ["u1", "v1", 1.0],
            ["u1", "v1", 1.0],
            ["u1", "v1", 1.0],
            ["u1", "v1", 1.0],
        ],
        "threshold": 1.0,
    }
    response = client.post("/api/v1/algos/graph/dynamic/midas-anomaly-detection", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert len(res["data"]["scored_events"]) == 4


def test_api_graph_embeddings_textrank(client):
    payload = {
        "tokens_or_sentences": ["machine", "learning", "graph", "algorithms", "machine", "learning"],
        "window_size": 2,
    }
    response = client.post("/api/v1/algos/graph/embeddings/textrank", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["converged"] is True
    assert "machine" in res["data"]["ranks"]


def test_api_graph_embeddings_d_separation(client):
    payload = {
        "dag_adjacency": {"A": ["B"], "B": ["C"], "C": []},
        "set_x": ["A"],
        "set_y": ["C"],
        "conditioning_set": ["B"],
    }
    response = client.post("/api/v1/algos/graph/embeddings/d-separation", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["is_d_separated"] is True
