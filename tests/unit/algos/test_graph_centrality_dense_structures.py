"""
================================================================================
UNIT TESTS: GRAPH CENTRALITY, DENSE STRUCTURES & NETWORK MEASURES (#101-150)
================================================================================
"""

import pytest
from src.features.code_engine.algos.graph.centrality_dense_structures import (
    GraphAlgoDegreeCentrality,
    GraphAlgoPageRankInDepth,
    GraphAlgoPushPersonalizedPageRank,
    GraphAlgoMonteCarloBidirectionalPpr,
    GraphAlgoSimRank,
    GraphAlgoHitsSalsa,
    GraphAlgoKatzCentrality,
    GraphAlgoEigenvectorCentrality,
    GraphAlgoBrandesBetweenness,
    GraphAlgoApproxBetweenness,
    GraphAlgoHyperBallCloseness,
    GraphAlgoCurrentFlowCentrality,
    GraphAlgoInfluenceMaximization,
    GraphAlgoCollectiveInfluence,
    GraphAlgoLocalSimilarityIndices,
    GraphAlgoGlobalSimilarityIndices,
    GraphAlgoDiffusionKernels,
    GraphAlgoRolxStructuralRoles,
    GraphAlgoRegularEquivalence,
    GraphAlgoGraphletDegreeVectors,
    GraphAlgoExactTriangleCounting,
    GraphAlgoApproxTriangleCounting,
    GraphAlgoClusteringCoefficients,
    GraphAlgoKCliqueListing,
    GraphAlgoBronKerboschCliques,
    GraphAlgoMaximumClique,
    GraphAlgoKTrussDecomposition,
    GraphAlgoNucleusDecomposition,
    GraphAlgoDensestSubgraph,
    GraphAlgoFraudarDenseBlocks,
    GraphAlgoQuasiCliqueMining,
    GraphAlgoMotifSignificance,
    GraphAlgoAssortativityCoefficient,
    GraphAlgoRichClubCoefficient,
    GraphAlgoPowerLawFit,
    GraphAlgoHyperanfEffectiveDiameter,
    GraphAlgoExactDiameterIfub,
    GraphAlgoEccentricityBounding,
    GraphAlgoSmallWorldMeasures,
    GraphAlgoBowtieDecomposition,
    GraphAlgoConfigurationModel,
    GraphAlgoGenerativeGraphModels,
    GraphAlgoErgmStatistics,
    GraphAlgoPercolationRobustness,
    GraphAlgoCascadeFailureMotterLai,
    GraphAlgoEpidemicSirSis,
    GraphAlgoIndependentCascadeSimulation,
    GraphAlgoGraphSampling,
    GraphAlgoSnowballRdsSampling,
    GraphAlgoGraphSizeEstimation,
)


def test_degree_centrality() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 2.0)],
        "B": [("C", 1.5)],
        "C": [],
    }
    engine = GraphAlgoDegreeCentrality[str](adj, is_directed=True)
    metrics = engine.compute_metrics()
    assert metrics["out_degrees"]["A"] == 2.0
    assert metrics["in_degrees"]["C"] == 2.0
    assert metrics["strengths"]["A"] == 3.0


def test_pagerank_in_depth() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 1.0)],
        "B": [("C", 1.0)],
        "C": [("A", 1.0)],
    }
    engine = GraphAlgoPageRankInDepth[str](adj, damping=0.85, max_iter=50)
    ranks, iters, conv, _ = engine.compute_pagerank()
    assert conv is True
    assert sum(ranks.values()) == pytest.approx(1.0, rel=1e-3)
    assert ranks["C"] > ranks["B"]


def test_push_personalized_pagerank() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["C", "D"],
        "C": ["A"],
        "D": ["A"],
    }
    engine = GraphAlgoPushPersonalizedPageRank[str](adj, alpha=0.15, epsilon=1e-3)
    p, r, pushes = engine.compute_ppr("A")
    assert "A" in p
    assert p["A"] > 0.0
    assert pushes > 0


