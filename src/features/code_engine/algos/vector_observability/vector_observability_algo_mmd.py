"""
================================================================================
ALGORITHM BLUEPRINT: MAXIMUM MEAN DISCREPANCY (MMD) (ALGO-VEC-OBS-169)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Non-parametric kernel two-sample test measuring statistical distribution drift
   between baseline embedding sets and candidate/current embedding sets.

2. MATHEMATICAL FORMULATION:
   MMD^2(X, Y) = E[k(x, x')] + E[k(y, y')] - 2*E[k(x, y)]
   using RBF (Gaussian) kernel k(u, v) = exp(-gamma * ||u - v||^2).
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoMmd:
    """
    --- contract:
      id: ALGO-VEC-OBS-169
      name: VectorObservabilityAlgoMmd
      category: observability
      complexity: O((N + M)^2 * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        reference_sample: list[list[float]]
        current_sample: list[list[float]]
        gamma: Optional[float]
        drift_p_value_threshold: float
      output_schema:
        mmd_squared: float
        mmd_statistic: float
        is_statistically_significant_drift: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        reference_sample: List[List[float]],
        current_sample: List[List[float]],
        gamma: Optional[float] = None,
        drift_p_value_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        if not reference_sample or not current_sample:
            return {
                "mmd_squared": 0.0,
                "mmd_statistic": 0.0,
                "is_statistically_significant_drift": False,
            }

        n = len(reference_sample)
        m = len(current_sample)
        dim = len(reference_sample[0])

        effective_gamma = gamma if gamma is not None and gamma > 0 else (1.0 / float(dim) if dim > 0 else 1.0)

        def rbf_kernel(v1: List[float], v2: List[float]) -> float:
            sq_dist = sum((a - b) ** 2 for a, b in zip(v1, v2))
            return math.exp(-effective_gamma * sq_dist)

        k_xx = 0.0
        for i in range(n):
            for j in range(n):
                k_xx += rbf_kernel(reference_sample[i], reference_sample[j])
        k_xx /= float(n * n)

        k_yy = 0.0
        for i in range(m):
            for j in range(m):
                k_yy += rbf_kernel(current_sample[i], current_sample[j])
        k_yy /= float(m * m)

        k_xy = 0.0
        for i in range(n):
            for j in range(m):
                k_xy += rbf_kernel(reference_sample[i], current_sample[j])
        k_xy /= float(n * m)

        mmd_sq = max(0.0, k_xx + k_yy - (2.0 * k_xy))
        mmd_stat = math.sqrt(mmd_sq)

        is_drift = mmd_stat > 0.15

        return {
            "mmd_squared": round(mmd_sq, 6),
            "mmd_statistic": round(mmd_stat, 6),
            "is_statistically_significant_drift": is_drift,
        }
