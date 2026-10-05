"""
================================================================================
ALGORITHM BLUEPRINT: SCORE-NORMALIZED CONVEX FUSION (ALGO-VEC-SRCH-88)
================================================================================

Score-normalized convex combination fuses multiple retrieval score channels by
first normalizing scores into a shared standard range (min-max [0, 1] or z-score)
and computing a convex linear combination Σ [ w_i · Score_normalized_i(d) ] where
Σ w_i = 1.0. This allows blending disparate score spaces (e.g. cosine similarity,
BM25, BM25F, or neural re-rankers) with explicit control over channel weighting.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoConvexScoreFusion:
    """
    --- contract:
      id: ALGO-VEC-SRCH-88
      name: ConvexScoreFusion
      category: vector
      complexity: O(M * L + N log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        score_lists: list[list[dict[str, any]]]
        weights: list[float]
        norm_method: str
        top_k: int
      output_schema:
        channel_count: int
        total_unique_items: int
        fused_results: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _normalize(scores: List[float], method: str = "minmax") -> List[float]:
        if not scores:
            return []
        if method == "zscore":
            mean_s = sum(scores) / len(scores)
            var = sum((s - mean_s) ** 2 for s in scores) / len(scores)
            std_s = math.sqrt(var) if var > 1e-12 else 1.0
            return [(s - mean_s) / std_s for s in scores]

        min_s = min(scores)
        max_s = max(scores)
        span = max_s - min_s if max_s > min_s else 1.0
        return [(s - min_s) / span for s in scores]

    @staticmethod
    def fuse(
        score_lists: List[List[Dict[str, Any]]],
        weights: List[float],
        norm_method: str = "minmax",
        top_k: int = 5,
    ) -> Dict[str, Any]:
        if not score_lists or not weights:
            return {"channel_count": 0, "total_unique_items": 0, "fused_results": []}

        total_weight = sum(weights)
        if total_weight <= 0:
            weights = [1.0 / len(score_lists)] * len(score_lists)
        else:
            weights = [w / total_weight for w in weights]

        item_channel_scores: Dict[Any, Dict[int, float]] = {}

        for ch_idx, result_list in enumerate(score_lists):
            raw_scores = [float(item.get("score", 0.0)) for item in result_list]
            normalized = VectorSearchAlgoConvexScoreFusion._normalize(raw_scores, method=norm_method)

            for item, norm_score in zip(result_list, normalized):
                item_id = item.get("id")
                if item_id not in item_channel_scores:
                    item_channel_scores[item_id] = {}
                item_channel_scores[item_id][ch_idx] = norm_score

        fused: List[Dict[str, Any]] = []
        for item_id, channel_map in item_channel_scores.items():
            combined_score = 0.0
            for ch_idx, w in enumerate(weights):
                s = channel_map.get(ch_idx, 0.0)
                combined_score += w * s

            fused.append({
                "id": item_id,
                "fused_score": round(combined_score, 6),
                "channel_breakdown": {str(k): round(v, 4) for k, v in channel_map.items()},
            })

        fused.sort(key=lambda x: x["fused_score"], reverse=True)

        return {
            "channel_count": len(score_lists),
            "total_unique_items": len(fused),
            "fused_results": fused[:top_k],
        }
