"""
Unit tests for Dynamic, Streaming, Temporal, Parallel, and Distributed Graph Processing suite (#201 to #250).
"""

import pytest
from src.features.code_engine.algos.graph.dynamic_streaming_distributed import (
    GraphAlgoDynamicSsspRamalingamReps,
    GraphAlgoIncrementalTopologicalSortPearceKelly,
    GraphAlgoDynamicMinimumSpanningTree,
    GraphAlgoDynamicPagerankResidualPush,
    GraphAlgoIncrementalTriangleCounting,
    GraphAlgoSemiStreamingConnectivityMatching,
    GraphAlgoLinearGraphSketchesAgm,
    GraphAlgoCountMinTcmGraphSketch,
    GraphAlgoDistinctNeighborHyperloglog,
    GraphAlgoReservoirSamplingEdges,
    GraphAlgoSlidingWindowGraph,
    GraphAlgoTemporalReachabilityJourneys,
    GraphAlgoTemporalMotifsCounting,
    GraphAlgoTemporalGraphStorage,
    GraphAlgoMidasSpotlightAnomalyDetection,
    GraphAlgoGatherApplyScatterGas,
    GraphAlgoBlockCentricSubgraphProcessing,
    GraphAlgoAsynchronousGraphProcessing,
    GraphAlgoGpuFrontierAdvanceFilter,
    GraphAlgoGraphblasSemirings,
    GraphAlgoSpmvMaskedSpgemm,
    GraphAlgoFrontierRepresentationSwitching,
    GraphAlgoLigraEdgemapVertexmap,
    GraphAlgoOutOfCoreGraphchiXstream,
    GraphAlgoDistributedBfs2dPartitioning,
    GraphAlgoDistributedTriangleCounting,
    GraphAlgoDistributedConnectedComponentsFastsv,
    GraphAlgoDistributedMstGhs,
    GraphAlgoDistributedSubgraphMatchingWcoj,
    GraphAlgoFactorizedGraphQueryResults,
    GraphAlgoHybridQueryPlansBinaryWcoj,
    GraphAlgoPatternAwareSubgraphEnumeration,
    GraphAlgoSymmetryBreakingSubgraphSearch,
    GraphAlgoColorCodingApproxCounting,
    GraphAlgoColorCodingKPath,
    GraphAlgoGraphSummarizationSwegMdl,
    GraphAlgoVirtualNodeCompression,
    GraphAlgoGraphSpannersBaswanaSen,
    GraphAlgoCutSparsifiersBenczurKarger,
    GraphAlgoAllDistancesSketchesAds,
    GraphAlgoHighDegreeVertexSplitting,
    GraphAlgoEdgeBalancedChunkingMergePath,
    GraphAlgoCheckpointingRecoveryGraphJobs,
    GraphAlgoMultiVersionGraphStorageLlama,
    GraphAlgoGraphTransactionsIsolation,
    GraphAlgoMaterializedViewsQueryCaching,
    GraphAlgoGhostMirrorVerticesSync,
    GraphAlgoIncrementalViewMaintenanceDred,
    GraphAlgoDifferentialDataflowGraphs,
    GraphAlgoApproximateQueryProcessingSampling,
)


def test_dyn_sssp_ramalingam_reps():
    init_adj = {"A": {"B": 2.0, "C": 10.0}, "B": {"C": 3.0}}
    algo = GraphAlgoDynamicSsspRamalingamReps(source="A", initial_adjacency=init_adj)
    assert algo.get_distances()["C"] == 5.0
    res = algo.insert_or_decrease_edge("A", "C", 1.0)
    assert algo.get_distances()["C"] == 1.0
    assert "C" in res.affected_nodes


def test_incremental_topological_sort_pearce_kelly():
    algo = GraphAlgoIncrementalTopologicalSortPearceKelly(["A", "B", "C"])
    res1 = algo.add_edge("A", "B")
    assert res1.added is True
    res2 = algo.add_edge("B", "C")
    assert res2.added is True
    order = algo.get_order()
    assert order["A"] < order["B"] < order["C"]
    res_cycle = algo.add_edge("C", "A")
    assert res_cycle.added is False


def test_dynamic_mst():
    edges = [("A", "B", 1.0), ("B", "C", 2.0), ("A", "C", 5.0)]
    algo = GraphAlgoDynamicMinimumSpanningTree(edges)
    assert algo.get_current_mst().total_weight == 3.0
    algo.insert_or_update_edge("A", "C", 0.5)
    assert algo.get_current_mst().total_weight == 1.5


