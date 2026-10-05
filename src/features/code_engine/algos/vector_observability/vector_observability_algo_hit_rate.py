"""
================================================================================
ALGORITHM BLUEPRINT: HIT RATE / SUCCESS@K (ALGO-VEC-OBS-161)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates binary hit rate (Success@k): proportion of queries with at least one
   relevant document appearing in the top-k retrieved list.

2. MATHEMATICAL FORMULATION:
   Hit_i = 1 if |Retrieved_i,k ∩ Relevant_i| >= 1 else 0
   HitRate@k = (1/N) * sum(Hit_i)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoHitRate:
    """
    --- contract:
      id: ALGO-VEC-OBS-161
      name: VectorObservabilityAlgoHitRate
      category: observability
      complexity: O(N * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        retrieved_ids: list[list[str]]
        relevant_ids: list[list[str]]
        k: int
      output_schema:
        hit_rate_at_k: float
        hit_count: int
        total_queries: int
        failed_query_indices: list[int]
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
                "hit_rate_at_k": 0.0,
                "hit_count": 0,
                "total_queries": 0,
                "failed_query_indices": [],
            }

        num_queries = min(len(retrieved_ids), len(relevant_ids))
        hits = 0
        failed_indices: List[int] = []

        for i in range(num_queries):
            ret_k = set(retrieved_ids[i][:k])
            rel_set = set(relevant_ids[i])
            if ret_k.intersection(rel_set):
                hits += 1
            else:
                failed_indices.append(i)

        hit_rate = hits / float(num_queries) if num_queries > 0 else 0.0

        return {
            "hit_rate_at_k": round(hit_rate, 4),
            "hit_count": hits,
            "total_queries": num_queries,
            "failed_query_indices": failed_indices,
        }
