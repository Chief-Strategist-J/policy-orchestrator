import json
import pytest
from fastapi.testclient import TestClient
from src.api.rest.app import create_app
from src.features.code_engine.registry.algorithm_catalog import BUILTIN_ALGORITHM_CONTRACTS


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_api_has_exactly_42_builtin_algorithms(client):
    res = client.get("/api/v1/algos/contracts")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total_contracts"] == 152
    assert len(body["data"]["contracts"]) == 152


def test_api_execute_all_42_algorithms_direct(client):
    test_inputs = {
        "ALGO-SRCH-01": {"root_dir": "src/features"},
        "ALGO-SRCH-02": {"root_dir": "src/features"},
        "ALGO-SRCH-03": {"root_dir": "src/features"},
        "ALGO-SRCH-04": {"pattern": "*.py", "file_paths": ["test.py", "main.rs"]},
        "ALGO-SRCH-05": {"file_path": "pyproject.toml"},
        "ALGO-SRCH-06": {"file_path": "pyproject.toml"},
        "ALGO-SRCH-07": {"file_path": "pyproject.toml", "max_bytes": 1000000},
        "ALGO-SRCH-08": {"file_path": "pyproject.toml"},
        "ALGO-SRCH-09": {"text": "algorithm inverted index test"},
        "ALGO-SRCH-10": {"data": "hello\nworld\ntest\n", "byte": "\n"},
        "ALGO-SRCH-11": {"text": "the quick brown fox", "patterns": ["quick", "fox"]},
        "ALGO-SRCH-12": {"text": "user@example.com", "pattern": r"user@example\.com"},
        "ALGO-SRCH-13": {"file_path": "pyproject.toml", "needle": "policy"},
        "ALGO-SRCH-14": {"text": "line1\nline2 target\nline3", "match_offset": 6},
        "ALGO-SRCH-15": {"file_path": "pyproject.toml", "needle": "name"},
        "ALGO-OBS-16": {"content": "alpha\nbeta\ngamma", "offset": 7},
        "ALGO-OBS-17": {"code": "def foo():\n    return 42", "language": "python"},
        "ALGO-OBS-18": {"code": "x = 10\ndef bar():\n    y = 20\n    return x + y"},
        "ALGO-OBS-19": {"code": "def clean():\n    return 1"},
        "ALGO-OBS-20": {"file_paths": ["src/api/rest/app.py"]},
        "ALGO-OBS-21": {"code": "class Sample:\n    def method(self):\n        pass"},
        "ALGO-UPD-22": {"code": "x = old_fn()", "pattern": "old_fn", "replacement": "new_fn"},
        "ALGO-UPD-23": {"file_path": "/tmp/test_patch.txt", "patches": []},
        "ALGO-UPD-24": {"original_content": "line1\nline2", "modified_content": "line1\nline2_mod"},
        "ALGO-VEC-01": {"vector": [3.0, 4.0]},
        "ALGO-VEC-02": {"vectors": [[1.0, 2.0], [3.0, 4.0]]},
        "ALGO-VEC-03": {"vector": [1.0, 2.0, 3.0, 4.0]},
        "ALGO-VEC-04": {"vector": [1.0, 5.0, 10.0]},
        "ALGO-VEC-05": {"vector": [float(i) for i in range(128)], "target_dim": 32},
        "ALGO-VEC-06": {"vector": [0.1, -0.5, 0.9, -0.2], "bits": 8},
        "ALGO-VEC-07": {"vector": [0.5, -0.2, 0.8, -0.9]},
        "ALGO-VEC-08": {"token_embeddings": [[1.0, 2.0], [3.0, 4.0]]},
        "ALGO-VEC-09": {"text": "Hello world from vector semantic chunker.", "max_chunk_size": 50, "overlap": 10},
        "ALGO-GRAPH-01": {"adjacency_list": {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}, "start_node": "A"},
        "ALGO-GRAPH-02": {"adjacency_list": {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}, "start_node": "A"},
        "ALGO-GRAPH-03": {"weighted_edges": [{"source": "A", "target": "B", "weight": 1.0}], "start_node": "A", "target_node": "B"},
        "ALGO-GRAPH-04": {"weighted_edges": [{"source": "A", "target": "B", "weight": 1.0}], "start_node": "A", "target_node": "B"},
        "ALGO-GRAPH-05": {"adjacency_list": {"A": ["B"], "B": ["A"]}},
        "ALGO-GRAPH-06": {"adjacency_list": {"A": ["B"], "B": ["A"]}},
        "ALGO-GRAPH-07": {"edges": [["A", "B"], ["C", "D"]]},
        "ALGO-GRAPH-08": {"adjacency_list": {"A": ["B"], "B": ["A"]}},
        "ALGO-GRAPH-09": {"target_graph": {"1": ["2"], "2": []}, "pattern_graph": {"A": ["B"], "B": []}},
        "ALGO-VEC-SRCH-51": {"database_vectors": [[1.0, 0.0], [0.0, 1.0]], "query_vectors": [[1.0, 0.0]], "k": 2},
        "ALGO-VEC-SRCH-52": {"vector_a": [1.0, 2.0], "vector_b": [1.0, 3.0], "metric": "l2"},
        "ALGO-VEC-SRCH-53": {"candidates": [{"id": "1", "score": 5.0}], "k": 1},
        "ALGO-VEC-SRCH-54": {"scores": [1.0, 5.0, 2.0], "k": 2},
        "ALGO-VEC-SRCH-55": {"database_vectors": [[0.0, 0.0], [1.0, 1.0]], "query_vector": [0.0, 0.0], "k": 1},
        "ALGO-VEC-SRCH-56": {"database_vectors": [[0.0, 0.0], [1.0, 1.0]], "pivots": [[0.0, 0.0]], "query_vector": [0.1, 0.1], "k": 1},
        "ALGO-VEC-SRCH-57": {"vectors": [[1.0, 2.0], [3.0, 4.0]], "query": [1.0, 2.0], "k": 1},
        "ALGO-VEC-SRCH-58": {"vectors": [[1.0, 2.0], [3.0, 4.0]], "query": [1.0, 2.0], "k": 1},
        "ALGO-VEC-SRCH-59": {"vectors": [[1.0, 2.0], [3.0, 4.0]], "query": [1.0, 2.0], "k": 1},
        "ALGO-VEC-SRCH-60": {"vectors": [[1.0, 2.0], [3.0, 4.0]], "query": [1.0, 2.0], "k": 1, "num_trees": 2},
        "ALGO-VEC-SRCH-61": {"vectors": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], "query": [1.0, 2.0], "k": 1, "num_clusters": 2},
        "ALGO-VEC-SRCH-62": {"vectors": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]], "query": [1.0, 2.0, 3.0, 4.0], "k": 1, "num_clusters": 2, "subspaces": 2, "codebook_size": 2},
        "ALGO-VEC-SRCH-63": {"database_vectors": [[1.0, 2.0], [3.0, 4.0]], "sample_queries": [[1.0, 2.0]], "k": 1, "num_clusters": 2},
        "ALGO-VEC-SRCH-64": {"vectors": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]], "query": [1.0, 2.0, 3.0, 4.0], "k": 1, "codebook_k1": 2, "codebook_k2": 2},
        "ALGO-VEC-SRCH-65": {"vectors": [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [10.0, 10.0]], "query": [0.1, 0.1], "k": 2, "max_edges": 3},
        "ALGO-VEC-SRCH-66": {"vectors": [[0.0, 0.0], [1.0, 0.0]], "layers": [{"0": [1], "1": [0]}], "entry_point": 0, "top_layer": 0, "query": [0.1, 0.0], "k": 1, "ef": 4},
        "ALGO-VEC-SRCH-67": {"vectors": [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], "m": 2, "ef_construction": 4},
        "ALGO-VEC-SRCH-68": {"vectors": [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]], "adjacency": {"0": [1], "1": [0, 2], "2": [1]}, "start_nodes": [0], "query": [1.1, 0.0], "k": 1, "ef": 4},
        "ALGO-VEC-SRCH-69": {"vectors": [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], "query": [0.1, 0.1], "k": 2, "r_max_degree": 2, "l_search_list_size": 4, "alpha": 1.2},
        "ALGO-VEC-SRCH-70": {"point": [0.0, 0.0], "candidate_vectors": [[1.0, 0.0], [0.0, 1.0]], "alpha": 1.2, "r_max_degree": 2},
        "ALGO-VEC-SRCH-71": {"vectors": [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]], "query": [0.1, 0.1], "k": 2, "r_max_degree": 2},
        "ALGO-VEC-SRCH-72": {"vectors": [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], "query": [0.1, 0.1], "k": 2, "fixed_degree": 2},
        "ALGO-VEC-SRCH-73": {"vectors": [[0.0, 0.0], [1.0, 1.0]], "strategy": "medoid"},
        "ALGO-VEC-SRCH-74": {"vectors": [[0.0, 0.0], [1.0, 0.0]], "adjacency": {"0": [1], "1": [0]}, "entry_points": [0]},
        "ALGO-VEC-SRCH-75": {"vectors": [[0.0, 0.0], [1.0, 0.0]], "labels": ["t1", "t2"], "query": [0.0, 0.0], "target_label": "t1", "k": 1},
        "ALGO-VEC-SRCH-76": {"vectors": [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]], "query": [0.0, 0.0], "k": 1, "num_centroids": 2, "nprobe": 1, "slack_factor": 1.2},
        "ALGO-VEC-SRCH-77": {"vectors": [[1.0, 0.0], [0.0, 1.0]], "query": [1.0, 0.0], "k": 1, "num_bits": 2, "num_tables": 2},
        "ALGO-VEC-SRCH-78": {"vectors": [[1.0, 0.0], [0.0, 1.0]], "query": [1.0, 0.0], "k": 1, "num_bits": 2, "probe_budget": 2},
        "ALGO-VEC-SRCH-79": {"vectors": [[0.0, 0.0], [1.0, 1.0]], "query": [0.0, 0.0], "k": 1, "slot_width_w": 2.0, "num_projections_m": 2, "num_tables_l": 2},
        "ALGO-VEC-FLTR-80": {"vectors": [[0.0, 0.0], [1.0, 1.0]], "metadata": [{"tenant": "alpha"}, {"tenant": "beta"}], "query": [0.1, 0.1], "filters": {"tenant": "alpha"}, "k": 1},
        "ALGO-VEC-FLTR-81": {"vectors": [[0.0, 0.0], [1.0, 1.0]], "metadata": [{"lang": "en"}, {"lang": "fr"}], "query": [0.1, 0.1], "filters": {"lang": "en"}, "k": 1, "oversample_factor": 2.0},
        "ALGO-VEC-FLTR-82": {"vectors": [[0.0, 0.0], [1.0, 0.0]], "metadata": [{"status": "active"}, {"status": "inactive"}], "adjacency": {"0": [1], "1": []}, "entry_point": 0, "query": [0.9, 0.0], "filters": {"status": "active"}, "k": 1, "ef_search": 4},
        "ALGO-VEC-FLTR-83": {"total_vectors": 1000, "metadata_sample": [{"tenant": "T1"}, {"tenant": "T2"}], "filters": {"tenant": "T1"}, "is_security_filter": True},
        "ALGO-VEC-FLTR-84": {"partitions": {"tenant_A": [{"id": "d1", "vector": [1.0, 0.0], "metadata": {}}]}, "target_partition": "tenant_A", "query": [0.9, 0.1], "k": 1},
        "ALGO-VEC-SRCH-85": {"corpus": ["the quick brown fox"], "query": "fox", "k": 1},
        "ALGO-VEC-SRCH-86": {"dense_results": [{"id": "1", "score": 0.9}], "sparse_results": [{"id": "1", "score": 10.0}], "alpha": 0.5, "k": 1},
        "ALGO-VEC-SRCH-87": {"rankings": [[{"id": "doc1"}], [{"id": "doc1"}]], "k_rrf": 60, "top_k": 1},
        "ALGO-VEC-SRCH-88": {"score_lists": [[{"id": "doc1", "score": 0.9}]], "weights": [1.0], "top_k": 1},
        "ALGO-VEC-SRCH-89": {"candidate_vectors": [[1.0, 0.0]], "candidate_ids": ["1"], "query_vector": [1.0, 0.0], "lambda_mult": 0.5, "k": 1},
        "ALGO-VEC-SRCH-90": {"vectors": [[0.0, 0.0]], "query": [0.0, 0.0], "radius": 1.0, "metric": "l2", "max_results": 1},
        "ALGO-VEC-SRCH-91": {"document_token_vectors": [[[1.0, 0.0]]], "query_token_vectors": [[1.0, 0.0]], "k": 1},
        "ALGO-VEC-SRCH-92": {"vectors": [[1.0, 0.0]], "expanded_queries": [[1.0, 0.0]], "k": 1, "aggregation": "max"},
        "ALGO-VEC-SRCH-93": {"candidate_ids": [0], "full_precision_vectors": [[1.0, 0.0]], "query_vector": [1.0, 0.0], "metric": "l2", "top_k": 1},
        "ALGO-VEC-SRCH-94": {"query": "test", "candidates": [{"id": "1", "text": "test document"}], "top_k": 1},
        "ALGO-VEC-SRCH-95": {"stage1_candidates": [{"id": "1", "score": 1.0}], "stage2_top_m": 1, "stage3_top_k": 1},
        "ALGO-VEC-SRCH-96": {"query": "test", "candidates": [{"id": "1", "text": "doc"}], "simulated_llm_response": "[0]", "top_k": 1},
        "ALGO-VEC-SRCH-97": {"corpus_vectors": [[1.0, 0.0]], "query_vector": [1.0, 0.0], "hypothetical_vectors": [[1.0, 0.0]], "k": 1, "query_weight": 0.5},
        "ALGO-VEC-SRCH-98": {"query": "def parse():", "available_routes": ["lexical_bm25", "dense_vector"]},
        "ALGO-VEC-SRCH-99": {"shard_results": [[{"id": "doc1", "score": 1.0}]], "top_k": 1},
        "ALGO-VEC-SRCH-100": {"centroids": [[1.0, 0.0]], "centroid_to_shard_map": {"0": "shard1"}, "query_vector": [1.0, 0.0], "num_target_shards": 1},
        "ALGO-VEC-SRCH-101": {"replicas": [{"id": "rep1", "is_healthy": True, "active_connections": 1}], "strategy": "least_loaded", "counter": 0},
        "ALGO-VEC-SRCH-102": {"primary_latency_ms": 10.0, "backup_latency_ms": 5.0, "hedge_delay_threshold_ms": 2.0, "is_read_only": True},
        "ALGO-VEC-SRCH-103": {"shard_sorted_lists": [[{"id": "doc1", "score": 0.9}]], "k": 1},
        "ALGO-VEC-SRCH-104": {"cache_store": {}, "query": "q", "tenant_id": "t1", "filters": {}, "index_version": "v1", "results": [{"id": "1"}], "ttl_seconds": 3600.0, "max_size": 1000},
        "ALGO-VEC-SRCH-105": {"cached_entries": [{"id": "e1", "vector": [1.0, 0.0], "tenant_id": "t1", "response": "resp"}], "query_vector": [1.0, 0.0], "tenant_id": "t1", "similarity_threshold": 0.9},
        "ALGO-VEC-SRCH-106": {"pending_queries": [{"id": "q1"}], "max_batch_size": 2, "max_latency_ms": 10.0},
        "ALGO-VEC-SRCH-107": {"components": [{"name": "c1", "size_mb": 10, "access_priority": 1}], "ram_budget_mb": 100.0},
        "ALGO-VEC-SRCH-108": {"requested_node_ids": [1], "cached_nodes": [], "page_size_bytes": 4096, "bytes_per_node": 128, "max_batch_size": 16},
        "ALGO-VEC-SRCH-109": {"current_tokens": 10.0, "max_tokens": 100.0, "refill_rate_per_sec": 10.0, "last_refill_timestamp": 0.0, "current_concurrency": 1, "max_concurrency": 10, "request_cost": 1.0, "now": 1.0},
        "ALGO-VEC-SRCH-110": {"ground_truth_topk": [[1]], "parameter_evaluations": [{"parameters": {"ef": 16}, "retrieved_topk": [[1]], "latency_ms": 1.0}], "target_recall": 0.8},
        "ALGO-VEC-TRFM-01": {"text": "unbelievable tokenization test", "vocab": {"un": 1, "believ": 2, "able": 3, "token": 4, "ization": 5, "test": 6}},
        "ALGO-VEC-TRFM-02": {"token_ids": [101, 2054, 102], "hidden_dim": 16},
        "ALGO-VEC-TRFM-03": {"token_embeddings": [[1.0, 2.0], [3.0, 4.0]], "attention_mask": [1, 1]},
        "ALGO-VEC-TRFM-04": {"token_embeddings": [[1.0, 2.0], [3.0, 4.0]]},
        "ALGO-VEC-TRFM-05": {"token_embeddings": [[1.0, 2.0], [3.0, 4.0]], "attention_mask": [1, 1]},
        "ALGO-VEC-TRFM-06": {"text": "what is vector search?", "task_type": "query"},
        "ALGO-VEC-TRFM-07": {"query_vectors": [[1.0, 0.0]], "document_vectors": [[0.9, 0.1], [0.0, 1.0]]},
        "ALGO-VEC-TRFM-08": {"candidates": [{"id": "d1", "similarity": 0.88}, {"id": "d2", "similarity": 0.5}], "positive_ids": ["d2"]},
        "ALGO-VEC-TRFM-09": {"vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6], "nested_dims": [2, 4]},
        "ALGO-VEC-TRFM-10": {"token_embeddings": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], "chunk_spans": [[0, 2], [2, 3]]},
        "ALGO-VEC-TRFM-11": {"tokens": ["token1", "token2", "token3", "token4", "token5"], "window_size": 3, "overlap": 1},
        "ALGO-VEC-TRFM-12": {"sentences": ["First sentence here.", "Second sentence follows.", "Third sentence about cars."], "sentence_embeddings": [[1.0, 0.0], [0.95, 0.05], [0.0, 1.0]]},
        "ALGO-VEC-TRFM-13": {"text": "Paragraph one.\n\nParagraph two is slightly longer.", "chunk_size": 20},
        "ALGO-VEC-TRFM-14": {"token_sequences": [[1, 2, 3], [4, 5]], "batch_size": 2},
        "ALGO-VEC-TRFM-15": {"vector": [3.0, 4.0]},
        "ALGO-VEC-TRFM-16": {"vectors": [[2.0, 4.0], [4.0, 6.0]]},
        "ALGO-VEC-TRFM-17": {"vectors": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]},
        "ALGO-VEC-TRFM-18": {"vectors": [[10.0, 1.0], [10.2, 2.0], [9.8, 0.5]], "num_components_to_remove": 1},
        "ALGO-VEC-TRFM-19": {"database_vectors": [[1.0, 2.0], [3.0, 4.0]], "query_vector": [1.0, 1.0]},
        "ALGO-VEC-TRFM-20": {"scores": [0.9, 0.5, 0.1], "method": "temperature"},
        "ALGO-VEC-TRFM-21": {"query_vectors": [[1.0, 0.0]], "candidate_vectors": [[0.9, 0.1], [0.1, 0.9]]},
        "ALGO-VEC-TRFM-22": {"source_anchors": [[1.0, 0.0], [0.0, 1.0]], "target_anchors": [[0.0, 1.0], [-1.0, 0.0]]},
        "ALGO-VEC-TRFM-23": {"vectors": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], "target_dim": 2},
        "ALGO-VEC-TRFM-24": {"vectors": [[1.0, 0.0, 2.0], [0.0, 3.0, 0.0], [4.0, 0.0, 5.0]], "n_components": 2},
        "ALGO-VEC-TRFM-25": {"vectors": [[1.0, 2.0, 3.0, 4.0]], "target_dim": 2},
        "ALGO-VEC-TRFM-26": {"vectors": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], "bottleneck_dim": 2},
        "ALGO-VEC-TRFM-27": {"vectors": [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9]], "n_components": 2, "n_neighbors": 2},
        "ALGO-VEC-TRFM-28": {"vectors": [[1.0, 2.0], [1.1, 2.1], [5.0, 5.0], [5.1, 5.1]], "n_components": 2, "perplexity": 2.0},
        "ALGO-VEC-TRFM-29": {"vector": [1.0, 2.0, 3.0, 4.0]},
        "ALGO-VEC-TRFM-30": {"batch_vectors": [[1.0, 2.0], [3.0, 4.0]], "target_dim": 1},
        "ALGO-VEC-TRFM-31": {"vector": [0.5, -0.2, 0.8], "num_bits": 16},
        "ALGO-VEC-TRFM-32": {"token_embeddings": [[0.1, 0.8, -0.3]]},
        "ALGO-VEC-TRFM-33": {"vector": [-1.0, 0.0, 0.5, 1.0], "bits": 8},
        "ALGO-VEC-TRFM-34": {"vector": [0.5, -0.2, 0.8, -0.9]},
        "ALGO-VEC-TRFM-35": {"vector": [1.0, 2.0, 3.0, 4.0], "m_subspaces": 2},
        "ALGO-VEC-TRFM-36": {"vector": [1.0, 2.0, 3.0, 4.0], "m_subspaces": 2},
        "ALGO-VEC-TRFM-37": {"vector": [1.0, 2.0, 3.0, 4.0], "num_stages": 2},
        "ALGO-VEC-TRFM-38": {"vector": [1.0, 2.0, 3.0, 4.0]},
        "ALGO-VEC-TRFM-39": {"vectors": [[0.0, 0.0], [1.0, 1.0], [5.0, 5.0], [6.0, 6.0]], "k_clusters": 2},
        "ALGO-VEC-TRFM-40": {"vectors": [[0.0, 0.0], [1.0, 1.0], [5.0, 5.0], [6.0, 6.0]], "k_clusters": 2},
        "ALGO-VEC-TRFM-41": {"vectors": [[0.0, 0.0], [1.0, 1.0], [10.0, 10.0], [11.0, 11.0]], "k_clusters": 2, "batch_size": 2},
        "ALGO-VEC-TRFM-42": {"vectors": [[0.0, 0.0], [1.0, 1.0], [5.0, 5.0], [6.0, 6.0]], "branching_factor": 2, "max_depth": 1},
        "ALGO-VEC-TRFM-43": {"query_vector": [1.0, 2.0], "codebooks": [[[0.0], [1.0]], [[0.0], [2.0]]], "candidate_pq_codes": [[1, 1], [0, 0]]},
        "ALGO-VEC-TRFM-44": {"query_vector": [1.0, 2.0, 3.0, 4.0], "candidate_codes": [[0, 1], [1, 0]], "subspace_dim": 2},
        "ALGO-VEC-TRFM-45": {"vector": [1.2, -0.8, 3.4]},
        "ALGO-VEC-TRFM-46": {"vector": [1.0, -2.5, 0.003], "dtype_target": "float16"},
        "ALGO-VEC-TRFM-47": {"tokens": ["hello", "world"], "token_embeddings": [[1.0, 0.0], [0.0, 1.0]]},
        "ALGO-VEC-TRFM-48": {"token_vectors": [[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]]},
        "ALGO-VEC-TRFM-49": {"term_weights": {"vector": 0.8, "search": 0.5}},
        "ALGO-VEC-TRFM-50": {"cache_store": {}, "text": "sample text query", "vector_to_cache": [0.1, 0.2]},
    }

    for contract in BUILTIN_ALGORITHM_CONTRACTS:
        algo_id = contract.id
        assert algo_id in test_inputs, f"Missing test input for {algo_id}"
        payload = {"inputs": test_inputs[algo_id], "parameters": {}}
        res = client.post(f"/api/v1/algos/execute/{algo_id}", json=payload)
        assert res.status_code == 200, f"Execution failed for {algo_id}: {res.text}"
        body = res.json()
        assert body["success"] is True
        assert body["meta"]["status"].lower() == "success"
        assert body["data"]["algo_id"] == algo_id


