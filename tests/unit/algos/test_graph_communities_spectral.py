"""
Unit tests for Graph Communities, Spectral Methods, Coloring, Isomorphism & Decompositions (#151–200).
"""

import pytest
from src.features.code_engine.algos.graph.communities_spectral_decompositions import (
    GraphAlgoModularityResolution,
    GraphAlgoLeidenCpm,
    GraphAlgoGirvanNewmanCommunities,
    GraphAlgoSlpaOverlappingCommunities,
    GraphAlgoInfomapFlow,
    GraphAlgoWalktrapCommunities,
    GraphAlgoFastGreedyModularity,
    GraphAlgoSpectralClustering,
    GraphAlgoMarkovClusteringMcl,
    GraphAlgoSbmInference,
    GraphAlgoLocalPprClustering,
    GraphAlgoLocalMaxFlowClustering,
    GraphAlgoCorePeripheryBorgatti,
    GraphAlgoBipartiteCommunityProjection,
    GraphAlgoHypergraphCliqueExpansion,
    GraphAlgoConductanceExpansion,
    GraphAlgoExternalInternalRatio,
    GraphAlgoNmiAmiPartitionAgreement,
    GraphAlgoKlPartitioning,
    GraphAlgoMultilevelGraphPartitioning,
    GraphAlgoStreamingVertexPartitioning,
    GraphAlgoLaplacianEigensolvers,
    GraphAlgoSpectralSparsification,
    GraphAlgoLaplacianLinearSolvers,
    GraphAlgoEffectiveResistanceDistance,
    GraphAlgoWilsonRandomSpanningTree,
    GraphAlgoGraphSignalProcessing,
    GraphAlgoGreedyVertexColoring,
    GraphAlgoFractionalChromaticNumber,
    GraphAlgoMaximumIndependentSet,
    GraphAlgoWeisfeilerLehmanIsomorphism,
    GraphAlgoUllmannSubgraphIsomorphism,
    GraphAlgoVf2SubgraphIsomorphism,
    GraphAlgoMcsCommonSubgraph,
    GraphAlgoGraphEditDistance,
    GraphAlgoPlanarityHopcroftTarjan,
    GraphAlgoTreewidthMinDegree,
    GraphAlgoChordalGraphRecognition,
    GraphAlgoCliqueTreeJunctionTree,
    GraphAlgoNestedDissection,
    GraphAlgoBiconnectedComponentsHopcroft,
    GraphAlgoTriconnectedComponentsSpqr,
    GraphAlgoModularDecomposition,
    GraphAlgoSplitDecomposition,
    GraphAlgoCographRecognition,
    GraphAlgoIntervalGraphRecognition,
    GraphAlgoComparabilityGraphTransitivity,
    GraphAlgoPermutationGraphInversion,
    GraphAlgoThresholdGraphPeeling,
    GraphAlgoDistanceHereditaryGraphs,
)


@pytest.fixture
def barbell_graph():
    # Two K4 cliques connected by a bridge edge (3, 4)
    adj = {
        0: [1, 2, 3], 1: [0, 2, 3], 2: [0, 1, 3], 3: [0, 1, 2, 4],
        4: [3, 5, 6, 7], 5: [4, 6, 7], 6: [4, 5, 7], 7: [4, 5, 6]
    }
    return adj


@pytest.fixture
def cycle5_graph():
    return {0: [1, 4], 1: [0, 2], 2: [1, 3], 3: [2, 4], 4: [3, 0]}


@pytest.fixture
def bipartite_graph():
    return {
        "u1": ["v1", "v2"], "u2": ["v1", "v2"], "u3": ["v3", "v4"], "u4": ["v3", "v4"],
        "v1": ["u1", "u2"], "v2": ["u1", "u2"], "v3": ["u3", "u4"], "v4": ["u3", "u4"]
    }


def test_modularity_resolution(barbell_graph):
    partition = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1}
    evaluator = GraphAlgoModularityResolution(barbell_graph, partition, gamma=1.0)
    q, internal_e, comm_deg = evaluator.evaluate_modularity()
    assert q > 0.0
    assert len(internal_e) == 2


def test_leiden_cpm(barbell_graph):
    detector = GraphAlgoLeidenCpm(barbell_graph, gamma=0.2)
    part, quality, num_c = detector.detect_communities()
    assert len(part) == 8
    assert num_c >= 1


