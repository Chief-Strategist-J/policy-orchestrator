"""Unit tests for Graph Representation and Traversal/Shortest Path algorithms."""

import pytest
from src.features.code_engine.algos.graph.representation import (
    GraphAlgoAdjacencyMatrix,
    GraphAlgoCsrCsc,
    GraphAlgoEdgeListCoo,
    GraphAlgoIncidenceHypergraph,
    GraphAlgoDynamicAdjacency,
    GraphAlgoWebGraphCompression,
    GraphAlgoK2Tree,
    GraphAlgoBitmapAdjacency,
    GraphAlgoRcmReordering,
    GraphAlgoVertexIdMapping,
    GraphAlgoMultigraphTypedIndex,
    GraphAlgoHierarchicalCoarsening,
)
from src.features.code_engine.algos.graph.traversal_shortest_path import (
    GraphAlgoDirectionOptimizingBfs,
    GraphAlgoIterativeDfsClassified,
    GraphAlgoIddfs,
    GraphAlgoLexBfs,
    GraphAlgoParallelBfs,
    GraphAlgoRandomWalkAlias,
    GraphAlgoEulerTourTree,
    GraphAlgoTopologicalSort,
    GraphAlgoJohnsonCycleEnumeration,
    GraphAlgoBipartiteTest,
    GraphAlgoDaryHeapDijkstra,
    GraphAlgoBellmanFordMoore,
    GraphAlgoJohnsonAllPairs,
    GraphAlgoFloydWarshall,
    GraphAlgoDagShortestLongestPath,
    GraphAlgoZeroOneBfs,
    GraphAlgoDialsShortestPath,
    GraphAlgoBidirectionalBfs,
    GraphAlgoBidirectionalDijkstra,
    GraphAlgoAltShortestPath,
    GraphAlgoContractionHierarchies,
    GraphAlgoHubLabeling,
    GraphAlgoYenKShortestPaths,
    GraphAlgoSuurballeDisjointPaths,
    GraphAlgoResourceConstrainedShortestPath,
    GraphAlgoParetoShortestPath,
    GraphAlgoWidestBottleneckPath,
    GraphAlgoKarpMinMeanCycle,
    GraphAlgoMultiSourceBfs,
    GraphAlgoTemporalCsaPath,
    TemporalConnection,
    GraphAlgoRaptorRouting,
    TransitRoute,
    TransitTrip,
    StopTime,
)


def test_adjacency_matrix() -> None:
    res = GraphAlgoAdjacencyMatrix.construct(
        nodes=["A", "B", "C"],
        edges=[{"source": "A", "target": "B", "weight": 2.5}, {"source": "B", "target": "C", "weight": 1.5}],
        directed=True,
    )
    assert res["matrix"][0][1] == 2.5
    assert res["matrix"][0][2] == 0.0
    p2 = GraphAlgoAdjacencyMatrix.matrix_power(res["matrix"], 2)
    assert p2[0][2] == 3.75


def test_csr_csc() -> None:
    nodes = ["A", "B", "C"]
    edges = [
        {"source": "A", "target": "B", "weight": 1.0},
        {"source": "A", "target": "C", "weight": 2.0},
        {"source": "B", "target": "C", "weight": 3.0},
    ]
    res = GraphAlgoCsrCsc.build(nodes, edges)
    assert res["csr"]["offsets"][0] == 0
    assert res["csr"]["offsets"][1] == 2


def test_edge_list_coo() -> None:
    edges = [
        {"source": "A", "target": "B", "weight": 1.0},
        {"source": "A", "target": "B", "weight": 2.0},
        {"source": "B", "target": "C", "weight": 3.0},
    ]
    res = GraphAlgoEdgeListCoo.normalize_and_deduplicate(edges)
    assert res["num_unique_edges"] == 2


def test_incidence_hypergraph() -> None:
    vertices = ["v1", "v2", "v3", "v4"]
    hyperedges = {
        "e1": ["v1", "v2", "v3"],
        "e2": ["v2", "v3", "v4"],
    }
    res = GraphAlgoIncidenceHypergraph.construct(vertices, hyperedges)
    assert "clique_projection_edges" in res
    assert len(res["clique_projection_edges"]) > 0


def test_dynamic_adjacency() -> None:
    base_edges = [{"source": "u", "target": "v", "weight": 1.0}]
    mutations = [{"op": "add_edge", "source": "u", "target": "w", "weight": 5.0}]
    res = GraphAlgoDynamicAdjacency.apply_mutations(base_edges, mutations)
    assert res["num_edges"] == 2


def test_webgraph_compression() -> None:
    adj = {0: [1, 2, 3], 1: [2, 3, 4], 2: [3, 4, 5]}
    res = GraphAlgoWebGraphCompression.compress(adj)
    assert "compressed_nodes" in res
    decomp = GraphAlgoWebGraphCompression.decompress(res["compressed_nodes"])
    assert decomp[0] == [1, 2, 3]