def test_dynamic_pagerank_residual_push():
    algo = GraphAlgoDynamicPagerankResidualPush(alpha=0.85, epsilon=1e-4)
    algo.add_node("A")
    algo.add_node("B")
    algo.add_node("C")
    algo.add_edge("A", "B")
    algo.add_edge("B", "C")
    algo.add_edge("C", "A")
    ranks = algo.get_scores().scores
    assert len(ranks) == 3


def test_incremental_triangle_counting():
    algo = GraphAlgoIncrementalTriangleCounting()
    algo.add_edge("A", "B")
    algo.add_edge("B", "C")
    counts = algo.get_counts()
    assert counts.total_triangles == 0
    res = algo.add_edge("A", "C")
    assert res.total_triangles == 1
    assert res.delta_triangles == 1


def test_semi_streaming_connectivity_matching():
    algo = GraphAlgoSemiStreamingConnectivityMatching()
    algo.process_edge("A", "B")
    algo.process_edge("C", "D")
    summary = algo.get_summary()
    assert summary.matching_size == 2
    assert len(summary.maximal_matching) == 2


def test_linear_graph_sketches_agm():
    algo = GraphAlgoLinearGraphSketchesAgm(seed=42)
    algo.update_edge("A", "B", 1)
    algo.update_edge("B", "C", 1)
    res = algo.query_connectivity()
    assert res.num_components == 1


def test_count_min_tcm_sketch():
    algo = GraphAlgoCountMinTcmGraphSketch(width=64, depth=4)
    algo.update_edge("A", "B", 5)
    algo.update_edge("A", "C", 3)
    assert algo.estimate_edge_frequency("A", "B") >= 5
    assert algo.estimate_vertex_degree("A") >= 8


def test_distinct_neighbor_hyperloglog():
    algo = GraphAlgoDistinctNeighborHyperloglog(precision=6)
    for i in range(20):
        algo.add_edge("A", f"N_{i}")
    est = algo.estimate_distinct_neighbors("A")
    assert 10.0 <= est <= 30.0


def test_reservoir_sampling_edges():
    algo = GraphAlgoReservoirSamplingEdges(capacity=5, seed=42)
    for i in range(100):
        algo.add_edge(f"U_{i}", f"V_{i}", 1.0)
    sample = algo.get_sample()
    assert len(sample) == 5
    assert algo.estimate_total_stream_size() == 100


def test_sliding_window_graph():
    algo = GraphAlgoSlidingWindowGraph(window_size=10.0, is_time_window=True)
    algo.add_edge("A", "B", timestamp=10.0)
    algo.add_edge("A", "C", timestamp=15.0)
    algo.add_edge("B", "C", timestamp=25.0)
    assert algo.get_degree("A") == 1
    assert len(algo.get_active_edges()) == 2


def test_temporal_reachability_journeys():
    contacts = [("A", "B", 1.0, 1.0), ("B", "C", 3.0, 1.0), ("A", "C", 10.0, 1.0)]
    algo = GraphAlgoTemporalReachabilityJourneys(contacts)
    foremost = algo.compute_foremost_journeys("A", start_time=0.0)
    assert foremost["C"] == 4.0
    fastest = algo.compute_fastest_journey("A", "C")
    assert fastest is not None
    assert fastest["duration"] == 1.0


def test_temporal_motifs_counting():
    edges = [("A", "B", 1.0), ("B", "C", 2.0), ("C", "A", 3.0)]
    algo = GraphAlgoTemporalMotifsCounting(edges, delta=5.0)
    assert algo.count_two_hop_bursts() >= 2
    assert algo.count_temporal_triangles() >= 1


def test_temporal_graph_storage():
    algo = GraphAlgoTemporalGraphStorage()
    algo.add_edge("A", "B", t_start=1.0, t_end=10.0)
    algo.add_edge("A", "C", t_start=5.0, t_end=15.0)
    snap = algo.get_snapshot_at(6.0)
    nbrs = [v for v, _ in snap.get("A", [])]
    assert "B" in nbrs and "C" in nbrs
    snap_late = algo.get_snapshot_at(12.0)
    nbrs_late = [v for v, _ in snap_late.get("A", [])]
    assert "B" not in nbrs_late and "C" in nbrs_late


def test_midas_spotlight_anomaly():
    algo = GraphAlgoMidasSpotlightAnomalyDetection(width=64, depth=3)
    score1 = algo.score_edge("A", "B", 1.0)
    assert score1 > 0.0