def test_girvan_newman(barbell_graph):
    detector = GraphAlgoGirvanNewmanCommunities(barbell_graph, target_components=2)
    part, max_q, dendro = detector.find_communities()
    assert len(part) == 8


def test_slpa_overlapping(barbell_graph):
    detector = GraphAlgoSlpaOverlappingCommunities(barbell_graph, num_rounds_t=15, retention_threshold_r=0.3, rng_seed=42)
    node_to_labels, comm_to_members, num_comm = detector.detect_overlapping_communities()
    assert len(node_to_labels) == 8


def test_infomap_flow(barbell_graph):
    detector = GraphAlgoInfomapFlow(barbell_graph, max_iter=10, rng_seed=42)
    part, code_length, count = detector.detect_modules()
    assert len(part) == 8


def test_walktrap_communities(barbell_graph):
    detector = GraphAlgoWalktrapCommunities(barbell_graph, t_steps=3)
    part, modularity, count = detector.detect_communities()
    assert len(part) == 8


def test_fast_greedy_modularity(barbell_graph):
    detector = GraphAlgoFastGreedyModularity(barbell_graph)
    part, best_q, dendro = detector.detect_communities()
    assert len(part) == 8


def test_spectral_clustering(barbell_graph):
    clusterer = GraphAlgoSpectralClustering(barbell_graph, k_clusters=2, rng_seed=42)
    part, e_vecs, fiedler = clusterer.cluster()
    assert len(part) == 8


def test_markov_clustering(barbell_graph):
    mcl = GraphAlgoMarkovClusteringMcl(barbell_graph, inflation_r=2.0, expansion_power=2)
    part, num_c, matrix = mcl.cluster()
    assert len(part) == 8


def test_sbm_inference(barbell_graph):
    sbm = GraphAlgoSbmInference(barbell_graph, num_blocks_k=2, max_iter=15, rng_seed=42)
    part, matrix, log_likelihood = sbm.infer_sbm()
    assert len(part) == 8


def test_local_ppr_clustering(barbell_graph):
    clusterer = GraphAlgoLocalPprClustering(barbell_graph, alpha=0.15, epsilon=1e-3)
    cluster, conductance, volume = clusterer.extract_local_cluster(0)
    assert 0 in cluster


def test_local_max_flow_clustering(barbell_graph):
    clusterer = GraphAlgoLocalMaxFlowClustering(barbell_graph, seed_nodes=[0, 1])
    cluster, min_cut, size = clusterer.extract_community()
    assert 0 in cluster


def test_core_periphery(barbell_graph):
    detector = GraphAlgoCorePeripheryBorgatti(barbell_graph)
    core, periph, corr = detector.detect_core_periphery()
    assert len(core) + len(periph) == 8


def test_bipartite_communities(bipartite_graph):
    detector = GraphAlgoBipartiteCommunityProjection()
    u_set = ["u1", "u2", "u3", "u4"]
    v_set = ["v1", "v2", "v3", "v4"]
    res = detector.detect(bipartite_graph, u_set, v_set)
    assert res.num_communities >= 2


def test_hypergraph_projection():
    projector = GraphAlgoHypergraphCliqueExpansion()
    hyperedges = [[1, 2, 3], [3, 4, 5]]
    res_clique = projector.clique_expansion(hyperedges)
    assert res_clique.node_count == 5
    assert res_clique.edge_count > 0

    res_star = projector.star_expansion(hyperedges)
    assert res_star.node_count == 7


def test_conductance(barbell_graph):
    evaluator = GraphAlgoConductanceExpansion()
    profile = evaluator.evaluate(barbell_graph, subset=[0, 1, 2, 3])
    assert profile.conductance > 0.0
    assert profile.cut_weight == 1.0


def test_external_internal_ratio(barbell_graph):
    evaluator = GraphAlgoExternalInternalRatio()
    partition = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1}
    res = evaluator.evaluate(barbell_graph, partition)
    assert res.total_internal_edges == 12
    assert res.total_external_edges == 1


def test_partition_agreement():
    evaluator = GraphAlgoNmiAmiPartitionAgreement()
    p1 = {0: 0, 1: 0, 2: 1, 3: 1}
    p2 = {0: 0, 1: 0, 2: 1, 3: 1}
    res = evaluator.evaluate(p1, p2)
    assert pytest.approx(res.nmi, 1e-4) == 1.0
    assert pytest.approx(res.ari, 1e-4) == 1.0


