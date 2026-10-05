"""
================================================================================
UNIT TESTS: VECTOR SEARCH ALGORITHMS (ALGO-VEC-SRCH-85 TO 110)
================================================================================
"""

import pytest

from src.features.code_engine.algos.vector_search import (
    VectorSearchAlgoBM25,
    VectorSearchAlgoSparseDenseHybrid,
    VectorSearchAlgoRRF,
    VectorSearchAlgoConvexScoreFusion,
    VectorSearchAlgoMMR,
    VectorSearchAlgoRangeSearch,
    VectorSearchAlgoMaxSim,
    VectorSearchAlgoMultiQueryExpansion,
    VectorSearchAlgoFullPrecisionRescore,
    VectorSearchAlgoCrossEncoderRerank,
    VectorSearchAlgoMultiStageFunnel,
    VectorSearchAlgoLLMListwiseRerank,
    VectorSearchAlgoHyDE,
    VectorSearchAlgoQueryRouting,
    VectorSearchAlgoScatterGather,
    VectorSearchAlgoPartitionAwareRouting,
    VectorSearchAlgoReplicationLoadBalancer,
    VectorSearchAlgoHedgedRequests,
    VectorSearchAlgoKWayMerge,
    VectorSearchAlgoQueryCache,
    VectorSearchAlgoSemanticCache,
    VectorSearchAlgoQueryBatching,
    VectorSearchAlgoMemoryTiering,
    VectorSearchAlgoDiskIOScheduler,
    VectorSearchAlgoAdmissionControl,
    VectorSearchAlgoSearchAutotune,
)
from src.features.code_engine.service.code_engine_service import CodeEngineService


def test_algo_85_bm25():
    corpus = ["the quick brown fox", "jumps over the lazy dog", "quick fox dog"]
    res = VectorSearchAlgoBM25.search(corpus, "quick fox", k=2)
    assert res["total_documents"] == 3
    assert len(res["matches"]) == 2
    assert res["matches"][0]["score"] > 0


def test_algo_86_sparse_dense_hybrid():
    dense = [{"id": "doc1", "score": 0.9}, {"id": "doc2", "score": 0.1}]
    sparse = [{"id": "doc1", "score": 10.0}, {"id": "doc2", "score": 1.0}]
    res = VectorSearchAlgoSparseDenseHybrid.blend(dense, sparse, alpha=0.5, k=2)
    assert res["dense_count"] == 2
    assert res["sparse_count"] == 2
    assert len(res["fused_results"]) == 2
    assert res["fused_results"][0]["id"] == "doc1"


def test_algo_87_rrf():
    rankings = [
        [{"id": "docA"}, {"id": "docB"}],
        [{"id": "docB"}, {"id": "docA"}],
    ]
    res = VectorSearchAlgoRRF.fuse(rankings, k_rrf=60, top_k=2)
    assert res["num_rankings"] == 2
    assert res["total_unique_items"] == 2
    assert len(res["fused_ranking"]) == 2


def test_algo_88_convex_score_fusion():
    score_lists = [
        [{"id": "docA", "score": 0.9}, {"id": "docB", "score": 0.1}],
        [{"id": "docA", "score": 100.0}, {"id": "docB", "score": 10.0}],
    ]
    res = VectorSearchAlgoConvexScoreFusion.fuse(score_lists, weights=[0.6, 0.4], top_k=2)
    assert len(res["fused_results"]) == 2
    assert res["fused_results"][0]["id"] == "docA"


def test_algo_89_mmr():
    candidate_vecs = [[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]]
    candidate_ids = ["a", "b", "c"]
    query_vec = [1.0, 0.0]
    res = VectorSearchAlgoMMR.rerank(candidate_vecs, candidate_ids, query_vec, lambda_mult=0.7, k=2)
    assert res["requested_k"] == 2
    assert len(res["selected"]) == 2
    assert res["selected"][0]["id"] == "a"


def test_algo_90_range_search():
    vectors = [[0.0, 0.0], [1.0, 1.0], [10.0, 10.0]]
    query = [0.0, 0.0]
    res = VectorSearchAlgoRangeSearch.search_range(vectors, query, radius=2.0)
    assert res["total_in_range"] == 2
    assert len(res["matches"]) == 2


def test_algo_91_maxsim():
    doc_toks = [[[1.0, 0.0], [0.0, 1.0]], [[0.5, 0.5]]]
    q_toks = [[1.0, 0.0]]
    res = VectorSearchAlgoMaxSim.compute_maxsim(doc_toks, q_toks, k=1)
    assert res["total_documents"] == 2
    assert len(res["matches"]) == 1
    assert res["matches"][0]["id"] == 0