def test_api_graph_dedicated_endpoints(client):
    res_bfs = client.post("/api/v1/algos/graph/bfs", json={"adjacency_list": {"A": ["B"]}, "start_node": "A"})
    assert res_bfs.status_code == 200
    assert res_bfs.json()["data"]["total_visited"] >= 1

    res_dfs = client.post("/api/v1/algos/graph/dfs", json={"adjacency_list": {"A": ["B"]}, "start_node": "A"})
    assert res_dfs.status_code == 200
    assert res_dfs.json()["data"]["total_visited"] >= 1

    res_dijkstra = client.post("/api/v1/algos/graph/dijkstra", json={"weighted_edges": [{"source": "A", "target": "B", "weight": 2.5}], "start_node": "A", "target_node": "B"})
    assert res_dijkstra.status_code == 200
    assert res_dijkstra.json()["data"]["target_distance"] == 2.5

    res_astar = client.post("/api/v1/algos/graph/astar", json={"weighted_edges": [{"source": "A", "target": "B", "weight": 1.0}], "start_node": "A", "target_node": "B"})
    assert res_astar.status_code == 200
    assert res_astar.json()["data"]["found"] is True

    res_pr = client.post("/api/v1/algos/graph/pagerank", json={"adjacency_list": {"A": ["B"], "B": ["A"]}})
    assert res_pr.status_code == 200
    assert res_pr.json()["data"]["converged"] is True

    res_dc = client.post("/api/v1/algos/graph/degree-centrality", json={"adjacency_list": {"A": ["B"], "B": ["A"]}})
    assert res_dc.status_code == 200
    assert res_dc.json()["data"]["node_count"] == 2

    res_cc = client.post("/api/v1/algos/graph/connected-components", json={"edges": [["A", "B"], ["C", "D"]]})
    assert res_cc.status_code == 200
    assert res_cc.json()["data"]["component_count"] == 2

    res_scc = client.post("/api/v1/algos/graph/tarjan-scc", json={"adjacency_list": {"A": ["B"], "B": ["A"]}})
    assert res_scc.status_code == 200
    assert res_scc.json()["data"]["scc_count"] == 1

    res_sub = client.post("/api/v1/algos/graph/subgraph-match", json={"target_graph": {"1": ["2"], "2": []}, "pattern_graph": {"A": ["B"], "B": []}})
    assert res_sub.status_code == 200
    assert res_sub.json()["data"]["match_count"] >= 1


def test_api_vector_search_dedicated_endpoints(client):
    res_gemm = client.post("/api/v1/algos/vector-search/gemm", json={"database_vectors": [[1.0, 0.0], [0.0, 1.0]], "query_vectors": [[1.0, 0.0]], "k": 2})
    assert res_gemm.status_code == 200
    assert res_gemm.json()["data"]["total_queries"] == 1

    res_simd = client.post("/api/v1/algos/vector-search/simd-dist", json={"vector_a": [1.0, 2.0], "vector_b": [1.0, 3.0], "metric": "l2"})
    assert res_simd.status_code == 200
    assert res_simd.json()["data"]["metric"] == "l2"

    res_ivf = client.post("/api/v1/algos/vector-search/ivf", json={"vectors": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]], "query": [1.0, 0.0], "k": 2, "num_clusters": 2})
    assert res_ivf.status_code == 200
    assert len(res_ivf.json()["data"]["matches"]) == 2