def test_simrank() -> None:
    adj = {
        "Univ": ["ProfA", "ProfB"],
        "ProfA": ["Student1"],
        "ProfB": ["Student2"],
        "Student1": ["Univ"],
        "Student2": ["Univ"],
    }
    engine = GraphAlgoSimRank[str](adj, decay_c=0.8, max_iter=5)
    sim, _, _ = engine.compute_similarity()
    assert sim[("Student1", "Student1")] == 1.0
    assert sim[("ProfA", "ProfB")] > 0.0


def test_hits_salsa() -> None:
    adj = {
        "Hub1": ["Auth1", "Auth2"],
        "Hub2": ["Auth2", "Auth3"],
        "Auth1": [],
        "Auth2": [],
        "Auth3": [],
    }
    engine = GraphAlgoHitsSalsa[str](adj, max_iter=20)
    hubs, auths = engine.compute_hits()
    assert auths["Auth2"] >= auths["Auth1"]
    s_hubs, s_auths = engine.compute_salsa()
    assert s_auths["Auth2"] > 0.0


def test_katz_centrality() -> None:
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": [],
    }
    engine = GraphAlgoKatzCentrality[str](adj, alpha=0.2, beta=1.0, max_iter=50)
    scores, _, conv = engine.compute_centrality()
    assert conv is True
    assert scores["D"] > scores["A"]


def test_eigenvector_centrality() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoEigenvectorCentrality[str](adj, max_iter=50)
    ev, l_max, _, conv = engine.compute_centrality()
    assert conv is True
    assert ev["C"] > ev["D"]


def test_brandes_betweenness() -> None:
    adj = {
        "A": [("B", 1.0)],
        "B": [("A", 1.0), ("C", 1.0)],
        "C": [("B", 1.0)],
    }
    engine = GraphAlgoBrandesBetweenness[str](adj, is_directed=False, normalized=True)
    cb, eb = engine.compute_betweenness()
    assert cb["B"] == 1.0
    assert cb["A"] == 0.0
    assert cb["C"] == 0.0


def test_approx_betweenness() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B"],
    }
    engine = GraphAlgoApproxBetweenness[str](adj, num_samples=100, rng_seed=42)
    approx_cb, sampled = engine.compute_approx_betweenness()
    assert sampled > 0
    assert approx_cb["B"] >= approx_cb["A"]


def test_hyperball_closeness() -> None:
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": [],
    }
    engine = GraphAlgoHyperBallCloseness[str](adj, num_registers=16, max_rounds=5)
    harmonic, sizes, _ = engine.compute_centrality()
    assert harmonic["A"] > harmonic["C"]


def test_current_flow_centrality() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoCurrentFlowCentrality[str](adj)
    cb, cc, res = engine.compute_centrality()
    assert len(cc) == 3
    assert res[("A", "B")] > 0.0


def test_influence_maximization() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 1.0)],
        "B": [("D", 0.8)],
        "C": [("D", 0.8)],
        "D": [],
    }
    engine = GraphAlgoInfluenceMaximization[str](adj, k=1, num_simulations=50, rng_seed=42)
    seeds, spread, gains = engine.select_seeds()
    assert len(seeds) == 1
    assert seeds[0] == "A"
    assert spread > 2.0


def test_collective_influence() -> None:
    adj = {
        "Hub": ["A", "B"],
        "A": ["Hub", "A1", "A2"],
        "B": ["Hub", "B1", "B2"],
        "A1": ["A"],
        "A2": ["A"],
        "B1": ["B"],
        "B2": ["B"],
    }
    engine = GraphAlgoCollectiveInfluence[str](adj, radius_ell=1)
    ci, coreness, top = engine.compute_metrics()
    assert top[0] == "Hub"
    assert ci["Hub"] > 0.0


