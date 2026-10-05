"""
================================================================================
UNIT TESTS: VECTOR FILTER ALGORITHMS (ALGO-VEC-FLTR-80 TO 84)
================================================================================
"""

import pytest

from src.features.code_engine.algos.vector_filter import (
    VectorFilterAlgoPreFilter,
    VectorFilterAlgoPostFilter,
    VectorFilterAlgoInGraphFilter,
    VectorFilterAlgoSelectivityPlanner,
    VectorFilterAlgoPartitionedIndex,
)


def test_vector_pre_filter():
    vectors = [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [10.0, 10.0]]
    metadata = [
        {"tenant": "alpha", "env": "prod"},
        {"tenant": "beta", "env": "prod"},
        {"tenant": "alpha", "env": "dev"},
        {"tenant": "alpha", "env": "prod"},
    ]
    res = VectorFilterAlgoPreFilter.search_filtered(
        vectors=vectors,
        metadata=metadata,
        query=[0.1, 0.1],
        filters={"tenant": "alpha", "env": "prod"},
        k=2,
    )
    assert res["total_vectors"] == 4
    assert res["passed_filter_count"] == 2
    assert len(res["matches"]) == 2
    assert res["matches"][0]["id"] == 0
    assert res["matches"][1]["id"] == 3


def test_vector_post_filter():
    vectors = [[0.0, 0.0], [0.1, 0.1], [0.2, 0.2], [10.0, 10.0]]
    metadata = [
        {"lang": "fr"},
        {"lang": "en"},
        {"lang": "en"},
        {"lang": "en"},
    ]
    res = VectorFilterAlgoPostFilter.search_with_oversampling(
        vectors=vectors,
        metadata=metadata,
        query=[0.05, 0.05],
        filters={"lang": "en"},
        k=2,
        oversample_factor=2.0,
    )
    assert res["requested_k"] == 2
    assert res["surviving_count"] == 2
    assert len(res["matches"]) == 2
    assert res["matches"][0]["id"] == 1
    assert res["matches"][1]["id"] == 2


def test_vector_in_graph_filter():
    vectors = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]]
    metadata = [
        {"status": "active"},
        {"status": "archived"},
        {"status": "active"},
        {"status": "active"},
    ]
    adj = {
        "0": [1],
        "1": [0, 2],
        "2": [1, 3],
        "3": [2],
    }
    res = VectorFilterAlgoInGraphFilter.search(
        vectors=vectors,
        metadata=metadata,
        adjacency=adj,
        entry_point=0,
        query=[1.9, 0.0],
        filters={"status": "active"},
        k=2,
        ef_search=4,
    )
    assert res["allowed_evaluated"] >= 2
    assert res["filtered_bypassed"] >= 1
    assert len(res["neighbors"]) == 2
    assert res["neighbors"][0]["id"] == 2


def test_vector_selectivity_planner():
    sample = [
        {"tenant": "T1"},
        {"tenant": "T2"},
        {"tenant": "T2"},
        {"tenant": "T2"},
    ]
    res_high_sel = VectorFilterAlgoSelectivityPlanner.plan(
        total_vectors=10000,
        metadata_sample=sample,
        filters={"tenant": "T1"},
        is_security_filter=False,
    )
    assert res_high_sel["selectivity_ratio"] == 0.25
    assert res_high_sel["selected_strategy"] == "in_graph_traversal"

    res_sec = VectorFilterAlgoSelectivityPlanner.plan(
        total_vectors=10000,
        metadata_sample=sample,
        filters={"tenant": "T1"},
        is_security_filter=True,
    )
    assert res_sec["selected_strategy"] == "pre_filter_isolated"


def test_vector_partitioned_index():
    partitions = {
        "tenant_A": [
            {"id": "doc1", "vector": [1.0, 0.0], "metadata": {"title": "Doc A1"}},
            {"id": "doc2", "vector": [0.0, 1.0], "metadata": {"title": "Doc A2"}},
        ],
        "tenant_B": [
            {"id": "doc3", "vector": [10.0, 10.0], "metadata": {"title": "Doc B1"}},
        ],
    }
    res = VectorFilterAlgoPartitionedIndex.search_partition(
        partitions=partitions,
        target_partition="tenant_A",
        query=[0.9, 0.1],
        k=1,
    )
    assert res["target_partition"] == "tenant_A"
    assert res["partition_size"] == 2
    assert len(res["matches"]) == 1
    assert res["matches"][0]["id"] == "doc1"
