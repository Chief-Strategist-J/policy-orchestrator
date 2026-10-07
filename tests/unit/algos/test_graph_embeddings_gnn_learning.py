"""Unit tests for Graph Embeddings, Advanced GNNs, PGMs, Causal Graphs & Graph-Based Learning Suite (#251-300)."""

import pytest

from src.features.code_engine.algos.graph.embeddings_gnn_learning import (
    GraphAlgoAdjacencySpectralEmbedding,
    GraphAlgoAndersenPointsToAnalysis,
    GraphAlgoAppnpPersonalizedPropagation,
    GraphAlgoBayesianNetworkStructureLearning,
    GraphAlgoBeliefPropagationTree,
    GraphAlgoCflDyckReachability,
    GraphAlgoConditionalRandomFieldsCrf,
    GraphAlgoConstraintCausalDiscoveryPcFci,
    GraphAlgoDoCalculusBackdoorFrontdoor,
    GraphAlgoDSeparationBayesBall,
    GraphAlgoEquivariantGeometricGnn,
    GraphAlgoFactorGraphsMessagePassing,
    GraphAlgoGibbsSamplingPgm,
    GraphAlgoGinIsomorphismNetwork,
    GraphAlgoGrarepMultihopEmbedding,
    GraphAlgoGraphAutoencoderGae,
    GraphAlgoGraphicalLassoPrecision,
    GraphAlgoGraphmaeMaskedPretraining,
    GraphAlgoGromovWassersteinMatching,
    GraphAlgoHarmonicLabelPropagation,
    GraphAlgoHeterophilyH2gcnGprgnn,
    GraphAlgoHetesimMetapathRelevance,
    GraphAlgoHigherOrderSubgraphGnn,
    GraphAlgoHopeDirectedEmbedding,
    GraphAlgoIfdsIdeDataflowAnalysis,
    GraphAlgoIsorankSpectralAlignment,
    GraphAlgoJunctionTreeInference,
    GraphAlgoLayerwiseNeighborSampling,
    GraphAlgoLineProximityEmbedding,
    GraphAlgoLoopyBeliefPropagation,
    GraphAlgoMaxProductViterbiDecoding,
    GraphAlgoMeanFieldVariationalInference,
    GraphAlgoNavigabilityKleinbergRouting,
    GraphAlgoNetmfMatrixFactorization,
    GraphAlgoNnDescentKnnGraph,
    GraphAlgoP3alphaRp3betaRecommenders,
    GraphAlgoPartitionedBiggraphEmbedding,
    GraphAlgoPathRankingAlgorithmPra,
    GraphAlgoPathsimMetapathSimilarity,
    GraphAlgoPixieRandomWalkRecommendation,
    GraphAlgoPositionalStructuralEncodings,
    GraphAlgoProneSpectralPropagation,
    GraphAlgoProximityGraphAnnRng,
    GraphAlgoRegalEmbeddingAlignment,
    GraphAlgoSgcSimplifiedConvolution,
    GraphAlgoSimilarityGraphConstruction,
    GraphAlgoSteensgaardPointsToAnalysis,
    GraphAlgoStruc2vecRoleEmbedding,
    GraphAlgoTextrankKeywordSentenceRanking,
    GraphAlgoVariableEliminationPgm,
)


def test_ase_embedding():
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B", "D"], "D": ["C"]}
    algo = GraphAlgoAdjacencySpectralEmbedding(adj, dim=2)
    res = algo.compute_embeddings()
    assert len(res) == 4


def test_line_embedding():
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    algo = GraphAlgoLineProximityEmbedding(adj, dim=4)
    res = algo.train_embeddings(epochs=5)
    assert len(res) == 3


def test_struc2vec():
    adj = {"A": ["B", "C"], "B": ["A"], "C": ["A"], "D": ["E"], "E": ["D"]}
    algo = GraphAlgoStruc2vecRoleEmbedding(adj, dim=4)
    res = algo.compute_embeddings()
    assert len(res) == 5


def test_hope_embedding():
    adj = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    algo = GraphAlgoHopeDirectedEmbedding(adj, dim=2)
    s_emb, t_emb = algo.compute_embeddings()
    assert len(s_emb) == 4
    assert len(t_emb) == 4


def test_grarep_embedding():
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    algo = GraphAlgoGrarepMultihopEmbedding(adj, dim_per_step=2, k_steps=2)
    res = algo.compute_embeddings()
    assert len(res) == 3


