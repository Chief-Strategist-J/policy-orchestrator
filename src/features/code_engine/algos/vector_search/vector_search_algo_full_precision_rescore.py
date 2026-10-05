"""
================================================================================
ALGORITHM BLUEPRINT: FULL-PRECISION RE-SCORING (ALGO-VEC-SRCH-93)
================================================================================

Full-precision re-scoring refines an initial candidate set retrieved via fast
approximate or quantized methods (e.g. SQ8, PQ, IVFPQ, binary) by scoring candidate
vectors against the query using full FP32 precision. This eliminates quantization
distortion and rank inversions on the short candidate list while preserving sub-millisecond
throughput on the full corpus.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoFullPrecisionRescore:
    """
    --- contract:
      id: ALGO-VEC-SRCH-93
      name: VectorSearchAlgoFullPrecisionRescore
      category: vector
      complexity: O(|candidates| * D + k log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        candidate_ids: list[int]
        full_precision_vectors: list[list[float]]
        query_vector: list[float]
        metric: str
        top_k: int
      output_schema:
        candidates_rescored: int
        top_k: int
        metric: str
        rescored_matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def rescore(
        candidate_ids: List[int],
        full_precision_vectors: List[List[float]],
        query_vector: List[float],
        metric: str = "l2",
        top_k: int = 5,
    ) -> Dict[str, Any]:
        if not candidate_ids or not full_precision_vectors or not query_vector:
            return {
                "candidates_rescored": 0,
                "top_k": top_k,
                "metric": metric,
                "rescored_matches": [],
            }

        dim = len(query_vector)
        scored: List[Dict[str, Any]] = []

        for cid in candidate_ids:
            if cid < 0 or cid >= len(full_precision_vectors):
                continue
            vec = full_precision_vectors[cid]

            if metric == "cosine":
                dot = sum(vec[d] * query_vector[d] for d in range(min(dim, len(vec))))
                norm_v = math.sqrt(sum(v ** 2 for v in vec))
                norm_q = math.sqrt(sum(q ** 2 for q in query_vector))
                sim = dot / (norm_v * norm_q) if norm_v * norm_q > 1e-12 else 0.0
                scored.append({"id": cid, "score": round(sim, 6)})
            else:
                dist_sq = sum((vec[d] - query_vector[d]) ** 2 for d in range(min(dim, len(vec))))
                scored.append({"id": cid, "distance": round(math.sqrt(dist_sq), 6)})

        if metric == "cosine":
            scored.sort(key=lambda x: x["score"], reverse=True)
        else:
            scored.sort(key=lambda x: x["distance"])

        return {
            "candidates_rescored": len(scored),
            "top_k": top_k,
            "metric": metric,
            "rescored_matches": scored[:top_k],
        }
