"""
================================================================================
UNIT TESTS: VECTOR SEARCH ALGORITHMS (ALGO-VEC-SRCH-51 TO 64)
================================================================================
"""

import pytest
import numpy as np

from src.features.code_engine.algos.vector_search import (
    VectorSearchAlgoBruteForceGemm,
    VectorSearchAlgoSimdDistance,
    VectorSearchAlgoHeapTopK,
    VectorSearchAlgoRadixTopK,
    VectorSearchAlgoEarlyAbandoning,
    VectorSearchAlgoPivotPruning,
    VectorSearchAlgoKdTree,
    VectorSearchAlgoBallTree,
    VectorSearchAlgoVpTree,
    VectorSearchAlgoRpForest,
    VectorSearchAlgoIvf,
    VectorSearchAlgoIvfPq,
    VectorSearchAlgoNprobeTuner,
    VectorSearchAlgoInvertedMultiIndex,
)


def test_brute_force_gemm_l2_and_cosine():
    db = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    q = [[1.0, 0.0]]
    res_l2 = VectorSearchAlgoBruteForceGemm.search(db, q, k=2, metric="l2")
    assert res_l2["total_queries"] == 1
    assert len(res_l2["results"][0]["matches"]) == 2
    assert res_l2["results"][0]["matches"][0]["index"] == 0
    assert abs(res_l2["results"][0]["matches"][0]["distance"]) < 1e-5

    res_cos = VectorSearchAlgoBruteForceGemm.search(db, q, k=1, metric="cosine")
    assert res_cos["results"][0]["matches"][0]["index"] == 0
    assert abs(res_cos["results"][0]["matches"][0]["similarity"] - 1.0) < 1e-5


def test_simd_distance_all_metrics():
    va = [1.0, 2.0, 3.0, 4.0]
    vb = [1.0, 2.0, 3.0, 5.0]
    res_l2 = VectorSearchAlgoSimdDistance.compute_distance(va, vb, metric="l2")
    assert abs(res_l2["distance"] - 1.0) < 1e-5
    assert abs(res_l2["euclidean_distance"] - 1.0) < 1e-5

    res_dot = VectorSearchAlgoSimdDistance.compute_distance(va, vb, metric="dot")
    assert abs(res_dot["score"] - (1 + 4 + 9 + 20)) < 1e-5

    res_cos = VectorSearchAlgoSimdDistance.compute_distance(va, va, metric="cosine")
    assert abs(res_cos["similarity"] - 1.0) < 1e-5

    bits_a = [0b1011]
    bits_b = [0b1000]
    res_ham = VectorSearchAlgoSimdDistance.compute_distance(bits_a, bits_b, metric="hamming")
    assert res_ham["hamming_distance"] == 2


def test_heap_topk():
    candidates = [
        {"id": "doc1", "score": 10.5},
        {"id": "doc2", "score": 20.0},
        {"id": "doc3", "score": 5.2},
        {"id": "doc4", "score": 15.0},
    ]
    res = VectorSearchAlgoHeapTopK.select_top_k(candidates, k=2, order="desc")
    assert len(res["top_k"]) == 2
    assert res["top_k"][0]["id"] == "doc2"
    assert res["top_k"][1]["id"] == "doc4"


def test_radix_topk():
    scores = [10.0, 40.0, 20.0, 50.0, 30.0]
    res = VectorSearchAlgoRadixTopK.select_top_k(scores, k=3, largest=True)
    assert len(res["top_k"]) == 3
    assert res["top_k"][0]["score"] == 50.0
    assert res["top_k"][1]["score"] == 40.0
    assert res["top_k"][2]["score"] == 30.0


def test_early_abandoning():
    db = [[0.0, 0.0], [5.0, 5.0], [0.1, 0.1]]
    q = [0.0, 0.0]
    res = VectorSearchAlgoEarlyAbandoning.scan_with_early_abandon(db, q, k=1)
    assert len(res["matches"]) == 1
    assert res["matches"][0]["index"] == 0
    assert res["abandoned_count"] >= 1


def test_pivot_pruning():
    db = [[0.0, 0.0], [1.0, 1.0], [10.0, 10.0]]
    pivots = [[0.0, 0.0]]
    q = [0.1, 0.1]
    res = VectorSearchAlgoPivotPruning.search_with_pivots(db, pivots, q, k=1)
    assert len(res["matches"]) == 1
    assert res["matches"][0]["index"] == 0


def test_kdtree():
    vectors = [[2.0, 3.0], [5.0, 4.0], [9.0, 6.0], [4.0, 7.0], [8.0, 1.0], [7.0, 2.0]]
    q = [9.0, 5.0]
    res = VectorSearchAlgoKdTree.query_k_nearest(vectors, q, k=2)
    assert len(res["matches"]) == 2
    assert res["matches"][0]["index"] == 2


def test_ball_tree():
    vectors = [[0.0, 0.0], [1.0, 1.0], [5.0, 5.0], [10.0, 10.0]]
    q = [0.9, 0.9]
    res = VectorSearchAlgoBallTree.query_k_nearest(vectors, q, k=1, leaf_size=2)
    assert len(res["matches"]) == 1
    assert res["matches"][0]["index"] == 1


def test_vptree():
    vectors = [[0.0, 0.0], [1.0, 1.0], [5.0, 5.0], [10.0, 10.0]]
    q = [5.1, 5.1]
    res = VectorSearchAlgoVpTree.query_k_nearest(vectors, q, k=1)
    assert len(res["matches"]) == 1
    assert res["matches"][0]["index"] == 2


def test_rp_forest():
    vectors = [[float(i), float(i * 2)] for i in range(20)]
    q = [5.0, 10.0]
    res = VectorSearchAlgoRpForest.search(vectors, q, k=3, num_trees=4, search_k=20)
    assert len(res["matches"]) == 3
    assert res["matches"][0]["index"] == 5


def test_ivf():
    vectors = [[float(i), 0.0] for i in range(16)]
    q = [0.1, 0.0]
    res = VectorSearchAlgoIvf.search(vectors, q, k=2, num_clusters=4, nprobe=2)
    assert len(res["matches"]) == 2
    assert res["matches"][0]["index"] == 0


def test_ivf_pq():
    vectors = [[float(i), float(i), float(i), float(i)] for i in range(12)]
    q = [3.0, 3.0, 3.0, 3.0]
    res = VectorSearchAlgoIvfPq.search(vectors, q, k=2, num_clusters=3, nprobe=2, subspaces=2, codebook_size=3)
    assert len(res["matches"]) == 2


def test_nprobe_tuner():
    vectors = [[float(i), float(i)] for i in range(20)]
    queries = [[1.0, 1.0], [5.0, 5.0]]
    res = VectorSearchAlgoNprobeTuner.tune_nprobe(vectors, queries, target_recall=0.8, k=2, num_clusters=4)
    assert res["recommended_nprobe"] >= 1
    assert len(res["sweep_results"]) > 0


def test_inverted_multi_index():
    vectors = [[float(i), float(i % 3), float(i % 5), float(i)] for i in range(24)]
    q = [0.0, 0.0, 0.0, 0.0]
    res = VectorSearchAlgoInvertedMultiIndex.search(vectors, q, k=3, codebook_k1=3, codebook_k2=3, max_cells_to_probe=3)
    assert len(res["matches"]) == 3