def test_gather_apply_scatter_gas():
    adj = {"A": ["B"], "B": ["C"], "C": []}
    init_st = {"A": 1, "B": 0, "C": 0}
    algo = GraphAlgoGatherApplyScatterGas(
        adj,
        init_st,
        gather_fn=lambda u, v, su, sv: sv,
        sum_fn=lambda a, b: max(a if a is not None else 0, b if b is not None else 0),
        apply_fn=lambda u, gsum, state: max(state, gsum if gsum is not None else 0),
    )
    final_st, _ = algo.run_until_convergence(max_steps=5)
    assert final_st["A"] == 1


def test_block_centric_subgraph_processing():
    adj = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    part = {"A": 0, "B": 0, "C": 1, "D": 1}
    algo = GraphAlgoBlockCentricSubgraphProcessing(adj, part)
    dists, _ = algo.compute_block_bfs("A")
    assert dists["D"] == 3


def test_asynchronous_graph_processing():
    adj = {"A": ["B", "C"], "B": ["C"], "C": ["A"]}
    init = {"A": 0.33, "B": 0.33, "C": 0.33}
    algo = GraphAlgoAsynchronousGraphProcessing(adj, init)
    ranks, updates = algo.compute_async_pagerank()
    assert updates > 0
    assert abs(sum(ranks.values()) - 1.0) < 1e-2


def test_gpu_frontier_advance_filter():
    adj = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    algo = GraphAlgoGpuFrontierAdvanceFilter(adj)
    dists = algo.run_bfs("A")
    assert dists["D"] == 2


def test_graphblas_semirings():
    nodes = ["A", "B", "C"]
    edges = [("A", "B", 2.0), ("B", "C", 3.0)]
    algo = GraphAlgoGraphblasSemirings(nodes, edges)
    dists = algo.compute_shortest_paths_tropical("A")
    assert dists["C"] == 5.0


def test_spmv_masked_spgemm():
    algo = GraphAlgoSpmvMaskedSpgemm()
    matrix = {("A", "B"): 2.0, ("B", "C"): 3.0}
    vec = {"B": 1.0}
    y = algo.spmv(matrix, vec)
    assert y["A"] == 2.0

    tri_adj = {("A", "B"): 1.0, ("B", "A"): 1.0, ("B", "C"): 1.0, ("C", "B"): 1.0, ("A", "C"): 1.0, ("C", "A"): 1.0}
    assert algo.count_triangles(tri_adj) == 1


def test_frontier_representation_switching():
    adj = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    algo = GraphAlgoFrontierRepresentationSwitching(adj)
    dists, _ = algo.run_bfs("A")
    assert dists["D"] == 2


def test_ligra_edgemap_vertexmap():
    adj = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    algo = GraphAlgoLigraEdgemapVertexmap(adj)
    dists = algo.compute_bfs("A")
    assert dists["D"] == 2


def test_out_of_core_graphchi():
    edges = [("A", "B", 1.0), ("B", "C", 1.0), ("C", "A", 1.0)]
    algo = GraphAlgoOutOfCoreGraphchiXstream(edges, num_shards=2)
    ranks = algo.compute_pagerank(iterations=5)
    assert len(ranks) == 3


def test_distributed_bfs_2d_partitioning():
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B"), ("B", "C"), ("C", "D")]
    algo = GraphAlgoDistributedBfs2dPartitioning(nodes, edges, grid_dim=2)
    dists = algo.compute_bfs("A")
    assert dists["D"] == 3


def test_distributed_triangle_counting():
    edges = [("A", "B"), ("B", "C"), ("A", "C"), ("C", "D")]
    algo = GraphAlgoDistributedTriangleCounting(edges, num_partitions=2)
    assert algo.count_global_triangles() == 1


def test_distributed_connected_components_fastsv():
    nodes = ["A", "B", "C", "D", "E"]
    edges = [("A", "B"), ("B", "C"), ("D", "E")]
    algo = GraphAlgoDistributedConnectedComponentsFastsv(nodes, edges)
    comps = algo.compute_components()
    assert comps["A"] == comps["C"]
    assert comps["A"] != comps["D"]
    assert algo.get_component_count() == 2


def test_distributed_mst_ghs():
    nodes = ["A", "B", "C"]
    edges = [("A", "B", 1.0), ("B", "C", 2.0), ("A", "C", 3.0)]
    algo = GraphAlgoDistributedMstGhs(nodes, edges)
    mst = algo.compute_mst()
    assert len(mst) == 2
    assert algo.get_mst_weight() == 3.0


