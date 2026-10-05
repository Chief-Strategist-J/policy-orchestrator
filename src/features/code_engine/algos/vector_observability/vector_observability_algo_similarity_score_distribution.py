"""
================================================================================
ALGORITHM BLUEPRINT: SIMILARITY SCORE DISTRIBUTION MONITOR (ALGO-VEC-OBS-171)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Monitors the percentile distribution (p10, p50, p90, p99) and spread of top-1/top-k
   retrieval similarity scores to detect score collapse, anisotropy, or model degradation.

2. MATHEMATICAL FORMULATION:
   Spread = p90 - p10
   Anisotropy Warning = (spread < min_spread_threshold) or (mean_top1 < baseline_threshold)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoSimilarityScoreDistribution:
    """
    --- contract:
      id: ALGO-VEC-OBS-171
      name: VectorObservabilityAlgoSimilarityScoreDistribution
      category: observability
      complexity: O(N log N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        top1_scores: list[float]
        baseline_mean_score: Optional[float]
        min_spread_threshold: float
      output_schema:
        mean_score: float
        p10: float
        p50: float
        p90: float
        p99: float
        score_spread: float
        is_score_collapse_detected: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        top1_scores: List[float],
        baseline_mean_score: Optional[float] = None,
        min_spread_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        if not top1_scores:
            return {
                "mean_score": 0.0,
                "p10": 0.0,
                "p50": 0.0,
                "p90": 0.0,
                "p99": 0.0,
                "score_spread": 0.0,
                "is_score_collapse_detected": False,
            }

        sorted_scores = sorted(top1_scores)
        n = len(sorted_scores)

        def get_percentile(p: float) -> float:
            idx = int(p * (n - 1))
            return sorted_scores[min(n - 1, max(0, idx))]

        p10 = get_percentile(0.10)
        p50 = get_percentile(0.50)
        p90 = get_percentile(0.90)
        p99 = get_percentile(0.99)
        mean_val = sum(sorted_scores) / float(n)
        spread = p90 - p10

        collapse = spread < min_spread_threshold
        if baseline_mean_score is not None and baseline_mean_score > 0:
            if (baseline_mean_score - mean_val) > 0.15:
                collapse = True

        return {
            "mean_score": round(mean_val, 4),
            "p10": round(p10, 4),
            "p50": round(p50, 4),
            "p90": round(p90, 4),
            "p99": round(p99, 4),
            "score_spread": round(spread, 4),
            "is_score_collapse_detected": collapse,
        }
