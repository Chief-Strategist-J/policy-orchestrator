"""Unit tests for Connectivity, Trees, Flows, Matching and Routing Graph algorithms."""

import pytest
from src.features.code_engine.algos.graph.connectivity_flows import (
    GraphAlgoBlockCutTree,
    GraphAlgoBoruvkaMst,
    GraphAlgoBridgesArticulationPoints,
    GraphAlgoCentroidDecomposition,
    GraphAlgoChinesePostman,
    GraphAlgoChristofidesTsp,
    GraphAlgoDinicMaxFlow,
    GraphAlgoDominatorTree,
    GraphAlgoEdmondsArborescence,
    GraphAlgoEdmondsBlossomMatching,
    GraphAlgoEdmondsKarpMaxFlow,
    GraphAlgoEulerianPathHierholzer,
    GraphAlgoGaleShapleyStableMatching,
    GraphAlgoHeavyLightDecomposition,
    GraphAlgoHeldKarpTsp,
    GraphAlgoHopcroftKarpMatching,
    GraphAlgoHungarianAssignment,
    GraphAlgoKargerMinCut,
    GraphAlgoKonigVertexCover,
    GraphAlgoKruskalMst,
    GraphAlgoLcaBinaryLifting,
    GraphAlgoMaximumWeightClosure,
    GraphAlgoMinCostFlow,
    GraphAlgoPrimMst,
    GraphAlgoPushRelabel,
    GraphAlgoSteinerTreeApprox,
    GraphAlgoStoerWagnerMinCut,
    GraphAlgoTreeDpRerooting,
    GraphAlgoTreeIsomorphismAhu,
    GraphAlgoTwoEdgeConnected,
    GraphAlgoUnionFind,
)


def test_union_find() -> None:
    uf = GraphAlgoUnionFind[str](["A", "B", "C", "D"])
    assert uf.connected("A", "B") is False
    assert uf.union("A", "B") is True
    assert uf.connected("A", "B") is True
    assert uf.get_set_size("A") == 2
    uf.rollback()
    assert uf.connected("A", "B") is False


def test_bridges_articulation_points() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C", "D"],
        "C": ["B", "D"],
        "D": ["B", "C", "E"],
        "E": ["D"],
    }
    bap = GraphAlgoBridgesArticulationPoints[str](adj)
    aps, bridges = bap.analyze()
    assert "B" in aps or "D" in aps
    assert len(bridges) == 2


def test_block_cut_tree() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C", "D"],
        "C": ["B", "D"],
        "D": ["B", "C"],
    }
    bct = GraphAlgoBlockCutTree[str](adj)
    blocks, aps, tree_adj = bct.decompose()
    assert len(blocks) >= 2
    assert "B" in aps


def test_two_edge_connected() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    tec = GraphAlgoTwoEdgeConnected[str](adj)
    comps, bridges, tree = tec.decompose()
    assert len(comps) == 2
    assert len(bridges) == 1


def test_dominator_tree() -> None:
    adj = {
        "R": ["A", "B"],
        "A": ["C"],
        "B": ["C"],
        "C": ["D"],
        "D": [],
    }
    dt = GraphAlgoDominatorTree[str](adj)
    idom, tree, df = dt.compute_dominators("R")
    assert idom["C"] == "R"
    assert idom["D"] == "C"


def test_kruskal_mst() -> None:
    edges = [
        ("A", "B", 1.0),
        ("B", "C", 2.0),
        ("A", "C", 3.0),
    ]
    kmst = GraphAlgoKruskalMst[str](edges)
    total_w, mst_edges = kmst.compute_mst()
    assert total_w == 3.0
    assert len(mst_edges) == 2


def test_prim_mst() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 3.0)],
        "B": [("A", 1.0), ("C", 2.0)],
        "C": [("A", 3.0), ("B", 2.0)],
    }
    pmst = GraphAlgoPrimMst[str](adj)
    total_w, mst_edges = pmst.compute_mst()
    assert total_w == 3.0
    assert len(mst_edges) == 2


def test_boruvka_mst() -> None:
    edges = [
        ("A", "B", 1.0),
        ("B", "C", 2.0),
        ("A", "C", 3.0),
    ]
    bmst = GraphAlgoBoruvkaMst[str](edges)
    total_w, mst_edges = bmst.compute_mst()
    assert total_w == 3.0
    assert len(mst_edges) == 2


def test_edmonds_arborescence() -> None:
    edges = [
        ("R", "A", 10.0),
        ("R", "B", 2.0),
        ("B", "A", 1.0),
    ]
    earb = GraphAlgoEdmondsArborescence[str](edges)
    total_w, arb_edges = earb.compute_arborescence("R")
    assert total_w == 3.0
    assert len(arb_edges) == 2


