"""
================================================================================
ALGORITHM BLUEPRINT: LATENCY HISTOGRAMS AND PERCENTILES (ALGO-VEC-OBS-178)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Aggregates pipeline duration telemetry into histogram buckets and extracts
   robust p50, p90, p95, p99, p99.9 latency percentiles across retrieval stages
   (embedding, ANN search, filter, rerank).

2. MATHEMATICAL FORMULATION:
   Percentile p_q = Value at sorted rank floor(q * (N - 1))
   Bucket Assignment: Count[b] for val in [threshold_{b-1}, threshold_b)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoLatencyHistograms:
    """
    --- contract:
      id: ALGO-VEC-OBS-178
      name: VectorObservabilityAlgoLatencyHistograms
      category: observability
      complexity: O(N log N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        latencies_ms: list[float]
        stage_latencies_ms: Optional[dict[str, list[float]]]
        bucket_thresholds_ms: Optional[list[float]]
      output_schema:
        count: int
        p50_ms: float
        p90_ms: float
        p95_ms: float
        p99_ms: float
        p999_ms: float
        histogram_buckets: dict[str, int]
        stage_p95_breakdown: dict[str, float]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        latencies_ms: List[float],
        stage_latencies_ms: Optional[Dict[str, List[float]]] = None,
        bucket_thresholds_ms: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not latencies_ms:
            return {
                "count": 0,
                "p50_ms": 0.0,
                "p90_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "p999_ms": 0.0,
                "histogram_buckets": {},
                "stage_p95_breakdown": {},
            }

        sorted_lat = sorted(latencies_ms)
        n = len(sorted_lat)

        def percentile(q: float) -> float:
            idx = int(q * (n - 1))
            return sorted_lat[min(n - 1, max(0, idx))]

        p50 = percentile(0.50)
        p90 = percentile(0.90)
        p95 = percentile(0.95)
        p99 = percentile(0.99)
        p999 = percentile(0.999)

        buckets = bucket_thresholds_ms or [5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0]
        sorted_buckets = sorted(buckets)
        hist: Dict[str, int] = {}
        for b in sorted_buckets:
            hist[f"le_{b}ms"] = 0
        hist["le_inf"] = 0

        for val in sorted_lat:
            placed = False
            for b in sorted_buckets:
                if val <= b:
                    hist[f"le_{b}ms"] += 1
                    placed = True
                    break
            if not placed:
                hist["le_inf"] += 1

        stage_p95: Dict[str, float] = {}
        if stage_latencies_ms:
            for stage, vals in stage_latencies_ms.items():
                if vals:
                    s_sorted = sorted(vals)
                    s_idx = int(0.95 * (len(s_sorted) - 1))
                    stage_p95[stage] = round(s_sorted[min(len(s_sorted) - 1, max(0, s_idx))], 2)

        return {
            "count": n,
            "p50_ms": round(p50, 2),
            "p90_ms": round(p90, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
            "p999_ms": round(p999, 2),
            "histogram_buckets": hist,
            "stage_p95_breakdown": stage_p95,
        }