def test_distributed_subgraph_matching_wcoj():
    adj = {"A": {"B", "C"}, "B": {"A", "C"}, "C": {"A", "B"}}
    pattern = [("x", "y"), ("y", "z"), ("x", "z")]
    algo = GraphAlgoDistributedSubgraphMatchingWcoj(adj, pattern)
    assert algo.count_matches() == 6


def test_factorized_graph_query_results():
    data = {
        "p1": {"posts": ["post1", "post2"], "tags": ["tag1", "tag2", "tag3"]},
        "p2": {"posts": ["post3"], "tags": ["tag4"]},
    }
    algo = GraphAlgoFactorizedGraphQueryResults(data)
    assert algo.count_tuples() == 7
    flat = algo.materialize_flat()
    assert len(flat) == 7


def test_hybrid_query_plans_binary_wcoj():
    adj = {"A": ["B", "C", "D"], "B": ["A", "C"], "C": ["A", "B"], "D": []}
    algo = GraphAlgoHybridQueryPlansBinaryWcoj(adj)
    res = algo.execute_triangle_with_tail()
    assert len(res) == 1
    assert res[0]["d"] == "D"


def test_pattern_aware_subgraph_enumeration():
    adj = {
        "A": ["B", "C", "D"],
        "B": ["A", "C", "D"],
        "C": ["A", "B", "D"],
        "D": ["A", "B", "C"],
    }
    algo = GraphAlgoPatternAwareSubgraphEnumeration(adj)
    cliques = algo.enumerate_4_cliques()
    assert len(cliques) == 1


def test_symmetry_breaking_subgraph_search():
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    algo = GraphAlgoSymmetryBreakingSubgraphSearch(adj)
    assert len(algo.search_triangles_symmetry_broken()) == 1


def test_color_coding_approx_counting():
    adj = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    algo = GraphAlgoColorCodingApproxCounting(adj, k=4, num_trials=20, seed=42)
    est, _ = algo.estimate_k_path_count()
    assert est >= 0.0


def test_color_coding_k_path():
    adj = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    algo = GraphAlgoColorCodingKPath(adj, k=4, trials=50, seed=42)
    assert algo.has_simple_k_path() is True
    path = algo.find_simple_k_path()
    assert path == ["A", "B", "C", "D"]


def test_graph_summarization_sweg_mdl():
    adj = {"A": ["X", "Y"], "B": ["X", "Y"], "X": ["A", "B"], "Y": ["A", "B"]}
    algo = GraphAlgoGraphSummarizationSwegMdl(adj, similarity_threshold=0.8)
    summary = algo.compute_summary()
    assert len(summary["supernodes"]) >= 1


def test_virtual_node_compression():
    adj = {"A": ["X", "Y"], "B": ["X", "Y"], "X": [], "Y": []}
    algo = GraphAlgoVirtualNodeCompression(adj, min_biclique_size=4)
    comp_adj, v_nodes, savings = algo.compress()
    assert len(v_nodes) == 1
    assert savings == 0


def test_graph_spanners_baswana_sen():
    nodes = ["A", "B", "C"]
    edges = [("A", "B", 1.0), ("B", "C", 1.0), ("A", "C", 10.0)]
    algo = GraphAlgoGraphSpannersBaswanaSen(nodes, edges, k=2)
    spanner = algo.compute_greedy_spanner()
    assert len(spanner) == 2


def test_cut_sparsifiers_benczur_karger():
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B", 1.0), ("B", "C", 1.0), ("C", "D", 1.0), ("A", "D", 1.0)]
    algo = GraphAlgoCutSparsifiersBenczurKarger(nodes, edges, epsilon=0.5, seed=42)
    sparsified = algo.compute_sparsifier()
    assert len(sparsified) > 0


def test_all_distances_sketches_ads():
    nodes = ["A", "B", "C"]
    edges = [("A", "B", 1.0), ("B", "C", 2.0)]
    algo = GraphAlgoAllDistancesSketchesAds(nodes, edges, k=2, seed=42)
    sketches = algo.build_sketches()
    assert "A" in sketches
    assert algo.estimate_neighborhood_size("A", max_dist=10.0) >= 1.0


def test_high_degree_vertex_splitting():
    adj = {"Hub": ["A", "B", "C", "D", "E"], "A": [], "B": [], "C": [], "D": [], "E": []}
    algo = GraphAlgoHighDegreeVertexSplitting(adj, max_degree_threshold=2)
    hubs = algo.get_hub_nodes()
    assert hubs == ["Hub"]
    new_adj, hub_map = algo.split_graph()
    assert "Hub" in hub_map
    assert len(hub_map["Hub"]) == 3