def test_local_similarity_indices() -> None:
    adj = {
        "A": ["Common1", "Common2", "OnlyA"],
        "B": ["Common1", "Common2", "OnlyB"],
        "Common1": ["A", "B"],
        "Common2": ["A", "B"],
        "OnlyA": ["A"],
        "OnlyB": ["B"],
    }
    engine = GraphAlgoLocalSimilarityIndices[str](adj)
    sims = engine.compute_pair_similarity("A", "B")
    assert sims["jaccard"] == 0.5
    assert sims["salton_cosine"] == pytest.approx(2.0 / 3.0, rel=1e-3)
    assert sims["adamic_adar"] > 0.0


def test_global_similarity_indices() -> None:
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": [],
    }
    engine = GraphAlgoGlobalSimilarityIndices[str](adj, katz_beta=0.1, lp_epsilon=0.01)
    katz, lp, _ = engine.compute_similarities()
    assert katz[("A", "C")] > 0.0
    assert lp[("A", "C")] > 0.0


def test_diffusion_kernels() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B"],
    }
    engine = GraphAlgoDiffusionKernels[str](adj, diffusion_time_t=0.5, gamma=0.1)
    heat, reg = engine.compute_kernels()
    assert heat[("A", "A")] > heat[("A", "C")]
    assert reg[("A", "A")] > 0.0


def test_rolx_structural_roles() -> None:
    adj = {
        "C1": ["L1_1", "L1_2"],
        "L1_1": ["C1"],
        "L1_2": ["C1"],
        "C2": ["L2_1", "L2_2"],
        "L2_1": ["C2"],
        "L2_2": ["C2"],
    }
    engine = GraphAlgoRolxStructuralRoles[str](adj, num_roles=2, num_recursions=1)
    role_dist, primary_role, _ = engine.extract_roles()
    assert primary_role["C1"] == primary_role["C2"]
    assert primary_role["L1_1"] == primary_role["L2_1"]


def test_regular_equivalence() -> None:
    adj = {
        "M1": ["W1", "W2"],
        "M2": ["W3", "W4"],
        "W1": [],
        "W2": [],
        "W3": [],
        "W4": [],
    }
    engine = GraphAlgoRegularEquivalence[str](adj, max_iter=5)
    m, classes = engine.compute_equivalence()
    assert m[("M1", "M2")] == 1.0


def test_graphlet_degree_vectors() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoGraphletDegreeVectors[str](adj)
    gdv, global_c = engine.compute_gdv()
    assert global_c["G2_triangle"] == 1
    assert gdv["A"][0] == 2


def test_exact_triangle_counting() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoExactTriangleCounting[str](adj)
    total_t, node_t, _ = engine.count_triangles()
    assert total_t == 1
    assert node_t["A"] == 1
    assert node_t["D"] == 0


def test_approx_triangle_counting() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoApproxTriangleCounting[str](adj, doulion_p=1.0, num_wedge_samples=100)
    doulion, wedge, _ = engine.estimate_triangles()
    assert doulion == 1.0
    assert wedge == 1.0


def test_clustering_coefficients() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoClusteringCoefficients[str](adj)
    local_c, avg_c, global_trans = engine.compute_coefficients()
    assert local_c["A"] == 1.0
    assert avg_c == 1.0
    assert global_trans == 1.0


def test_k_clique_listing() -> None:
    adj = {
        "A": ["B", "C", "D"],
        "B": ["A", "C", "D"],
        "C": ["A", "B", "D"],
        "D": ["A", "B", "C"],
    }
    engine = GraphAlgoKCliqueListing[str](adj, k=3)
    count, cliques, truncated = engine.list_cliques()
    assert count == 4
    assert len(cliques) == 4
    assert truncated is False


def test_bron_kerbosch_cliques() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoBronKerboschCliques[str](adj, min_size=2)
    count, cliques, max_sz = engine.enumerate_maximal_cliques()
    assert count == 2
    assert max_sz == 3


def test_maximum_clique() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoMaximumClique[str](adj)
    max_sz, best_clique, _ = engine.find_maximum_clique()
    assert max_sz == 3
    assert set(best_clique) == {"A", "B", "C"}


