"""
================================================================================
UNIT TESTS: VECTOR SEARCH ALGORITHMS (ALGO-VEC-SRCH-65 TO 79)
================================================================================
"""

import pytest

from src.features.code_engine.algos.vector_search import (
    VectorSearchAlgoNSW,
    VectorSearchAlgoHNSWSearch,
    VectorSearchAlgoHNSWInsert,
    VectorSearchAlgoBeamSearch,
    VectorSearchAlgoVamana,
    VectorSearchAlgoRobustPrune,
    VectorSearchAlgoNSG,
    VectorSearchAlgoCAGRA,
    VectorSearchAlgoEntryPoint,
    VectorSearchAlgoConnectivityRepair,
    VectorSearchAlgoFilteredDiskANN,
    VectorSearchAlgoSPANN,
    VectorSearchAlgoRandomHyperplaneLSH,
    VectorSearchAlgoMultiProbeLSH,
    VectorSearchAlgoE2LSH,
)


def test_nsw_build_and_search():
    vectors = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [10.0, 10.0]]
    res = VectorSearchAlgoNSW.build_and_search(vectors, query=[0.1, 0.1], k=2, max_edges=3)
    assert res["total_nodes"] == 4
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] == 0


def test_hnsw_insert_and_search():
    vectors = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 2.0], [10.0, 10.0]]
    idx = VectorSearchAlgoHNSWInsert.build_index(vectors, m=2, ef_construction=8)
    assert idx["total_nodes"] == 5
    assert idx["num_layers"] > 0

    s_res = VectorSearchAlgoHNSWSearch.search(
        vectors=vectors,
        layers=idx["layers"],
        entry_point=idx["entry_point"],
        top_layer=idx["top_layer"],
        query=[0.05, 0.05],
        k=2,
        ef=8,
    )
    assert len(s_res["neighbors"]) == 2
    assert s_res["neighbors"][0]["id"] == 0


def test_beam_search_graph():
    vectors = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]]
    adj = {"0": [1], "1": [0, 2], "2": [1, 3], "3": [2]}
    res = VectorSearchAlgoBeamSearch.execute_beam_search(
        vectors=vectors,
        adjacency=adj,
        start_nodes=[0],
        query=[2.1, 0.0],
        k=2,
        ef=4,
    )
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] == 2


def test_robust_prune():
    point = [0.0, 0.0]
    candidate_vecs = [[1.0, 0.0], [1.1, 0.05], [0.0, 1.0], [5.0, 5.0]]
    res = VectorSearchAlgoRobustPrune.prune(
        point=point,
        candidate_vectors=candidate_vecs,
        alpha=1.2,
        r_max_degree=2,
    )
    assert res["total_selected"] <= 2
    assert 0 in res["selected_ids"]
    assert res["pruned_count"] >= 1


def test_vamana_diskann():
    vectors = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [5.0, 5.0], [5.1, 5.0]]
    res = VectorSearchAlgoVamana.build_and_search(
        vectors=vectors,
        query=[0.1, 0.1],
        k=2,
        r_max_degree=3,
        l_search_list_size=4,
        alpha=1.2,
    )
    assert res["total_nodes"] == 5
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] == 0


def test_nsg_graph():
    vectors = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 2.0]]
    res = VectorSearchAlgoNSG.build_and_search(
        vectors=vectors,
        query=[0.05, 0.05],
        k=2,
        r_max_degree=2,
    )
    assert res["total_nodes"] == 4
    assert res["navigating_node"] >= 0
    assert len(res["neighbors"]) == 2


def test_cagra_regular_graph():
    vectors = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    res = VectorSearchAlgoCAGRA.execute(
        vectors=vectors,
        query=[0.05, 0.05],
        k=2,
        fixed_degree=2,
    )
    assert res["total_nodes"] == 4
    assert res["fixed_degree"] == 2
    assert len(res["regular_adjacency"]) == 4
    assert all(len(row) == 2 for row in res["regular_adjacency"])
    assert len(res["neighbors"]) == 2


def test_entry_point_selection():
    vectors = [[0.0, 0.0], [10.0, 10.0], [0.1, 0.1], [10.1, 10.1]]
    res_medoid = VectorSearchAlgoEntryPoint.select_entry_point(vectors, strategy="medoid")
    assert res_medoid["selected_entry_point"] >= 0

    res_adaptive = VectorSearchAlgoEntryPoint.select_entry_point(
        vectors, query=[9.9, 9.9], strategy="query_adaptive", num_seeds=2
    )
    assert res_adaptive["selected_entry_point"] in [1, 3]


def test_connectivity_repair():
    vectors = [[0.0, 0.0], [1.0, 0.0], [10.0, 10.0]]
    disconnected_adj = {"0": [1], "1": [0], "2": []}
    res = VectorSearchAlgoConnectivityRepair.audit_and_repair(
        vectors=vectors,
        adjacency=disconnected_adj,
        entry_points=[0],
    )
    assert res["unreachable_count"] == 1
    assert 2 in res["unreachable_nodes"]
    assert res["repaired_edges_added"] > 0
    assert 2 in res["repaired_adjacency"]["1"] or 2 in res["repaired_adjacency"]["0"]


def test_filtered_diskann():
    vectors = [[0.0, 0.0], [0.1, 0.1], [10.0, 10.0], [10.1, 10.1]]
    labels = ["tenantA", "tenantB", "tenantA", "tenantB"]
    res = VectorSearchAlgoFilteredDiskANN.search_filtered(
        vectors=vectors,
        labels=labels,
        query=[0.05, 0.05],
        target_label="tenantA",
        k=2,
    )
    assert res["target_label"] == "tenantA"
    assert res["matching_points"] == 2
    assert all(n["label"] == "tenantA" for n in res["neighbors"])


def test_spann_hybrid_partitions():
    vectors = [[0.0, 0.0], [0.1, 0.0], [5.0, 5.0], [5.1, 5.0]]
    res = VectorSearchAlgoSPANN.build_and_search(
        vectors=vectors,
        query=[0.05, 0.0],
        k=2,
        num_centroids=2,
        nprobe=1,
        slack_factor=1.2,
    )
    assert res["num_centroids"] == 2
    assert res["duplication_ratio"] >= 1.0
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] in [0, 1]


def test_random_hyperplane_lsh():
    vectors = [[1.0, 0.0], [0.99, 0.01], [0.0, 1.0], [-1.0, 0.0]]
    res = VectorSearchAlgoRandomHyperplaneLSH.build_and_search(
        vectors=vectors,
        query=[1.0, 0.0],
        k=2,
        num_bits=3,
        num_tables=4,
    )
    assert res["num_tables"] == 4
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] == 0


def test_multi_probe_lsh():
    vectors = [[1.0, 0.0], [0.99, 0.01], [0.0, 1.0], [0.0, -1.0]]
    res = VectorSearchAlgoMultiProbeLSH.build_and_search(
        vectors=vectors,
        query=[1.0, 0.0],
        k=2,
        num_bits=4,
        probe_budget=3,
    )
    assert len(res["probed_buckets"]) >= 1
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] == 0


def test_e2lsh():
    vectors = [[0.0, 0.0], [0.1, 0.1], [10.0, 10.0], [20.0, 20.0]]
    res = VectorSearchAlgoE2LSH.build_and_search(
        vectors=vectors,
        query=[0.05, 0.05],
        k=2,
        slot_width_w=2.0,
        num_projections_m=3,
        num_tables_l=3,
    )
    assert res["num_tables_l"] == 3
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] in [0, 1]