def test_edge_balanced_chunking():
    adj = {"A": ["1", "2"], "B": ["3", "4", "5", "6"], "C": ["7"]}
    algo = GraphAlgoEdgeBalancedChunkingMergePath(adj, num_workers=2)
    chunks = algo.compute_edge_balanced_chunks()
    assert len(chunks) == 2
    assert algo.get_imbalance_ratio() >= 1.0


def test_checkpointing_recovery_graph_jobs():
    algo = GraphAlgoCheckpointingRecoveryGraphJobs(num_partitions=2, checkpoint_interval=5)
    st = {0: {"A": 1.0}, 1: {"B": 2.0}}
    fr = {0: ["A"], 1: ["B"]}
    algo.save_checkpoint(5, st, fr)
    assert algo.get_latest_checkpoint_step() == 5
    rec = algo.recover_partition(0)
    assert rec is not None
    assert rec["states"] == {"A": 1.0}


def test_multi_version_graph_storage_llama():
    algo = GraphAlgoMultiVersionGraphStorageLlama()
    v1 = algo.create_version_snapshot()
    algo.add_edge("A", "B", 1.0)
    v2 = algo.create_version_snapshot()
    algo.add_edge("A", "C", 2.0)
    algo.remove_edge("A", "B")

    nbrs_v1 = [v for v, _ in algo.get_neighbors_at_version("A", v1)]
    assert "B" in nbrs_v1 and "C" not in nbrs_v1

    nbrs_v2 = [v for v, _ in algo.get_neighbors_at_version("A", v2)]
    assert "B" not in nbrs_v2 and "C" in nbrs_v2


def test_graph_transactions_isolation():
    algo = GraphAlgoGraphTransactionsIsolation()
    t1 = algo.begin_transaction()
    algo.write_edge(t1, "A", "B", 5.0)
    assert algo.commit_transaction(t1) is True

    t2 = algo.begin_transaction()
    algo.write_edge(t2, "A", "B", 10.0)
    assert algo.commit_transaction(t2) is True


def test_materialized_views_query_caching():
    cache = GraphAlgoMaterializedViewsQueryCaching(max_cache_size=100)
    key = cache.make_cache_key("two_hop", {"node": "A"})
    computed = False

    def comp():
        nonlocal computed
        computed = True
        return ["B", "C"]

    val1 = cache.get_or_compute(key, comp, touched_nodes=["A"])
    assert val1 == ["B", "C"]
    assert computed is True

    computed = False
    val2 = cache.get_or_compute(key, comp, touched_nodes=["A"])
    assert val2 == ["B", "C"]
    assert computed is False

    assert cache.invalidate_nodes(["A"]) == 1
    assert cache.get_stats()["cached_entries"] == 0


def test_ghost_mirror_vertices_sync():
    algo = GraphAlgoGhostMirrorVerticesSync(partition_id=0, master_assignments={"M1": 0, "G1": 1})
    algo.register_local_node("M1", initial_val=10)
    algo.register_local_node("G1", initial_val=0)

    gather_msgs = algo.prepare_mirror_gather_messages({"G1": 5.0})
    assert 1 in gather_msgs
    assert gather_msgs[1]["G1"] == 5.0

    algo.apply_broadcast_updates({"G1": 42})
    assert algo.get_local_state("G1") == 42


def test_incremental_view_maintenance_dred():
    algo = GraphAlgoIncrementalViewMaintenanceDred()
    derived = algo.add_edge("A", "B")
    derived2 = algo.add_edge("B", "C")
    assert ("A", "C") in derived2
    assert algo.is_two_hop_connected("A", "C") is True
    expired = algo.remove_edge("B", "C")
    assert ("A", "C") in expired
    assert algo.is_two_hop_connected("A", "C") is False


def test_differential_dataflow_graphs():
    algo = GraphAlgoDifferentialDataflowGraphs()
    algo.update_edge("A", "B", time=1, diff=1)
    algo.update_edge("B", "C", time=1, diff=1)
    reach = algo.compute_incremental_reachability()
    assert ("A", "C") in reach


def test_approximate_query_processing_sampling():
    nodes = [f"N_{i}" for i in range(100)]
    adj = {f"N_{i}": [f"N_{(i+1)%100}", f"N_{(i+2)%100}"] for i in range(100)}
    algo = GraphAlgoApproximateQueryProcessingSampling(nodes, adj, sample_ratio=0.3, seed=42)
    mean_d, ci_l, ci_u = algo.estimate_average_degree()
    assert 1.0 <= mean_d <= 3.0
    assert ci_l <= mean_d <= ci_u