def test_steiner_tree_approx() -> None:
    adj = {
        "A": [("X", 1.0)],
        "B": [("X", 1.0)],
        "C": [("X", 1.0)],
        "X": [("A", 1.0), ("B", 1.0), ("C", 1.0)],
    }
    st = GraphAlgoSteinerTreeApprox[str](adj)
    total_w, edges = st.compute_steiner_tree(["A", "B", "C"])
    assert total_w == 3.0
    assert len(edges) == 3


def test_lca_binary_lifting() -> None:
    adj = {
        "R": ["A", "B"],
        "A": ["C", "D"],
        "B": ["E"],
        "C": [],
        "D": [],
        "E": [],
    }
    lca = GraphAlgoLcaBinaryLifting[str](adj, root="R")
    assert lca.query_lca("C", "D") == "A"
    assert lca.query_lca("C", "E") == "R"
    assert lca.query_distance("C", "E") == 4


def test_heavy_light_decomposition() -> None:
    adj = {
        "R": ["A", "B"],
        "A": ["C", "D"],
        "B": [],
        "C": [],
        "D": [],
    }
    hld = GraphAlgoHeavyLightDecomposition[str](adj, root="R")
    segments = hld.get_path_segments("C", "B")
    assert len(segments) >= 1


def test_centroid_decomposition() -> None:
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B", "D"],
        "D": ["C"],
    }
    cd = GraphAlgoCentroidDecomposition[str](adj)
    root, tree, parents = cd.build_centroid_tree()
    assert root is not None
    assert len(parents) == 4


def test_tree_isomorphism_ahu() -> None:
    t1 = {"A": ["B", "C"], "B": ["A"], "C": ["A"]}
    t2 = {"1": ["2", "3"], "2": ["1"], "3": ["1"]}
    assert GraphAlgoTreeIsomorphismAhu.are_isomorphic(t1, t2) is True


def test_tree_dp_rerooting() -> None:
    adj = {
        "A": [("B", 1.0), ("C", 1.0)],
        "B": [("A", 1.0)],
        "C": [("A", 1.0)],
    }
    dp = GraphAlgoTreeDpRerooting[str](adj)
    res = dp.compute_sum_of_distances()
    assert res["A"] == 2.0
    assert res["B"] == 3.0


def test_edmonds_karp_max_flow() -> None:
    ek = GraphAlgoEdmondsKarpMaxFlow[str]()
    ek.add_edge("S", "A", 10.0)
    ek.add_edge("S", "B", 10.0)
    ek.add_edge("A", "T", 10.0)
    ek.add_edge("B", "T", 10.0)
    flow, flow_map = ek.compute_max_flow("S", "T")
    assert flow == 20.0
    s_part, t_part, cut = ek.extract_min_cut("S")
    assert len(s_part) >= 1


def test_dinic_max_flow() -> None:
    dinic = GraphAlgoDinicMaxFlow[str]()
    dinic.add_edge("S", "A", 10.0)
    dinic.add_edge("S", "B", 10.0)
    dinic.add_edge("A", "T", 10.0)
    dinic.add_edge("B", "T", 10.0)
    flow, flow_map = dinic.compute_max_flow("S", "T")
    assert flow == 20.0


def test_push_relabel() -> None:
    pr = GraphAlgoPushRelabel[str]()
    pr.add_edge("S", "A", 10.0)
    pr.add_edge("A", "T", 10.0)
    flow, _ = pr.compute_max_flow("S", "T")
    assert flow == 10.0


def test_stoer_wagner_min_cut() -> None:
    adj = {
        "A": [("B", 3.0), ("C", 1.0)],
        "B": [("A", 3.0), ("D", 2.0)],
        "C": [("A", 1.0), ("D", 4.0)],
        "D": [("B", 2.0), ("C", 4.0)],
    }
    sw = GraphAlgoStoerWagnerMinCut[str](adj)
    min_cut, p1, p2 = sw.compute_min_cut()
    assert min_cut > 0


