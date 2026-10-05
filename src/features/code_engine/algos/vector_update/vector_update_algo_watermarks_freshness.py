"""
================================================================================
ALGORITHM BLUEPRINT: WATERMARKS AND FRESHNESS TRACKING (ALGO-VEC-UPD-128)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Monitors event-time watermarks across pipeline stages, computes end-to-end
   data freshness lag, and alerts on SLO breaches.
================================================================================
"""

import time
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoWatermarksFreshness:
    """
    --- contract:
      id: ALGO-VEC-UPD-128
      name: VectorUpdateAlgoWatermarksFreshness
      category: update
      complexity: O(S)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        stage_watermarks: dict[str, float]
        max_allowed_lag_seconds: float
        current_time: Optional[float]
      output_schema:
        oldest_watermark: float
        freshness_lag_seconds: float
        slo_satisfied: bool
        bottleneck_stage: str
    ---
    """

    @classmethod
    def evaluate(
        cls,
        stage_watermarks: Dict[str, float],
        max_allowed_lag_seconds: float = 300.0,
        current_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        now = current_time if current_time is not None else time.time()
        if not stage_watermarks:
            return {
                "oldest_watermark": now,
                "freshness_lag_seconds": 0.0,
                "slo_satisfied": True,
                "bottleneck_stage": "NONE",
            }

        sorted_stages = sorted(stage_watermarks.items(), key=lambda x: x[1])
        bottleneck, oldest_wm = sorted_stages[0]
        lag = max(0.0, now - oldest_wm)

        return {
            "oldest_watermark": oldest_wm,
            "freshness_lag_seconds": round(lag, 2),
            "slo_satisfied": lag <= max_allowed_lag_seconds,
            "bottleneck_stage": bottleneck,
        }
