"""
================================================================================
ALGORITHM BLUEPRINT: GROUND-TRUTH SAMPLING / SHADOW BRUTE FORCE (ALGO-VEC-OBS-157)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Asynchronously evaluates production queries against shadow brute-force snapshots
   to track continuous live recall drift without interfering with serving latencies.

2. MATHEMATICAL FORMULATION:
   Sample rate s in (0, 1]. For sampled queries, compute exact Euclidean or Cosine top-k
   against snapshot vectors, then compare intersection with live production results.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoGroundTruthSampling:
    """
    --- contract:
      id: ALGO-VEC-OBS-157
      name: VectorObservabilityAlgoGroundTruthSampling
      category: observability
      complexity: O(S * N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        sampled_queries: list[dict[str, Any]]
        snapshot_vectors: list[dict[str, Any]]
        k: int
        metric: str
      output_schema:
        sample_count: int
        live_mean_recall: float
        sampled_results: list[dict[str, Any]]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        sampled_queries: List[Dict[str, Any]],
        snapshot_vectors: List[Dict[str, Any]],
        k: int = 5,
        metric: str = "cosine",
    ) -> Dict[str, Any]:
        if not sampled_queries or not snapshot_vectors or k <= 0:
            return {
                "sample_count": 0,
                "live_mean_recall": 0.0,
                "sampled_results": [],
            }

        def compute_sim(v1: List[float], v2: List[float]) -> float:
            if metric == "l2":
                return -math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            if norm1 == 0.0 or norm2 == 0.0:
                return 0.0
            return dot / (norm1 * norm2)

        results: List[Dict[str, Any]] = []
        recalls: List[float] = []

        for q in sampled_queries:
            q_id = q.get("query_id", "")
            q_vec = q.get("query_vector", [])
            live_retrieved_ids = set(q.get("live_retrieved_ids", [])[:k])

            scored = []
            for item in snapshot_vectors:
                doc_id = item.get("id", "")
                doc_vec = item.get("vector", [])
                if len(doc_vec) == len(q_vec) and doc_vec:
                    score = compute_sim(q_vec, doc_vec)
                    scored.append((score, doc_id))

            scored.sort(key=lambda x: x[0], reverse=True)
            exact_top_ids = [doc_id for _, doc_id in scored[:k]]
            exact_set = set(exact_top_ids)

            denom = min(k, len(exact_set)) if exact_set else k
            recall_val = len(live_retrieved_ids.intersection(exact_set)) / float(denom) if denom > 0 else 0.0
            recalls.append(recall_val)

            results.append({
                "query_id": q_id,
                "live_retrieved_ids": list(live_retrieved_ids),
                "exact_ground_truth_ids": exact_top_ids,
                "recall_at_k": round(recall_val, 4),
            })

        mean_recall = sum(recalls) / float(len(recalls)) if recalls else 0.0

        return {
            "sample_count": len(results),
            "live_mean_recall": round(mean_recall, 4),
            "sampled_results": results,
        }