def test_netmf_embedding():
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    algo = GraphAlgoNetmfMatrixFactorization(adj, dim=2, window_size=2)
    res = algo.compute_embeddings()
    assert len(res) == 3


def test_prone_embedding():
    adj = {"A": ["B", "C"], "B": ["A"], "C": ["A"]}
    algo = GraphAlgoProneSpectralPropagation(adj, dim=2)
    res = algo.compute_embeddings()
    assert len(res) == 3


def test_biggraph_partitioned():
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")]
    algo = GraphAlgoPartitionedBiggraphEmbedding(nodes=nodes, edges=edges, num_partitions=2, dim=4)
    res = algo.train_epoch()
    assert len(res) == 4


def test_gae():
    adj = {"A": ["B", "C"], "B": ["A"], "C": ["A"]}
    feats = {"A": [1.0, 0.0], "B": [0.0, 1.0], "C": [1.0, 1.0]}
    algo = GraphAlgoGraphAutoencoderGae(adj, feats, latent_dim=2)
    res = algo.encode()
    assert len(res) == 3


def test_gin():
    adj = {"A": ["B"], "B": ["A"]}
    feats = {"A": [1.0, 2.0], "B": [2.0, 1.0]}
    algo = GraphAlgoGinIsomorphismNetwork(adj, feats, num_layers=2)
    node_emb = algo.compute_node_embeddings()
    g_rep = algo.compute_graph_readout()
    assert len(node_emb) == 2
    assert len(g_rep) > 0


def test_appnp():
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    logits = {"A": [2.0, 0.5], "B": [0.1, 1.8], "C": [0.2, 2.1]}
    algo = GraphAlgoAppnpPersonalizedPropagation(adj, logits, k_steps=5, alpha=0.1)
    res = algo.propagate()
    assert len(res) == 3


def test_sgc():
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    feats = {"A": [1.0, 0.0], "B": [0.0, 1.0], "C": [1.0, 1.0]}
    algo = GraphAlgoSgcSimplifiedConvolution(adj, feats, k_hops=2)
    res = algo.smooth_features()
    assert len(res) == 3


def test_h2gcn():
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    feats = {"A": [1.0], "B": [2.0], "C": [3.0]}
    algo = GraphAlgoHeterophilyH2gcnGprgnn(adj, feats)
    res = algo.forward_h2gcn()
    assert len(res) == 3


def test_lap_pe():
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    algo = GraphAlgoPositionalStructuralEncodings(adj, k_lap_dim=2, k_rw_steps=3)
    lap = algo.compute_lappe()
    rw = algo.compute_rwse()
    assert len(lap) == 3
    assert len(rw) == 3


def test_subgraph_gnn():
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    algo = GraphAlgoHigherOrderSubgraphGnn(adj, policy="node_deleted")
    g_pool = algo.compute_subgraph_bag_embedding()
    assert len(g_pool) > 0


def test_egnn():
    adj = {"A": ["B"], "B": ["A"]}
    h = {"A": [1.0], "B": [0.0]}
    x = {"A": [0.0, 0.0, 0.0], "B": [1.0, 0.0, 0.0]}
    algo = GraphAlgoEquivariantGeometricGnn(adj, coordinates=x, features=h)
    new_h, new_x = algo.forward_layer()
    assert len(new_h) == 2
    assert len(new_x) == 2


def test_graphmae():
    adj = {"A": ["B", "C"], "B": ["A"], "C": ["A"]}
    feats = {"A": [1.0, 0.0], "B": [0.0, 1.0], "C": [1.0, 1.0]}
    algo = GraphAlgoGraphmaeMaskedPretraining[str]()
    res = algo.evaluate(adj, feats, mask_rate=0.3, epochs=5)
    assert len(res["embeddings"]) == 3


def test_layerwise_sampling():
    adj = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C"]}
    algo = GraphAlgoLayerwiseNeighborSampling[str]()
    res = algo.evaluate(adj, target_nodes=["A"], layer_sample_sizes=[2, 2], method="ladies")
    assert len(res["layer_nodes"]) == 3