def test_karger_min_cut() -> None:
    edges = [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D"), ("D", "E"), ("E", "F"), ("F", "D")]
    kmc = GraphAlgoKargerMinCut[str](edges)
    cut_val, p1, p2 = kmc.compute_min_cut(num_trials=30, seed=42)
    assert cut_val == 1


def test_min_cost_flow() -> None:
    mcf = GraphAlgoMinCostFlow[str]()
    mcf.add_edge("S", "A", cap=10.0, unit_cost=1.0)
    mcf.add_edge("S", "B", cap=10.0, unit_cost=5.0)
    mcf.add_edge("A", "T", cap=10.0, unit_cost=1.0)
    mcf.add_edge("B", "T", cap=10.0, unit_cost=1.0)
    cost, flow, _ = mcf.compute_min_cost_flow("S", "T", target_flow=5.0)
    assert flow == 5.0
    assert cost == 10.0


def test_hopcroft_karp_matching() -> None:
    adj = {
        "L1": ["R1", "R2"],
        "L2": ["R1"],
        "L3": ["R2"],
    }
    hk = GraphAlgoHopcroftKarpMatching[str, str](["L1", "L2", "L3"], ["R1", "R2"], adj)
    sz, match = hk.compute_maximum_matching()
    assert sz == 2


def test_hungarian_assignment() -> None:
    cost_matrix = [
        [4.0, 1.0, 3.0],
        [2.0, 0.0, 5.0],
        [3.0, 2.0, 2.0],
    ]
    ha = GraphAlgoHungarianAssignment[str, str](["L1", "L2", "L3"], ["R1", "R2", "R3"], cost_matrix)
    cost, assign = ha.compute_min_cost_assignment()
    assert len(assign) == 3
    assert cost == 5.0


def test_gale_shapley_stable_matching() -> None:
    p_prefs = {
        "M1": ["W1", "W2"],
        "M2": ["W1", "W2"],
    }
    a_prefs = {
        "W1": ["M1", "M2"],
        "W2": ["M1", "M2"],
    }
    gs = GraphAlgoGaleShapleyStableMatching[str, str](p_prefs, a_prefs)
    match = gs.compute_stable_matching()
    assert match["M1"] == "W1"
    assert match["M2"] == "W2"


def test_edmonds_blossom_matching() -> None:
    adj = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B", "D"],
        "D": ["C"],
    }
    eb = GraphAlgoEdmondsBlossomMatching[str](adj)
    sz, match = eb.compute_maximum_matching()
    assert sz == 2


def test_konig_vertex_cover() -> None:
    adj = {
        "L1": ["R1"],
        "L2": ["R1"],
    }
    kvc = GraphAlgoKonigVertexCover[str, str](["L1", "L2"], ["R1"], adj)
    l_cov, r_cov, sz = kvc.compute_minimum_vertex_cover()
    assert len(l_cov) + len(r_cov) == sz == 1


def test_eulerian_path_hierholzer() -> None:
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
    }
    eph = GraphAlgoEulerianPathHierholzer[str](adj, directed=True)
    has_p, is_c, trail = eph.find_eulerian_trail()
    assert has_p is True
    assert is_c is True
    assert len(trail) == 4


def test_chinese_postman() -> None:
    edges = [
        ("A", "B", 1.0),
        ("B", "C", 2.0),
        ("C", "A", 3.0),
    ]
    cpp = GraphAlgoChinesePostman[str](edges)
    cost, tour = cpp.compute_inspection_tour()
    assert cost == 6.0
    assert len(tour) >= 4


def test_held_karp_tsp() -> None:
    nodes = ["A", "B", "C"]
    matrix = [
        [0.0, 1.0, 3.0],
        [1.0, 0.0, 2.0],
        [3.0, 2.0, 0.0],
    ]
    hk = GraphAlgoHeldKarpTsp[str](nodes, matrix)
    cost, tour = hk.solve_exact_tsp()
    assert cost == 6.0
    assert len(tour) == 4


def test_christofides_tsp() -> None:
    nodes = ["A", "B", "C", "D"]
    matrix = [
        [0.0, 2.0, 2.0, 1.0],
        [2.0, 0.0, 1.0, 2.0],
        [2.0, 1.0, 0.0, 2.0],
        [1.0, 2.0, 2.0, 0.0],
    ]
    ctsp = GraphAlgoChristofidesTsp[str](nodes, matrix)
    cost, tour = ctsp.solve_tsp()
    assert cost <= 8.0
    assert len(tour) == 5


def test_maximum_weight_closure() -> None:
    values = {
        "ProjectA": 100.0,
        "ProjectB": -30.0,
        "ProjectC": -40.0,
    }
    prereqs = [("ProjectA", "ProjectB"), ("ProjectA", "ProjectC")]
    mwc = GraphAlgoMaximumWeightClosure[str](values, prereqs)
    profit, selected = mwc.solve_closure()
    assert profit == 30.0
    assert "ProjectA" in selected and "ProjectB" in selected and "ProjectC" in selected