def test_k2_tree() -> None:
    edges = [(0, 1), (1, 2), (2, 3)]
    tree = GraphAlgoK2Tree.build(4, edges, k=2)
    assert 1 in GraphAlgoK2Tree.query_out_neighbors(tree, 0)
    assert 2 not in GraphAlgoK2Tree.query_out_neighbors(tree, 0)
    assert 0 in GraphAlgoK2Tree.query_in_neighbors(tree, 1)


def test_bitmap_adjacency() -> None:
    edges = [(0, 1), (1, 2), (2, 0)]
    bm = GraphAlgoBitmapAdjacency.construct(3, edges, directed=False)
    triangles = GraphAlgoBitmapAdjacency.count_triangles(bm["bitmaps"], 3)
    assert triangles == 1


def test_rcm_reordering() -> None:
    adj = {"0": ["1", "2"], "1": ["0", "3"], "2": ["0", "3"], "3": ["1", "2"]}
    res = GraphAlgoRcmReordering.reorder(adj)
    assert len(res["permutation"]) == 4


def test_vertex_id_mapping() -> None:
    res = GraphAlgoVertexIdMapping.create_mapping(["node_a", "node_b", "node_c"])
    assert res["symbol_to_int"]["node_a"] == 0
    assert res["int_to_symbol"][0] == "node_a"


def test_multigraph_typed_index() -> None:
    edges = [
        {"source": "alice", "target": "bob", "edge_type": "FRIEND", "weight": 1.0},
        {"source": "alice", "target": "company", "edge_type": "WORKS_AT", "weight": 2.0},
    ]
    res = GraphAlgoMultigraphTypedIndex.build_index(edges)
    assert "alice" in res["typed_out_index"]
    assert "FRIEND" in res["typed_out_index"]["alice"]


def test_hierarchical_coarsening() -> None:
    nodes = ["A", "B", "C", "D"]
    edges = [
        {"source": "A", "target": "B", "weight": 10.0},
        {"source": "B", "target": "C", "weight": 1.0},
        {"source": "C", "target": "D", "weight": 8.0},
    ]
    res = GraphAlgoHierarchicalCoarsening.coarsen_hierarchy(nodes, edges, max_levels=2, min_nodes=2)
    assert res["num_levels"] >= 1


def test_direction_optimizing_bfs() -> None:
    nodes = ["A", "B", "C", "D"]
    out_adj = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    in_adj = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
    res = GraphAlgoDirectionOptimizingBfs.traverse(nodes, out_adj, in_adj, "A")
    assert res["distances"]["D"] == 2


def test_iterative_dfs_classified() -> None:
    nodes = ["A", "B", "C", "D"]
    adj = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    res = GraphAlgoIterativeDfsClassified.traverse(nodes, adj)
    assert "topological_order" in res
    assert len(res["topological_order"]) == 4


def test_iddfs() -> None:
    adj = {"A": ["B", "C"], "B": ["D"], "C": ["E"], "D": ["F"], "E": [], "F": []}
    res = GraphAlgoIddfs.search(adj, "A", "F", max_search_depth=5)
    assert res["found"] is True
    assert res["path"] == ["A", "B", "D", "F"]


def test_lex_bfs() -> None:
    nodes = ["0", "1", "2", "3"]
    adj = {"0": ["1", "2"], "1": ["0", "2", "3"], "2": ["0", "1", "3"], "3": ["1", "2"]}
    res = GraphAlgoLexBfs.compute(nodes, adj)
    assert len(res["ordering"]) == 4
    assert res["chordal_graph_certified"] is True


def test_bipartite_test() -> None:
    bip_adj = {"A": ["B", "D"], "B": ["A", "C"], "C": ["B", "D"], "D": ["A", "C"]}
    bip = GraphAlgoBipartiteTest[str](bip_adj)
    assert bip.is_bipartite() is True

    odd_adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    non_bip = GraphAlgoBipartiteTest[str](odd_adj)
    is_b, _, cycle = non_bip.analyze()
    assert is_b is False
    assert cycle is not None


def test_johnson_cycle_enumeration() -> None:
    adj = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": []}
    jce = GraphAlgoJohnsonCycleEnumeration[str](adj)
    assert jce.has_cycle() is True
    cycles = jce.enumerate_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B", "C"}


def test_dag_shortest_longest_path() -> None:
    adj = {
        "A": [("B", 3.0), ("C", 2.0)],
        "B": [("D", 4.0)],
        "C": [("D", 1.0)],
        "D": [],
    }
    dag_algo = GraphAlgoDagShortestLongestPath[str](adj)
    s_dist, _ = dag_algo.compute_shortest_paths("A")
    assert s_dist["D"] == 3.0
    l_dist, _ = dag_algo.compute_longest_paths("A")
    assert l_dist["D"] == 7.0