def test_kl_partitioning(barbell_graph):
    bisector = GraphAlgoKlPartitioning(max_passes=5)
    res = bisector.partition(barbell_graph)
    assert len(res.partition_a) == 4
    assert len(res.partition_b) == 4
    assert res.cut_size <= 2.0


def test_multilevel_partitioning(barbell_graph):
    partitioner = GraphAlgoMultilevelGraphPartitioning(num_partitions=2)
    res = partitioner.partition(barbell_graph)
    assert res.num_partitions == 2
    assert len(res.partition) == 8


def test_streaming_partitioning():
    partitioner = GraphAlgoStreamingVertexPartitioning(num_partitions=2, total_nodes_estimate=6)
    stream = [
        (0, [1, 2]),
        (1, [0, 2]),
        (2, [0, 1, 3]),
        (3, [2, 4, 5]),
        (4, [3, 5]),
        (5, [3, 4]),
    ]
    res = partitioner.partition_stream(stream)
    assert len(res.assignments) == 6


def test_laplacian_eigensolver(barbell_graph):
    solver = GraphAlgoLaplacianEigensolvers(num_iterations=15)
    res = solver.solve(barbell_graph)
    assert res.algebraic_connectivity > 0.0
    assert res.is_connected is True


def test_spectral_sparsifier(barbell_graph):
    sparsifier = GraphAlgoSpectralSparsification(epsilon=0.5)
    res = sparsifier.sparsify(barbell_graph)
    assert res.sparsified_edge_count > 0


def test_laplacian_linear_solver(barbell_graph):
    solver = GraphAlgoLaplacianLinearSolvers(max_iterations=50)
    rhs = {0: 1.0, 7: -1.0}
    res = solver.solve(barbell_graph, rhs)
    assert len(res.solution) == 8
    assert res.solution[0] > res.solution[7]


def test_effective_resistance(barbell_graph):
    calc = GraphAlgoEffectiveResistanceDistance()
    res = calc.compute(barbell_graph, pairs=[(0, 7), (0, 1)])
    assert (0, 7) in res.resistances
    assert res.resistances[(0, 7)] > res.resistances[(0, 1)]


def test_wilson_spanning_tree(barbell_graph):
    wilson = GraphAlgoWilsonRandomSpanningTree(seed=42)
    res = wilson.sample(barbell_graph)
    assert res.tree_size == 7
    assert res.num_components == 1


def test_graph_signal_processing(barbell_graph):
    gsp = GraphAlgoGraphSignalProcessing()
    signal = {u: 1.0 if u < 4 else -1.0 for u in range(8)}
    res = gsp.chebyshev_filter(barbell_graph, signal, filter_coeffs=[0.5, 0.5])
    assert len(res.filtered_signal) == 8


def test_vertex_coloring(barbell_graph):
    coloring = GraphAlgoGreedyVertexColoring()
    res = coloring.color(barbell_graph, strategy="dsatur")
    assert res.is_valid is True
    assert res.chromatic_number <= 5


def test_fractional_chromatic_number(cycle5_graph):
    solver = GraphAlgoFractionalChromaticNumber(max_mis_samples=20)
    res = solver.solve(cycle5_graph)
    assert res.fractional_chromatic_number >= 2.0


def test_maximum_independent_set(barbell_graph):
    solver = GraphAlgoMaximumIndependentSet()
    res = solver.solve(barbell_graph)
    assert res.independence_number == 2
    assert res.vertex_cover_number == 6
    assert res.independence_number + res.vertex_cover_number == 8


def test_weisfeiler_lehman(cycle5_graph):
    wl = GraphAlgoWeisfeilerLehmanIsomorphism()
    res = wl.hash_graph(cycle5_graph)
    assert len(res.canonical_hash) == 64
    assert wl.are_isomorphic(cycle5_graph, cycle5_graph) is True


def test_ullmann_subgraph():
    matcher = GraphAlgoUllmannSubgraphIsomorphism()
    target = {0: [1, 2], 1: [0, 2], 2: [0, 1, 3], 3: [2]}
    pattern = {10: [20, 30], 20: [10, 30], 30: [10, 20]}
    res = matcher.find_matches(pattern, target)
    assert res.is_subgraph is True
    assert res.match_count >= 1