def test_belief_prop_tree():
    adj = {"A": ["B", "C"], "B": ["A"], "C": ["A"]}
    node_pots = {"A": [0.8, 0.2], "B": [0.5, 0.5], "C": [0.5, 0.5]}
    edge_pots = {
        ("A", "B"): [[0.9, 0.1], [0.1, 0.9]],
        ("A", "C"): [[0.9, 0.1], [0.1, 0.9]],
    }
    algo = GraphAlgoBeliefPropagationTree[str]()
    res = algo.evaluate(adj, node_pots, edge_pots)
    assert len(res["marginals"]) == 3
    assert pytest.approx(sum(res["marginals"]["A"]), 1e-4) == 1.0


def test_loopy_bp():
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    node_pots = {"A": [0.6, 0.4], "B": [0.5, 0.5], "C": [0.5, 0.5]}
    edge_pots = {
        ("A", "B"): [[0.8, 0.2], [0.2, 0.8]],
        ("B", "C"): [[0.8, 0.2], [0.2, 0.8]],
        ("A", "C"): [[0.8, 0.2], [0.2, 0.8]],
    }
    algo = GraphAlgoLoopyBeliefPropagation[str]()
    res = algo.evaluate(adj, node_pots, edge_pots, max_iterations=20)
    assert len(res["marginals"]) == 3


def test_max_product_viterbi():
    adj = {"A": ["B"], "B": ["A"]}
    node_pots = {"A": [0.9, 0.1], "B": [0.5, 0.5]}
    edge_pots = {("A", "B"): [[0.9, 0.1], [0.1, 0.9]]}
    algo = GraphAlgoMaxProductViterbiDecoding[str]()
    res = algo.evaluate(adj, node_pots, edge_pots)
    assert res["map_configuration"]["A"] == 0
    assert res["map_configuration"]["B"] == 0


def test_junction_tree():
    variables = ["A", "B", "C"]
    cards = {"A": 2, "B": 2, "C": 2}
    factors = [
        {"scope": ["A", "B"], "table": {(0, 0): 0.8, (0, 1): 0.2, (1, 0): 0.1, (1, 1): 0.9}},
        {"scope": ["B", "C"], "table": {(0, 0): 0.7, (0, 1): 0.3, (1, 0): 0.2, (1, 1): 0.8}},
    ]
    algo = GraphAlgoJunctionTreeInference[str]()
    res = algo.evaluate(variables, cards, factors)
    assert len(res["marginals"]) == 3


def test_variable_elimination():
    factors = [
        {"scope": ["A", "B"], "table": {(0, 0): 0.8, (0, 1): 0.2, (1, 0): 0.1, (1, 1): 0.9}},
        {"scope": ["B", "C"], "table": {(0, 0): 0.7, (0, 1): 0.3, (1, 0): 0.2, (1, 1): 0.8}},
    ]
    algo = GraphAlgoVariableEliminationPgm[str]()
    res = algo.evaluate(query_variables=["C"], evidence={"A": 0}, factors=factors)
    assert len(res["posterior"]) > 0


def test_gibbs_sampling():
    variables = ["A", "B"]
    cards = {"A": 2, "B": 2}
    factors = [
        {"scope": ["A", "B"], "table": {(0, 0): 0.9, (0, 1): 0.1, (1, 0): 0.1, (1, 1): 0.9}}
    ]
    algo = GraphAlgoGibbsSamplingPgm[str]()
    res = algo.evaluate(variables, cards, factors, num_samples=100, burn_in=20)
    assert len(res["marginals"]) == 2


def test_mean_field():
    variables = ["A", "B"]
    cards = {"A": 2, "B": 2}
    factors = [
        {"scope": ["A", "B"], "table": {(0, 0): 0.9, (0, 1): 0.1, (1, 0): 0.1, (1, 1): 0.9}}
    ]
    algo = GraphAlgoMeanFieldVariationalInference[str]()
    res = algo.evaluate(variables, cards, factors, max_iterations=20)
    assert len(res["variational_marginals"]) == 2


def test_crf():
    emissions = [[1.0, 0.0], [0.0, 10.0], [1.0, 0.0]]
    trans = [[0.8, 0.2], [0.2, 0.8]]
    algo = GraphAlgoConditionalRandomFieldsCrf[str]()
    res = algo.evaluate(emissions, trans)
    assert res["viterbi_path"] == [0, 1, 0]


