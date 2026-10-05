"""
================================================================================
ALGORITHM BLUEPRINT: RECALL@K AGAINST EXACT GROUND TRUTH (ALGO-VEC-OBS-156)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes recall@k metric comparing approximate nearest neighbor index results
   against brute force exact ground truth nearest neighbors.

2. MATHEMATICAL FORMULATION:
   Recall@k = |Returned_k ∩ GroundTruth_k| / k
   For N queries: MeanRecall@k = (1/N) * sum(Recall_i@k)
   Percentiles (p5, p50, p95) and segmented recall by tenant/filter.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoRecallAtK:
    """
    --- contract:
      id: ALGO-VEC-OBS-156
      name: VectorObservabilityAlgoRecallAtK
      category: observability
      complexity: O(N * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        retrieved_ids: list[list[str]]
        ground_truth_ids: list[list[str]]
        k: int
        segments: Optional[list[str]]
      output_schema:
        mean_recall_at_k: float
        worst_5th_percentile_recall: float
        per_query_recall: list[float]
        segmented_recall: dict[str, float]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        retrieved_ids: List[List[str]],
        ground_truth_ids: List[List[str]],
        k: int = 10,
        segments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not retrieved_ids or not ground_truth_ids or k <= 0:
            return {
                "mean_recall_at_k": 0.0,
                "worst_5th_percentile_recall": 0.0,
                "per_query_recall": [],
                "segmented_recall": {},
            }

        num_queries = min(len(retrieved_ids), len(ground_truth_ids))
        recalls: List[float] = []
        seg_map: Dict[str, List[float]] = {}

        for i in range(num_queries):
            ret_k = set(retrieved_ids[i][:k])
            gt_k = set(ground_truth_ids[i][:k])
            denom = min(k, len(gt_k)) if gt_k else k
            recall_val = len(ret_k.intersection(gt_k)) / float(denom) if denom > 0 else 0.0
            recalls.append(recall_val)

            if segments and i < len(segments):
                seg = segments[i]
                if seg not in seg_map:
                    seg_map[seg] = []
                seg_map[seg].append(recall_val)

        sorted_recalls = sorted(recalls)
        p5_idx = int(0.05 * len(sorted_recalls))
        worst_5p = sorted_recalls[p5_idx] if sorted_recalls else 0.0
        mean_recall = sum(recalls) / float(len(recalls)) if recalls else 0.0

        segmented_avg: Dict[str, float] = {
            s: sum(vals) / float(len(vals)) for s, vals in seg_map.items() if vals
        }

        return {
            "mean_recall_at_k": round(mean_recall, 4),
            "worst_5th_percentile_recall": round(worst_5p, 4),
            "per_query_recall": [round(r, 4) for r in recalls],
            "segmented_recall": {k_s: round(v_s, 4) for k_s, v_s in segmented_avg.items()},
        }