def test_k_truss_decomposition() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoKTrussDecomposition[str](adj)
    edge_truss, max_k, _ = engine.compute_truss_decomposition()
    assert max_k == 3


def test_nucleus_decomposition() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoNucleusDecomposition[str](adj, r=1, s=2)
    coreness, max_k = engine.compute_nucleus()
    assert max_k == 2


def test_densest_subgraph() -> None:
    adj = {
        "A": ["B", "C", "D"],
        "B": ["A", "C", "D"],
        "C": ["A", "B", "D", "E"],
        "D": ["A", "B", "C"],
        "E": ["C"],
    }
    engine = GraphAlgoDensestSubgraph[str](adj)
    max_density, nodes, _ = engine.compute_densest_subgraph()
    assert max_density == 1.5
    assert set(nodes) == {"A", "B", "C", "D"}


def test_fraudar_dense_blocks() -> None:
    bipartite_edges = [
        ("U1", "I1"), ("U1", "I2"),
        ("U2", "I1"), ("U2", "I2"),
        ("U3", "I3"),
    ]
    engine = GraphAlgoFraudarDenseBlocks[str](bipartite_edges)
    score, users, items = engine.detect_fraud_block()
    assert score > 0.0
    assert "U1" in users and "U2" in users


def test_quasi_clique_mining() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C", "E"],
        "E": ["D"],
    }
    engine = GraphAlgoQuasiCliqueMining[str](adj, gamma=0.6, min_size=3)
    cliques, count = engine.mine_quasi_cliques()
    assert count >= 1


def test_motif_significance() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["C"],
        "C": [],
    }
    engine = GraphAlgoMotifSignificance[str](adj, num_null_samples=5, rng_seed=42)
    real_c, z_scores, _ = engine.compute_significance()
    assert real_c["feedforward_loop"] == 1


def test_assortativity_coefficient() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B"],
    }
    engine = GraphAlgoAssortativityCoefficient[str](adj)
    r, _, mean_deg = engine.compute_assortativity()
    assert -1.0 <= r <= 1.0
    assert mean_deg > 0.0


def test_rich_club_coefficient() -> None:
    adj = {
        "H1": ["H2", "L1", "L2"],
        "H2": ["H1", "L3", "L4"],
        "L1": ["H1"],
        "L2": ["H1"],
        "L3": ["H2"],
        "L4": ["H2"],
    }
    engine = GraphAlgoRichClubCoefficient[str](adj, num_null_models=3, rng_seed=42)
    raw_phi, norm_rho, max_deg = engine.compute_rich_club()
    assert max_deg == 3
    assert 0 in raw_phi


def test_power_law_fit() -> None:
    degrees = [100, 50, 25, 12, 6, 3, 2, 1, 1, 1, 1, 1]
    engine = GraphAlgoPowerLawFit[str](degrees)
    alpha, xmin, ks, tail = engine.fit_power_law()
    assert alpha > 1.0
    assert xmin >= 1


def test_hyperanf_effective_diameter() -> None:
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": [],
    }
    engine = GraphAlgoHyperanfEffectiveDiameter[str](adj, num_registers=16, max_hops=5)
    eff_d, avg_d, hops = engine.compute_effective_diameter()
    assert eff_d >= 0.0
    assert len(hops) > 0


def test_exact_diameter_ifub() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoExactDiameterIfub[str](adj)
    diam, pair, bfs_runs = engine.compute_exact_diameter()
    assert diam == 3
    assert bfs_runs > 0


def test_eccentricity_bounding() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B", "D"],
        "D": ["C"],
    }
    engine = GraphAlgoEccentricityBounding[str](adj)
    ecc, radius, center, periphery = engine.compute_eccentricities()
    assert radius == 2
    assert set(center) == {"B", "C"}
    assert set(periphery) == {"A", "D"}


