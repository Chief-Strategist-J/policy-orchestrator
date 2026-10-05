"""
================================================================================
ALGORITHM BLUEPRINT: ONLINE IMPLICIT FEEDBACK MONITOR (ALGO-VEC-OBS-165)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Aggregates user interaction telemetry (clicks, dwell time, copies, thumbs down)
   with position-bias de-biasing to evaluate live retrieval quality.

2. MATHEMATICAL FORMULATION:
   Position-Discounted CTR = sum(click_i / log2(pos_i + 1))
   QualityScore = (w_click * clicks + w_dwell * dwell_secs + w_copy * copies - w_neg * thumbs_down)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoOnlineImplicitFeedback:
    """
    --- contract:
      id: ALGO-VEC-OBS-165
      name: VectorObservabilityAlgoOnlineImplicitFeedback
      category: observability
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        events: list[dict[str, Any]]
        min_dwell_threshold_seconds: float
      output_schema:
        total_queries: int
        mean_click_through_rate: float
        debiased_ctr: float
        negative_feedback_rate: float
        satisfaction_score: float
    ---
    """

    @classmethod
    def evaluate(
        cls,
        events: List[Dict[str, Any]],
        min_dwell_threshold_seconds: float = 5.0,
    ) -> Dict[str, Any]:
        if not events:
            return {
                "total_queries": 0,
                "mean_click_through_rate": 0.0,
                "debiased_ctr": 0.0,
                "negative_feedback_rate": 0.0,
                "satisfaction_score": 0.0,
            }

        total_q = len(events)
        click_count = 0
        neg_count = 0
        debiased_sum = 0.0
        sat_scores = 0.0

        for ev in events:
            clicked = bool(ev.get("clicked", False))
            pos = int(ev.get("clicked_position", 1))
            dwell = float(ev.get("dwell_time_seconds", 0.0))
            is_neg = bool(ev.get("thumbs_down", False)) or bool(ev.get("rephrased_immediately", False))
            copied = bool(ev.get("copied_snippet", False))

            if clicked:
                click_count += 1
                pos_weight = 1.0 / math.log2(max(pos, 1) + 1.0)
                debiased_sum += pos_weight

            if is_neg:
                neg_count += 1

            score = 0.0
            if clicked:
                score += 0.4
            if dwell >= min_dwell_threshold_seconds:
                score += 0.3
            if copied:
                score += 0.3
            if is_neg:
                score -= 0.5
            sat_scores += max(0.0, min(1.0, score))

        mean_ctr = click_count / float(total_q)
        debiased_ctr = debiased_sum / float(total_q)
        neg_rate = neg_count / float(total_q)
        satisfaction = sat_scores / float(total_q)

        return {
            "total_queries": total_q,
            "mean_click_through_rate": round(mean_ctr, 4),
            "debiased_ctr": round(debiased_ctr, 4),
            "negative_feedback_rate": round(neg_rate, 4),
            "satisfaction_score": round(satisfaction, 4),
        }
