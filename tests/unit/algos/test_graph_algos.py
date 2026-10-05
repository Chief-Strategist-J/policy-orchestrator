from src.features.code_engine.algos.graph import (
    GraphAlgoBfsTraversal,
    GraphAlgoDfsTraversal,
    GraphAlgoDijkstraShortestPath,
    GraphAlgoAstarSearch,
    GraphAlgoPageRankCentrality,
    GraphAlgoDegreeCentrality,
    GraphAlgoConnectedComponents,
    GraphAlgoTarjanScc,
    GraphAlgoSubgraphIsomorphism,
)


def test_algo_graph_01_bfs_traversal():
    adj = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["E"],
        "D": [],
        "E": [],
    }
    res = GraphAlgoBfsTraversal.traverse(adj, start_node="A")
    assert res["visited_order"][0] == "A"
    assert "B" in res["visited_order"]
    assert "C" in res["visited_order"]
    assert res["distances"]["A"] == 0
    assert res["distances"]["B"] == 1
    assert res["distances"]["D"] == 2
    assert res["total_visited"] == 5


def test_algo_graph_02_dfs_traversal_and_cycle():
    adj_acyclic = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": [],
    }
    res1 = GraphAlgoDfsTraversal.traverse(adj_acyclic, start_node="A")
    assert res1["has_cycle"] is False
    assert len(res1["visited_order"]) == 4

    adj_cyclic = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
    }
    res2 = GraphAlgoDfsTraversal.traverse(adj_cyclic, start_node="A")
    assert res2["has_cycle"] is True


def test_algo_graph_03_dijkstra_shortest_path():
    edges = [
        {"source": "A", "target": "B", "weight": 4.0},
        {"source": "A", "target": "C", "weight": 2.0},
        {"source": "C", "target": "B", "weight": 1.0},
        {"source": "B", "target": "D", "weight": 5.0},
        {"source": "C", "target": "D", "weight": 8.0},
    ]
    res = GraphAlgoDijkstraShortestPath.compute(edges, start_node="A", target_node="D")
    assert res["distances"]["D"] == 8.0
    assert res["paths"]["D"] == ["A", "C", "B", "D"]
    assert res["target_distance"] == 8.0
    assert res["target_path"] == ["A", "C", "B", "D"]


def test_algo_graph_04_astar_search():
    edges = [
        {"source": "A", "target": "B", "weight": 1.5},
        {"source": "A", "target": "C", "weight": 2.0},
        {"source": "B", "target": "D", "weight": 3.0},
        {"source": "C", "target": "D", "weight": 1.0},
    ]
    heuristics = {"A": 3.0, "B": 2.0, "C": 1.0, "D": 0.0}
    res = GraphAlgoAstarSearch.search(edges, start_node="A", target_node="D", heuristics=heuristics)
    assert res["found"] is True
    assert res["path"] == ["A", "C", "D"]
    assert res["cost"] == 3.0
    assert res["nodes_expanded"] > 0


def test_algo_graph_05_pagerank_centrality():
    adj = {
        "A": ["B", "C"],
        "B": ["C"],
        "C": ["A"],
        "D": ["C"],
    }
    res = GraphAlgoPageRankCentrality.compute(adj, damping_factor=0.85, max_iterations=50)
    assert res["converged"] is True
    scores = res["scores"]
    assert len(scores) == 4
    assert scores["C"] > scores["D"]
    assert abs(sum(scores.values()) - 1.0) < 1e-3


def test_algo_graph_06_degree_centrality():
    adj = {
        "A": ["B", "C"],
        "B": ["C"],
        "C": ["A"],
    }
    res = GraphAlgoDegreeCentrality.compute(adj, normalized=True)
    assert res["node_count"] == 3
    assert "A" in res["in_degree"]
    assert "A" in res["out_degree"]
    assert res["total_degree"]["A"] > 0


def test_algo_graph_07_connected_components():
    edges = [
        ["A", "B"],
        ["B", "C"],
        ["D", "E"],
    ]
    res = GraphAlgoConnectedComponents.find_components(edges, nodes=["A", "B", "C", "D", "E", "F"])
    assert res["component_count"] == 3
    assert ["A", "B", "C"] in res["components"]
    assert ["D", "E"] in res["components"]
    assert ["F"] in res["components"]


def test_algo_graph_08_tarjan_scc():
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A", "D"],
        "D": ["E"],
        "E": ["F"],
        "F": ["D"],
    }
    res = GraphAlgoTarjanScc.find_sccs(adj)
    assert res["scc_count"] == 2
    assert ["A", "B", "C"] in res["sccs"]
    assert ["D", "E", "F"] in res["sccs"]


def test_algo_graph_09_subgraph_isomorphism():
    target_graph = {
        "1": ["2", "3"],
        "2": ["3"],
        "3": ["4"],
        "4": [],
    }
    pattern_graph = {
        "A": ["B"],
        "B": ["C"],
        "C": [],
    }
    res = GraphAlgoSubgraphIsomorphism.match(target_graph, pattern_graph=pattern_graph)
    assert res["match_count"] >= 1
    assert any(m.get("A") == "1" and m.get("B") == "2" and m.get("C") == "3" for m in res["matches"])