def test_factor_graphs():
    variables = ["A", "B"]
    cards = {"A": 2, "B": 2}
    factors = [
        {"name": "f1", "scope": ["A", "B"], "table": {(0, 0): 0.9, (0, 1): 0.1, (1, 0): 0.1, (1, 1): 0.9}}
    ]
    algo = GraphAlgoFactorGraphsMessagePassing[str]()
    res = algo.evaluate(variables, cards, factors, max_iterations=10)
    assert len(res["variable_marginals"]) == 2


def test_bayesian_structure_learning():
    variables = ["A", "B", "C"]
    data = [
        {"A": 0, "B": 0, "C": 0},
        {"A": 1, "B": 1, "C": 1},
        {"A": 0, "B": 0, "C": 0},
        {"A": 1, "B": 1, "C": 1},
    ] * 10
    algo = GraphAlgoBayesianNetworkStructureLearning[str]()
    res = algo.evaluate(variables, data, max_iterations=20)
    assert len(res["dag_adjacency"]) == 3


def test_d_separation():
    dag = {"A": ["B"], "B": ["C"]}
    algo = GraphAlgoDSeparationBayesBall[str]()
    res = algo.evaluate(dag, set_x=["A"], set_y=["C"], conditioning_set=["B"])
    assert res["is_d_separated"] is True


def test_pc_causal_discovery():
    variables = ["A", "B", "C"]
    data = [
        {"A": 1.0, "B": 2.0, "C": 3.0},
        {"A": 2.0, "B": 4.0, "C": 6.0},
        {"A": 3.0, "B": 6.0, "C": 9.0},
        {"A": 4.0, "B": 8.0, "C": 12.0},
    ] * 5
    algo = GraphAlgoConstraintCausalDiscoveryPcFci[str]()
    res = algo.evaluate(variables, data)
    assert "skeleton_adj" in res


def test_do_calculus():
    dag = {"X": ["Y"], "Z": ["X", "Y"]}
    algo = GraphAlgoDoCalculusBackdoorFrontdoor[str]()
    res = algo.evaluate(dag, treatment="X", outcome="Y")
    assert res["is_identifiable"] is True
    assert "Z" in res["adjustment_set"]


def test_graphical_lasso():
    cov = [[1.0, 0.6], [0.6, 1.0]]
    algo = GraphAlgoGraphicalLassoPrecision[str]()
    res = algo.evaluate(["A", "B"], cov, l1_penalty=0.1)
    assert len(res["precision_matrix"]) == 4


def test_nn_descent():
    points = {"A": [0.0, 0.0], "B": [0.1, 0.1], "C": [10.0, 10.0]}
    algo = GraphAlgoNnDescentKnnGraph[str]()
    res = algo.evaluate(points, k=1, max_iterations=5)
    assert len(res["knn_graph"]) == 3


def test_similarity_graph():
    points = {"A": [0.0, 0.0], "B": [1.0, 0.0], "C": [0.0, 1.0]}
    algo = GraphAlgoSimilarityGraphConstruction[str]()
    res = algo.evaluate(points, method="mutual_knn", k=2)
    assert len(res["weighted_adjacency"]) == 3


def test_textrank():
    tokens = ["graph", "algorithm", "ranking", "graph", "algorithm", "pagerank"]
    algo = GraphAlgoTextrankKeywordSentenceRanking[str]()
    res = algo.evaluate(tokens, window_size=2)
    assert len(res["ranks"]) > 0


def test_harmonic_label_propagation():
    adj = {"A": {"B": 1.0}, "B": {"A": 1.0, "C": 1.0}, "C": {"B": 1.0}}
    labeled = {"A": 0, "C": 1}
    algo = GraphAlgoHarmonicLabelPropagation[str]()
    res = algo.evaluate(adj, labeled, num_classes=2)
    assert res["predictions"]["A"] == 0
    assert res["predictions"]["C"] == 1


def test_pixie():
    adj = {"U1": ["I1", "I2"], "U2": ["I2", "I3"], "I1": ["U1"], "I2": ["U1", "U2"], "I3": ["U2"]}
    algo = GraphAlgoPixieRandomWalkRecommendation[str]()
    res = algo.evaluate(adj, query_seeds={"I1": 1.0}, num_total_steps=500)
    assert "recommendations" in res


def test_p3alpha_rp3beta():
    interactions = {"U1": ["I1", "I2"], "U2": ["I2", "I3"]}
    algo = GraphAlgoP3alphaRp3betaRecommenders[str]()
    res = algo.evaluate(interactions, target_user="U1", top_k=5)
    assert res["algorithm_variant"] == "RP3beta"