def test_small_world_measures() -> None:
    adj = {
        "A": ["B", "C", "D"],
        "B": ["A", "C", "D"],
        "C": ["A", "B", "D"],
        "D": ["A", "B", "C"],
    }
    engine = GraphAlgoSmallWorldMeasures[str](adj, num_random_samples=3, rng_seed=42)
    sigma, omega, c_real, l_real = engine.compute_small_world()
    assert c_real == 1.0
    assert l_real == 1.0


def test_bowtie_decomposition() -> None:
    adj = {
        "In1": ["Core1"],
        "Core1": ["Core2"],
        "Core2": ["Core1", "Out1"],
        "Out1": [],
    }
    engine = GraphAlgoBowtieDecomposition[str](adj)
    core, in_p, out_p, tubes, tendrils, disc = engine.compute_decomposition()
    assert set(core) == {"Core1", "Core2"}
    assert set(in_p) == {"In1"}
    assert set(out_p) == {"Out1"}


def test_configuration_model() -> None:
    adj = {
        "A": ["B"],
        "B": ["A"],
    }
    engine = GraphAlgoConfigurationModel[str](adjacency=adj, num_swaps=10, rng_seed=42)
    edges, matched, swaps = engine.generate_or_rewire()
    assert len(edges) == 1


def test_generative_graph_models() -> None:
    er = GraphAlgoGenerativeGraphModels(n=10, model_type="erdos_renyi", p_or_m=0.5, rng_seed=42)
    edges, n, m = er.generate()
    assert n == 10
    assert m > 0

    ba = GraphAlgoGenerativeGraphModels(n=10, model_type="barabasi_albert", p_or_m=2, rng_seed=42)
    edges_ba, _, _ = ba.generate()
    assert len(edges_ba) > 0


def test_ergm_statistics() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoErgmStatistics[str](adj)
    edges, stars, triangles, gwesp = engine.compute_statistics()
    assert edges == 3
    assert stars == 3
    assert triangles == 1
    assert gwesp > 0.0


def test_percolation_robustness() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoPercolationRobustness[str](adj, attack_strategy="degree")
    r, fc, curve = engine.compute_robustness()
    assert r > 0.0
    assert len(curve) == 3


def test_cascade_failure_motter_lai() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoCascadeFailureMotterLai[str](adj, initial_failures=["A"], tolerance_alpha=0.5)
    failed, surv_ratio, rounds = engine.simulate_cascade()
    assert "A" in failed
    assert rounds >= 1


def test_epidemic_sir_sis() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B"],
    }
    engine = GraphAlgoEpidemicSirSis[str](adj, initial_infected=["A"], beta_infection=1.0, gamma_recovery=0.0, max_steps=5)
    total_inf, peak_inf, states, traj = engine.simulate_epidemic()
    assert total_inf == 3
    assert peak_inf == 3


def test_independent_cascade_simulation() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 1.0)],
        "B": [],
        "C": [],
    }
    engine = GraphAlgoIndependentCascadeSimulation[str](adj, seeds=["A"], model="IC", num_runs=20, rng_seed=42)
    spread, act_probs, dist = engine.simulate()
    assert spread == 3.0
    assert act_probs["B"] == 1.0


def test_graph_sampling() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    engine = GraphAlgoGraphSampling[str](adj, method="metropolis_hastings", sample_size=2, rng_seed=42)
    nodes, edges, cov = engine.sample()
    assert len(nodes) == 2


def test_snowball_rds_sampling() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["A"],
        "D": ["B"],
    }
    engine = GraphAlgoSnowballRdsSampling[str](adj, seeds=["A"], target_sample_size=3, rng_seed=42)
    nodes, weights, sz = engine.sample_rds()
    assert sz == 3
    assert "A" in nodes
    assert sum(weights.values()) == pytest.approx(1.0, rel=1e-3)


def test_graph_size_estimation() -> None:
    s1 = ["A", "B", "C", "D"]
    s2 = ["C", "D", "E", "F"]
    engine = GraphAlgoGraphSizeEstimation[str](sample_1=s1, sample_2=s2)
    lp, chapman, _ = engine.estimate_size()
    assert lp == 8.0
    assert chapman > 0.0
