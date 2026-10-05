"""
================================================================================
ALGORITHM BLUEPRINT: PRECISION@K RETRIEVAL EVALUATION (ALGO-VEC-OBS-158)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Measures fraction of retrieved top-k passages that are verified relevant to query.

2. MATHEMATICAL FORMULATION:
   Precision@k = (Count of relevant documents in top k) / k
   MeanPrecision@k = (1/N) * sum(Precision_i@k)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoPrecisionAtK:
    """
    --- contract:
      id: ALGO-VEC-OBS-158
      name: VectorObservabilityAlgoPrecisionAtK
      category: observability
      complexity: O(N * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        retrieved_ids: list[list[str]]
        relevant_ids: list[list[str]]
        k: int
      output_schema:
        mean_precision_at_k: float
        per_query_precision: list[float]
        zero_precision_query_ratio: float
    ---
    """

    @classmethod
    def evaluate(
        cls,
        retrieved_ids: List[List[str]],
        relevant_ids: List[List[str]],
        k: int = 5,
    ) -> Dict[str, Any]:
        if not retrieved_ids or not relevant_ids or k <= 0:
            return {
                "mean_precision_at_k": 0.0,
                "per_query_precision": [],
                "zero_precision_query_ratio": 0.0,
            }

        num_queries = min(len(retrieved_ids), len(relevant_ids))
        precisions: List[float] = []

        for i in range(num_queries):
            ret_k = retrieved_ids[i][:k]
            rel_set = set(relevant_ids[i])
            matched = sum(1 for r_id in ret_k if r_id in rel_set)
            precisions.append(matched / float(k))

        mean_p = sum(precisions) / float(len(precisions)) if precisions else 0.0
        zero_count = sum(1 for p in precisions if p == 0.0)
        zero_ratio = zero_count / float(len(precisions)) if precisions else 0.0

        return {
            "mean_precision_at_k": round(mean_p, 4),
            "per_query_precision": [round(p, 4) for p in precisions],
            "zero_precision_query_ratio": round(zero_ratio, 4),
        }
