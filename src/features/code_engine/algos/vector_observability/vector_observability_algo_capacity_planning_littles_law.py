"""
================================================================================
ALGORITHM BLUEPRINT: CAPACITY PLANNING WITH LITTLE'S LAW (ALGO-VEC-OBS-186)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Sizes thread worker pools, connection pools, and replica counts by relating
   steady-state concurrency L, arrival throughput lambda, and service latency W.

2. MATHEMATICAL FORMULATION:
   L = lambda * W
   RequiredCapacity = (lambda_peak * W_p99) * (1.0 + headroom_buffer_ratio)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoCapacityPlanningLittlesLaw:
    """
    --- contract:
      id: ALGO-VEC-OBS-186
      name: VectorObservabilityAlgoCapacityPlanningLittlesLaw
      category: observability
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        arrival_rate_qps: float
        mean_latency_seconds: float
        p99_latency_seconds: float
        headroom_ratio: float
        max_threads_per_replica: int
      output_schema:
        average_in_flight_concurrency: float
        peak_concurrency_with_headroom: float
        recommended_worker_threads: int
        recommended_replica_count: int
    ---
    """

    @classmethod
    def evaluate(
        cls,
        arrival_rate_qps: float = 200.0,
        mean_latency_seconds: float = 0.05,
        p99_latency_seconds: float = 0.15,
        headroom_ratio: float = 0.40,
        max_threads_per_replica: int = 32,
    ) -> Dict[str, Any]:
        l_avg = arrival_rate_qps * mean_latency_seconds
        l_peak = arrival_rate_qps * p99_latency_seconds * (1.0 + headroom_ratio)

        recommended_threads = max(1, int(math.ceil(l_peak)))
        threads_per_rep = max(1, max_threads_per_replica)
        recommended_replicas = max(1, int(math.ceil(float(recommended_threads) / float(threads_per_rep))))

        return {
            "average_in_flight_concurrency": round(l_avg, 2),
            "peak_concurrency_with_headroom": round(l_peak, 2),
            "recommended_worker_threads": recommended_threads,
            "recommended_replica_count": recommended_replicas,
        }
