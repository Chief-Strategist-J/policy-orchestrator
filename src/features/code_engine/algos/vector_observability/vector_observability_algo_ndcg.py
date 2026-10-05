"""
================================================================================
ALGORITHM BLUEPRINT: NORMALIZED DISCOUNTED CUMULATIVE GAIN (nDCG@K) (ALGO-VEC-OBS-160)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Evaluates graded relevance ranking quality using position-discounted logarithmic gains.

2. MATHEMATICAL FORMULATION:
   DCG@k = sum_{i=1}^k (2^{rel_i} - 1) / log2(i + 1)
   IDCG@k = DCG@k of ideally sorted ground-truth relevant judgments
   nDCG@k = DCG@k / IDCG@k (with nDCG = 1.0 when IDCG = 0)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoNdcg:
    """
    --- contract:
      id: ALGO-VEC-OBS-160
      name: VectorObservabilityAlgoNdcg
      category: observability
      complexity: O(N * k * log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        retrieved_ids: list[list[str]]
        ground_truth_relevance: list[dict[str, float]]
        k: int
      output_schema:
        mean_ndcg_at_k: float
        per_query_ndcg: list[float]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        retrieved_ids: List[List[str]],
        ground_truth_relevance: List[Dict[str, float]],
        k: int = 10,
    ) -> Dict[str, Any]:
        if not retrieved_ids or not ground_truth_relevance or k <= 0:
            return {
                "mean_ndcg_at_k": 0.0,
                "per_query_ndcg": [],
            }

        def compute_dcg(relevances: List[float]) -> float:
            score = 0.0
            for i, rel in enumerate(relevances[:k], start=1):
                gain = (2.0 ** rel) - 1.0
                discount = math.log2(i + 1.0)
                score += gain / discount
            return score

        num_queries = min(len(retrieved_ids), len(ground_truth_relevance))
        ndcgs: List[float] = []

        for i in range(num_queries):
            ret_k = retrieved_ids[i][:k]
            rel_map = ground_truth_relevance[i]

            actual_rels = [rel_map.get(doc_id, 0.0) for doc_id in ret_k]
            dcg = compute_dcg(actual_rels)

            ideal_rels = sorted(rel_map.values(), reverse=True)[:k]
            idcg = compute_dcg(ideal_rels)

            if idcg == 0.0:
                ndcg_val = 1.0 if dcg == 0.0 else 0.0
            else:
                ndcg_val = dcg / idcg

            ndcgs.append(ndcg_val)

        mean_ndcg = sum(ndcgs) / float(len(ndcgs)) if ndcgs else 0.0

        return {
            "mean_ndcg_at_k": round(mean_ndcg, 4),
            "per_query_ndcg": [round(s, 4) for s in ndcgs],
        }