def test_pra():
    triplets = [("A", "knows", "B"), ("B", "knows", "C"), ("A", "friend", "C")]
    algo = GraphAlgoPathRankingAlgorithmPra[str]()
    res = algo.evaluate(triplets, target_relation="friend", candidate_source="A")
    assert "candidate_scores" in res


def test_hetesim():
    node_types = {"A1": "Author", "P1": "Paper", "A2": "Author"}
    rel_adj = {("Author", "Paper"): {"A1": ["P1"]}, ("Paper", "Author"): {"P1": ["A2"]}}
    algo = GraphAlgoHetesimMetapathRelevance[str]()
    res = algo.evaluate(node_types, rel_adj, ["Author", "Paper", "Author"], "A1", "A2")
    assert 0.0 <= res["relevance_score"] <= 1.0


def test_pathsim():
    node_types = {"A1": "Author", "P1": "Paper", "A2": "Author"}
    rel_adj = {("Author", "Paper"): {"A1": ["P1"], "A2": ["P1"]}, ("Paper", "Author"): {"P1": ["A1", "A2"]}}
    algo = GraphAlgoPathsimMetapathSimilarity[str]()
    res = algo.evaluate(node_types, rel_adj, ["Author", "Paper", "Author"], "A1", "A2")
    assert res["pathsim_score"] > 0.0


def test_isorank():
    adj1 = {"A": ["B"], "B": ["A"]}
    adj2 = {"1": ["2"], "2": ["1"]}
    algo = GraphAlgoIsorankSpectralAlignment[str]()
    res = algo.evaluate(adj1, adj2, max_iterations=10)
    assert len(res["matching"]) == 2


def test_regal_alignment():
    adj1 = {"A": ["B"], "B": ["A"]}
    adj2 = {"1": ["2"], "2": ["1"]}
    algo = GraphAlgoRegalEmbeddingAlignment[str]()
    res = algo.evaluate(adj1, adj2, embedding_dim=4)
    assert len(res["aligned_pairs"]) == 2


def test_gromov_wasserstein():
    c1 = [[0.0, 1.0], [1.0, 0.0]]
    c2 = [[0.0, 1.0], [1.0, 0.0]]
    algo = GraphAlgoGromovWassersteinMatching[str]()
    res = algo.evaluate(c1, c2, max_iterations=10)
    assert len(res["transport_coupling"]) == 2


def test_proximity_ann_rng():
    vectors = {"A": [0.0, 0.0], "B": [1.0, 0.0], "C": [0.0, 1.0], "D": [1.0, 1.0]}
    algo = GraphAlgoProximityGraphAnnRng[str]()
    res = algo.evaluate(vectors, r_max_degree=2)
    assert len(res["graph_adjacency"]) == 4


def test_kleinberg_routing():
    algo = GraphAlgoNavigabilityKleinbergRouting[str]()
    res = algo.evaluate(grid_size=5, num_shortcuts=1, source_coord=(0, 0), target_coord=(4, 4))
    assert res["hop_count"] >= 1


def test_ifds_dataflow():
    cfg = [("entry", "n1", "normal"), ("n1", "exit", "normal")]
    transfer = {("entry", "n1", "normal"): {"0": ["tainted"]}}
    algo = GraphAlgoIfdsIdeDataflowAnalysis[str]()
    res = algo.evaluate(cfg, ["0", "tainted"], transfer, entry_point="entry")
    assert "tainted" in res["reachable_facts"].get("n1", set())


def test_cfl_dyck():
    edges = [("A", "B", "("), ("B", "C", ")")]
    algo = GraphAlgoCflDyckReachability[str]()
    res = algo.evaluate(edges, [("S", ["(", ")"])], target_nonterminal="S")
    assert ("A", "C") in res["reachable_pairs"]


def test_andersen_points_to():
    stmts = [("addr", "p", "x"), ("copy", "q", "p")]
    algo = GraphAlgoAndersenPointsToAnalysis[str]()
    res = algo.evaluate(stmts)
    assert "x" in res["points_to_sets"]["q"]


def test_steensgaard_points_to():
    stmts = [("addr", "p", "x"), ("copy", "q", "p")]
    algo = GraphAlgoSteensgaardPointsToAnalysis[str]()
    res = algo.evaluate(stmts)
    assert "x" in res["points_to_sets"]["q"]
