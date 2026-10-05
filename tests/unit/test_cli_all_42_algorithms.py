import json
import subprocess
import pytest
from src.features.code_engine.registry.algorithm_catalog import BUILTIN_ALGORITHM_CONTRACTS


def test_cli_all_42_algorithms_execute():
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
        "ALGO-VEC-SRCH-62": {"vectors": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], "query": [1.0, 2.0], "k": 1, "num_clusters": 2, "subspaces": 2, "codebook_size": 2},
        "ALGO-VEC-SRCH-63": {"database_vectors": [[1.0, 2.0], [3.0, 4.0]], "sample_queries": [[1.0, 2.0]], "k": 1, "num_clusters": 2},
        "ALGO-VEC-SRCH-64": {"vectors": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], "query": [1.0, 2.0], "k": 1, "codebook_k1": 2, "codebook_k2": 2},
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
    }

    assert len(BUILTIN_ALGORITHM_CONTRACTS) == 76

    for contract in BUILTIN_ALGORITHM_CONTRACTS:
        algo_id = contract.id
        inp_json = json.dumps(test_inputs[algo_id])
        cmd = [
            "python3",
            "-m",
            "src.api.cli.main",
            "algo",
            "execute",
            "--id",
            algo_id,
            "--input",
            inp_json,
            "--json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"CLI execution failed for {algo_id}: {result.stderr}"
        parsed = json.loads(result.stdout)
        assert "algo_id" in parsed
        assert parsed["algo_id"] == algo_id
        assert "result" in parsed
