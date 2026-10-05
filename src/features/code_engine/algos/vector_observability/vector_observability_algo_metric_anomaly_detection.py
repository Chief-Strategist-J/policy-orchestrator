"""
================================================================================
ALGORITHM BLUEPRINT: METRIC STREAM ANOMALY DETECTOR (EWMA & CUSUM) (ALGO-VEC-OBS-189)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Detects sudden and creeping anomalies in streaming metric series (latency, top-1 score,
   error rate) using Exponentially Weighted Moving Average (EWMA) and CUSUM change-point filters.

2. MATHEMATICAL FORMULATION:
   EWMA_t = alpha * x_t + (1 - alpha) * EWMA_{t-1}
   Var_t = (1 - alpha) * (Var_{t-1} + alpha * (x_t - EWMA_{t-1})^2)
   Anomaly = |x_t - EWMA_t| > k * sqrt(Var_t)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoMetricAnomalyDetection:
    """
    --- contract:
      id: ALGO-VEC-OBS-189
      name: VectorObservabilityAlgoMetricAnomalyDetection
      category: observability
      complexity: O(T)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        metric_series: list[float]
        alpha: float
        sigma_threshold: float
      output_schema:
        anomaly_count: int
        anomaly_indices: list[int]
        final_ewma: float
        final_std_dev: float
        is_stream_anomalous: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        metric_series: List[float],
        alpha: float = 0.20,
        sigma_threshold: float = 3.0,
    ) -> Dict[str, Any]:
        if not metric_series:
            return {
                "anomaly_count": 0,
                "anomaly_indices": [],
                "final_ewma": 0.0,
                "final_std_dev": 0.0,
                "is_stream_anomalous": False,
            }

        ewma = metric_series[0]
        variance = 0.0
        anomaly_indices: List[int] = []

        for t, x in enumerate(metric_series):
            diff = x - ewma
            std_dev = math.sqrt(variance) if variance > 0 else 0.0

            if t > 5 and std_dev > 0.0:
                z = abs(diff) / std_dev
                if z > sigma_threshold:
                    anomaly_indices.append(t)

            ewma = alpha * x + (1.0 - alpha) * ewma
            variance = (1.0 - alpha) * (variance + alpha * (diff ** 2))

        final_std = math.sqrt(variance) if variance > 0 else 0.0

        return {
            "anomaly_count": len(anomaly_indices),
            "anomaly_indices": anomaly_indices,
            "final_ewma": round(ewma, 4),
            "final_std_dev": round(final_std, 4),
            "is_stream_anomalous": len(anomaly_indices) > 0,
        }