def test_algo_92_multi_query_expansion():
    vectors = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
    queries = [[1.0, 0.0], [0.9, 0.1]]
    res = VectorSearchAlgoMultiQueryExpansion.search_expanded(vectors, queries, k=2)
    assert res["query_variants_count"] == 2
    assert len(res["matches"]) == 2


def test_algo_93_full_precision_rescore():
    cand_ids = [0, 1]
    full_vecs = [[1.0, 0.0], [0.0, 1.0]]
    query_vec = [1.0, 0.0]
    res = VectorSearchAlgoFullPrecisionRescore.rescore(cand_ids, full_vecs, query_vec, top_k=1)
    assert res["candidates_rescored"] == 2
    assert len(res["rescored_matches"]) == 1
    assert res["rescored_matches"][0]["id"] == 0


def test_algo_94_cross_encoder_rerank():
    query = "token refresh flow"
    candidates = [
        {"id": "doc1", "text": "how to refresh oauth token with refresh_token"},
        {"id": "doc2", "text": "database migration postgres backup"},
    ]
    res = VectorSearchAlgoCrossEncoderRerank.rerank(query, candidates, top_k=2)
    assert res["total_candidates"] == 2
    assert len(res["reranked_results"]) == 2
    assert res["reranked_results"][0]["id"] == "doc1"


def test_algo_95_multi_stage_funnel():
    s1 = [{"id": f"doc{i}", "score": float(i)} for i in range(30)]
    res = VectorSearchAlgoMultiStageFunnel.execute_funnel(s1, stage2_top_m=10, stage3_top_k=3)
    assert res["stage1_count"] == 30
    assert res["stage2_count"] == 10
    assert res["stage3_count"] == 3


def test_algo_96_llm_listwise_rerank():
    candidates = [{"id": "a", "text": "alpha"}, {"id": "b", "text": "beta"}]
    res = VectorSearchAlgoLLMListwiseRerank.rerank(
        query="test",
        candidates=candidates,
        simulated_llm_response="[1] > [0]",
        top_k=2,
    )
    assert res["candidate_count"] == 2
    assert res["reranked_results"][0]["id"] == "b"


def test_algo_97_hyde():
    corpus = [[1.0, 0.0], [0.0, 1.0]]
    query = [1.0, 0.0]
    hypo = [[0.9, 0.1]]
    res = VectorSearchAlgoHyDE.search_hyde(corpus, query, hypo, k=1)
    assert res["hypothetical_count"] == 1
    assert len(res["matches"]) == 1


def test_algo_98_query_routing():
    res = VectorSearchAlgoQueryRouting.route_query(
        "def parse_request():",
        available_routes=["lexical_bm25", "dense_vector", "direct_id_lookup"],
    )
    assert res["selected_route"] in ["lexical_bm25", "dense_vector", "direct_id_lookup"]
    assert "confidence" in res
    assert "features_detected" in res


def test_algo_99_scatter_gather():
    shard_results = [
        [{"id": "docA", "score": 0.95}],
        [{"id": "docB", "score": 0.85}],
    ]
    res = VectorSearchAlgoScatterGather.scatter_gather_merge(shard_results, top_k=2)
    assert res["total_shards"] == 2
    assert len(res["global_results"]) == 2
    assert res["global_results"][0]["id"] == "docA"


def test_algo_100_partition_aware_routing():
    centroids = [[1.0, 0.0], [0.0, 1.0]]
    c_map = {"0": "shard_alpha", "1": "shard_beta"}
    res = VectorSearchAlgoPartitionAwareRouting.route_to_shards(centroids, c_map, [0.95, 0.05], num_target_shards=1)
    assert res["selected_shards"] == ["shard_alpha"]


def test_algo_101_replication_load_balancer():
    replicas = [
        {"id": "rep1", "is_healthy": True, "active_connections": 10},
        {"id": "rep2", "is_healthy": True, "active_connections": 2},
    ]
    res = VectorSearchAlgoReplicationLoadBalancer.select_replica(replicas, strategy="least_loaded")
    assert res["selected_replica"]["id"] == "rep2"