def test_alt_shortest_path() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 4.0)],
        "B": [("C", 2.0), ("D", 5.0)],
        "C": [("D", 1.0)],
        "D": [],
    }
    alt = GraphAlgoAltShortestPath[str](adj)
    cost, path = alt.find_shortest_path("A", "D")
    assert cost == 4.0
    assert path == ["A", "B", "C", "D"]


def test_contraction_hierarchies() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 5.0)],
        "B": [("C", 2.0), ("D", 4.0)],
        "C": [("D", 1.0)],
        "D": [],
    }
    ch = GraphAlgoContractionHierarchies[str](adj)
    cost, path = ch.query("A", "D")
    assert cost == 4.0
    assert path == ["A", "B", "C", "D"]


def test_hub_labeling() -> None:
    adj = {
        "A": [("B", 1.0)],
        "B": [("C", 2.0)],
        "C": [("D", 3.0)],
        "D": [],
    }
    hl = GraphAlgoHubLabeling[str](adj)
    d = hl.query_distance("A", "D")
    assert d == 6.0


def test_suurballe_disjoint_paths() -> None:
    adj = {
        "S": [("A", 1.0), ("B", 2.0)],
        "A": [("T", 2.0), ("B", 1.0)],
        "B": [("T", 1.0)],
        "T": [],
    }
    suurballe = GraphAlgoSuurballeDisjointPaths[str](adj)
    cost, paths = suurballe.find_disjoint_paths("S", "T")
    assert len(paths) == 2
    assert cost == 6.0


def test_resource_constrained_shortest_path() -> None:
    adj = {
        "A": [("B", 10.0, 5.0), ("C", 20.0, 2.0)],
        "B": [("D", 10.0, 5.0)],
        "C": [("D", 5.0, 2.0)],
        "D": [],
    }
    rcsp = GraphAlgoResourceConstrainedShortestPath[str](adj)
    cost, res, path = rcsp.find_shortest_constrained_path("A", "D", max_resource=6.0)
    assert cost == 25.0
    assert res == 4.0
    assert path == ["A", "C", "D"]


def test_pareto_shortest_path() -> None:
    adj: Dict[str, List[Tuple[str, Tuple[float, float]]]] = {
        "A": [("B", (10.0, 2.0)), ("B", (2.0, 10.0))],
        "B": [("C", (5.0, 5.0))],
        "C": [],
    }
    pareto = GraphAlgoParetoShortestPath[str](adj)
    front = pareto.find_pareto_front("A", "C")
    assert len(front) == 2


def test_widest_bottleneck_path() -> None:
    adj = {
        "A": [("B", 100.0), ("C", 50.0)],
        "B": [("D", 20.0)],
        "C": [("D", 40.0)],
        "D": [],
    }
    widest = GraphAlgoWidestBottleneckPath[str](adj)
    cap, path = widest.find_widest_path("A", "D")
    assert cap == 40.0
    assert path == ["A", "C", "D"]


def test_karp_min_mean_cycle() -> None:
    adj = {
        "A": [("B", 1.0)],
        "B": [("C", 2.0)],
        "C": [("A", 3.0), ("D", 10.0)],
        "D": [],
    }
    karp = GraphAlgoKarpMinMeanCycle[str](adj)
    min_mean, cycle = karp.compute_min_cycle_mean()
    assert min_mean == 2.0
    assert cycle is not None


def test_temporal_csa_path() -> None:
    conns = [
        TemporalConnection("A", "B", 10.0, 20.0, "trip1"),
        TemporalConnection("B", "C", 25.0, 35.0, "trip2"),
        TemporalConnection("A", "C", 5.0, 50.0, "trip3"),
    ]
    csa = GraphAlgoTemporalCsaPath[str](conns)
    arr, itin = csa.earliest_arrival("A", "C", start_time=8.0)
    assert arr == 35.0
    assert len(itin) == 2


def test_raptor_routing() -> None:
    trip1 = TransitTrip("t1", [StopTime("S1", 10.0, 10.0), StopTime("S2", 20.0, 20.0)])
    trip2 = TransitTrip("t2", [StopTime("S2", 25.0, 25.0), StopTime("S3", 35.0, 35.0)])
    r1 = TransitRoute("r1", ["S1", "S2"], [trip1])
    r2 = TransitRoute("r2", ["S2", "S3"], [trip2])
    raptor = GraphAlgoRaptorRouting[str]([r1, r2])
    pareto = raptor.route_query("S1", "S3", departure_time=5.0)
    assert len(pareto) > 0


def test_parallel_bfs() -> None:
    adj = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    p_bfs = GraphAlgoParallelBfs[str](adj)
    distances, levels = p_bfs.traverse_levels("A")
    assert distances["D"] == 2
    assert len(levels) == 3
