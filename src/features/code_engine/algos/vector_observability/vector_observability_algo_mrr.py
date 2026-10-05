"""
================================================================================
ALGORITHM BLUEPRINT: MEAN RECIPROCAL RANK (MRR) (ALGO-VEC-OBS-159)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates Mean Reciprocal Rank (MRR@k) across a corpus of queries, measuring
   the average inverse rank of the first relevant result.

2. MATHEMATICAL FORMULATION:
   ReciprocalRank = 1 / rank_of_first_relevant_item, or 0 if not found within k.
   MRR@k = (1/N) * sum(ReciprocalRank_i)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoMrr:
    """
    --- contract:
      id: ALGO-VEC-OBS-159
      name: VectorObservabilityAlgoMrr
      category: observability
      complexity: O(N * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        retrieved_ids: list[list[str]]
        relevant_ids: list[list[str]]
        k: int
      output_schema:
        mrr_score: float
        reciprocal_ranks: list[float]
        first_hit_ranks: list[Optional[int]]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        retrieved_ids: List[List[str]],
        relevant_ids: List[List[str]],
        k: int = 10,
    ) -> Dict[str, Any]:
        if not retrieved_ids or not relevant_ids or k <= 0:
            return {
                "mrr_score": 0.0,
                "reciprocal_ranks": [],
                "first_hit_ranks": [],
            }

        num_queries = min(len(retrieved_ids), len(relevant_ids))
        rrs: List[float] = []
        hit_ranks: List[Optional[int]] = []

        for i in range(num_queries):
            ret_k = retrieved_ids[i][:k]
            rel_set = set(relevant_ids[i])
            found_rank: Optional[int] = None
            for rank_idx, doc_id in enumerate(ret_k, start=1):
                if doc_id in rel_set:
                    found_rank = rank_idx
                    break

            if found_rank is not None:
                hit_ranks.append(found_rank)
                rrs.append(1.0 / float(found_rank))
            else:
                hit_ranks.append(None)
                rrs.append(0.0)

        mrr = sum(rrs) / float(len(rrs)) if rrs else 0.0

        return {
            "mrr_score": round(mrr, 4),
            "reciprocal_ranks": [round(r, 4) for r in rrs],
            "first_hit_ranks": hit_ranks,
        }