def test_vf2_subgraph():
    matcher = GraphAlgoVf2SubgraphIsomorphism(subgraph_mode=True)
    target = {0: [1, 2], 1: [0, 2], 2: [0, 1, 3], 3: [2]}
    pattern = {10: [20, 30], 20: [10, 30], 30: [10, 20]}
    res = matcher.match(pattern, target)
    assert res.is_isomorphic is True


def test_mcs_common_subgraph():
    mcs = GraphAlgoMcsCommonSubgraph()
    g1 = {0: [1, 2], 1: [0, 2], 2: [0, 1, 3], 3: [2]}
    g2 = {10: [20, 30], 20: [10, 30], 30: [10, 20], 40: []}
    res = mcs.solve(g1, g2)
    assert res.common_vertex_count >= 3


def test_graph_edit_distance():
    ged = GraphAlgoGraphEditDistance(beam_width=50)
    g1 = {0: [1], 1: [0]}
    g2 = {0: [1], 1: [0]}
    res = ged.compute_distance(g1, g2)
    assert res.edit_distance == 0.0


def test_planarity(barbell_graph):
    planarity = GraphAlgoPlanarityHopcroftTarjan()
    res = planarity.test_planarity(barbell_graph)
    assert res.is_planar is True


def test_treewidth(barbell_graph):
    solver = GraphAlgoTreewidthMinDegree()
    res = solver.decompose(barbell_graph, heuristic="min_fill")
    assert res.treewidth_upper_bound >= 3


def test_chordal_graph(barbell_graph):
    recognizer = GraphAlgoChordalGraphRecognition()
    res = recognizer.recognize(barbell_graph)
    assert res.is_chordal is True
    assert len(res.perfect_elimination_ordering) == 8


def test_junction_tree(barbell_graph):
    builder = GraphAlgoCliqueTreeJunctionTree()
    res = builder.build(barbell_graph)
    assert res.num_cliques >= 2


def test_nested_dissection(barbell_graph):
    orderer = GraphAlgoNestedDissection()
    res = orderer.order(barbell_graph)
    assert len(res.ordering) == 8


def test_biconnected_components(barbell_graph):
    bcc = GraphAlgoBiconnectedComponentsHopcroft()
    res = bcc.decompose(barbell_graph)
    assert 3 in res.articulation_points or 4 in res.articulation_points
    assert res.num_blocks >= 2


def test_spqr_tree(cycle5_graph):
    spqr = GraphAlgoTriconnectedComponentsSpqr()
    res = spqr.decompose(cycle5_graph)
    assert len(res.spqr_nodes) >= 1


def test_modular_decomposition(barbell_graph):
    modular = GraphAlgoModularDecomposition()
    res = modular.decompose(barbell_graph)
    assert res.root_id in res.nodes


def test_split_decomposition(barbell_graph):
    splitter = GraphAlgoSplitDecomposition()
    res = splitter.decompose(barbell_graph)
    assert isinstance(res.has_splits, bool)


def test_cograph_recognition(barbell_graph):
    recognizer = GraphAlgoCographRecognition()
    res = recognizer.recognize(barbell_graph)
    assert isinstance(res.is_cograph, bool)


def test_interval_graph(barbell_graph):
    recognizer = GraphAlgoIntervalGraphRecognition()
    res = recognizer.recognize(barbell_graph)
    assert isinstance(res.is_interval_graph, bool)


def test_comparability_graph(barbell_graph):
    recognizer = GraphAlgoComparabilityGraphTransitivity()
    res = recognizer.recognize(barbell_graph)
    assert isinstance(res.is_comparability_graph, bool)


def test_permutation_graph():
    recognizer = GraphAlgoPermutationGraphInversion()
    g = {0: [1], 1: [0, 2], 2: [1]}
    res = recognizer.recognize(g)
    assert isinstance(res.is_permutation_graph, bool)


def test_threshold_graph():
    recognizer = GraphAlgoThresholdGraphPeeling()
    star = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}
    res = recognizer.recognize(star)
    assert res.is_threshold_graph is True


def test_distance_hereditary(cycle5_graph):
    recognizer = GraphAlgoDistanceHereditaryGraphs()
    res = recognizer.recognize(cycle5_graph)
    assert res.is_distance_hereditary is False
