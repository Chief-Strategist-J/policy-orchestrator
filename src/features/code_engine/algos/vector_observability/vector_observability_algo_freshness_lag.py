"""
================================================================================
ALGORITHM BLUEPRINT: INGEST-TO-SEARCHABLE FRESHNESS LAG MONITOR (ALGO-VEC-OBS-182)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates the end-to-end elapsed time between source mutation creation timestamp
   and searchable index visibility, tracking percentile lags for updates and deletes.

2. MATHEMATICAL FORMULATION:
   FreshnessLag_i = IndexVisibilityTimestamp_i - SourceMutationTimestamp_i
   SLO Violation = p99_Lag > max_allowed_freshness_seconds
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoFreshnessLag:
    """
    --- contract:
      id: ALGO-VEC-OBS-182
      name: VectorObservabilityAlgoFreshnessLag
      category: observability
      complexity: O(N log N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        mutation_events: list[dict[str, Any]]
        max_allowed_lag_seconds: float
      output_schema:
        mean_lag_seconds: float
        p50_lag_seconds: float
        p95_lag_seconds: float
        p99_lag_seconds: float
        max_lag_seconds: float
        is_freshness_slo_violated: bool
        stalled_mutation_count: int
    ---
    """

    @classmethod
    def evaluate(
        cls,
        mutation_events: List[Dict[str, Any]],
        max_allowed_lag_seconds: float = 60.0,
    ) -> Dict[str, Any]:
        if not mutation_events:
            return {
                "mean_lag_seconds": 0.0,
                "p50_lag_seconds": 0.0,
                "p95_lag_seconds": 0.0,
                "p99_lag_seconds": 0.0,
                "max_lag_seconds": 0.0,
                "is_freshness_slo_violated": False,
                "stalled_mutation_count": 0,
            }

        lags: List[float] = []
        stalled = 0

        for ev in mutation_events:
            src_ts = float(ev.get("source_timestamp", 0.0))
            vis_ts = float(ev.get("visible_timestamp", src_ts))
            lag = max(0.0, vis_ts - src_ts)
            lags.append(lag)
            if lag > max_allowed_lag_seconds:
                stalled += 1

        sorted_lags = sorted(lags)
        n = len(sorted_lags)

        def pct(q: float) -> float:
            idx = int(q * (n - 1))
            return sorted_lags[min(n - 1, max(0, idx))]

        mean_val = sum(sorted_lags) / float(n)
        p50 = pct(0.50)
        p95 = pct(0.95)
        p99 = pct(0.99)
        max_val = sorted_lags[-1]

        violated = (p99 > max_allowed_lag_seconds) or (stalled > 0)

        return {
            "mean_lag_seconds": round(mean_val, 2),
            "p50_lag_seconds": round(p50, 2),
            "p95_lag_seconds": round(p95, 2),
            "p99_lag_seconds": round(p99, 2),
            "max_lag_seconds": round(max_val, 2),
            "is_freshness_slo_violated": violated,
            "stalled_mutation_count": stalled,
        }