def test_algo_102_hedged_requests():
    res = VectorSearchAlgoHedgedRequests.evaluate_hedged_execution(
        primary_latency_ms=100.0,
        backup_latency_ms=20.0,
        hedge_delay_threshold_ms=40.0,
        is_read_only=True,
    )
    assert res["hedged_issued"] is True
    assert res["winning_channel"] == "backup"
    assert res["effective_latency_ms"] == 60.0


def test_algo_103_kway_merge():
    shard_lists = [
        [{"id": "1", "score": 0.9}, {"id": "3", "score": 0.7}],
        [{"id": "2", "score": 0.8}, {"id": "4", "score": 0.6}],
    ]
    res = VectorSearchAlgoKWayMerge.merge(shard_lists, k=3)
    assert res["shard_count"] == 2
    assert len(res["merged_results"]) == 3
    assert res["merged_results"][0]["id"] == "1"


def test_algo_104_query_cache():
    store = {}
    res1 = VectorSearchAlgoQueryCache.get_or_set(
        cache_store=store,
        query="what is rag",
        tenant_id="tenant1",
        filters={},
        index_version="v1",
        results=[{"id": "doc1"}],
    )
    assert res1["is_hit"] is False
    assert len(store) == 1

    res2 = VectorSearchAlgoQueryCache.get_or_set(
        cache_store=store,
        query="what is rag",
        tenant_id="tenant1",
        filters={},
        index_version="v1",
    )
    assert res2["is_hit"] is True
    assert res2["cached_data"] == [{"id": "doc1"}]


def test_algo_105_semantic_cache():
    cached = [
        {"id": "entry1", "vector": [1.0, 0.0], "tenant_id": "t1", "response": "answer1"},
    ]
    res = VectorSearchAlgoSemanticCache.lookup(cached, [0.99, 0.01], tenant_id="t1", similarity_threshold=0.9)
    assert res["is_hit"] is True
    assert res["cached_response"] == "answer1"


def test_algo_106_query_batching():
    pending = [{"id": f"q{i}", "arrival_time": 0.0} for i in range(10)]
    res = VectorSearchAlgoQueryBatching.form_batches(pending, max_batch_size=4)
    assert res["total_pending"] == 10
    assert res["batches_formed"] == 3


def test_algo_107_memory_tiering():
    components = [
        {"name": "centroids", "size_mb": 64, "access_priority": 10},
        {"name": "full_vectors", "size_mb": 2048, "access_priority": 1},
    ]
    res = VectorSearchAlgoMemoryTiering.plan_tiering(components, ram_budget_mb=128)
    assert res["ram_allocated_mb"] == 64
    assert res["placement_plan"][0]["assigned_tier"] == "RAM"
    assert res["placement_plan"][1]["assigned_tier"] == "SSD_MMAP"


def test_algo_108_disk_io_scheduler():
    res = VectorSearchAlgoDiskIOScheduler.schedule_reads(
        requested_node_ids=[10, 20, 30],
        cached_nodes=[10],
        max_batch_size=2,
    )
    assert res["total_requested"] == 3
    assert res["cache_hits"] == 1
    assert res["disk_reads_required"] == 2
    assert len(res["io_batches"]) == 1


def test_algo_109_admission_control():
    res = VectorSearchAlgoAdmissionControl.evaluate_admission(
        current_tokens=10.0,
        max_tokens=100.0,
        refill_rate_per_sec=10.0,
        last_refill_timestamp=0.0,
        current_concurrency=2,
        max_concurrency=10,
        request_cost=1.0,
        now=1.0,
    )
    assert res["admitted"] is True
    assert res["recommended_ef_search"] == 64


def test_algo_110_search_autotune():
    ground_truth = [[1, 2, 3, 4, 5]]
    evals = [
        {"parameters": {"ef_search": 16}, "retrieved_topk": [[1, 2, 6, 7, 8]], "latency_ms": 1.0},
        {"parameters": {"ef_search": 64}, "retrieved_topk": [[1, 2, 3, 4, 5]], "latency_ms": 3.0},
    ]
    res = VectorSearchAlgoSearchAutotune.autotune_parameters(ground_truth, evals, target_recall=0.8)
    assert res["optimal_configuration"]["meets_target"] is True
    assert res["optimal_configuration"]["parameters"]["ef_search"] == 64


def test_code_engine_dispatch_batch_3():
    svc = CodeEngineService()
    res = svc.execute_algorithm(
        "ALGO-VEC-SRCH-85",
        {"corpus": ["alpha beta", "gamma delta"], "query": "alpha", "k": 1},
    )
    assert res["total_documents"] == 2
    assert len(res["matches"]) == 1
