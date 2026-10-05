"""
================================================================================
ALGORITHM BLUEPRINT: VECTOR NORM DISTRIBUTION & ANOMALY DETECTOR (ALGO-VEC-OBS-172)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates embedding length/magnitude distribution (L2 norms) to detect corrupted,
   unnormalized, zero, or NaN/Inf vectors at ingestion or query time.

2. MATHEMATICAL FORMULATION:
   L2_Norm = sqrt(sum_{d=1}^D v_d^2)
   Anomalies = Vectors with ||v|| == 0, ||v|| is NaN/Inf, or | ||v|| - expected | > tol
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoVectorNormDistribution:
    """
    --- contract:
      id: ALGO-VEC-OBS-172
      name: VectorObservabilityAlgoVectorNormDistribution
      category: observability
      complexity: O(N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        expected_norm: Optional[float]
        tolerance: float
      output_schema:
        mean_norm: float
        std_dev_norm: float
        zero_norm_count: int
        nan_or_inf_count: int
        abnormal_norm_count: int
        is_integrity_valid: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        vectors: List[List[float]],
        expected_norm: Optional[float] = 1.0,
        tolerance: float = 0.05,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "mean_norm": 0.0,
                "std_dev_norm": 0.0,
                "zero_norm_count": 0,
                "nan_or_inf_count": 0,
                "abnormal_norm_count": 0,
                "is_integrity_valid": True,
            }

        norms: List[float] = []
        zero_count = 0
        nan_inf_count = 0
        abnormal_count = 0

        for vec in vectors:
            has_nan_inf = any(math.isnan(x) or math.isinf(x) for x in vec)
            if has_nan_inf or not vec:
                nan_inf_count += 1
                abnormal_count += 1
                continue

            norm_val = math.sqrt(sum(x * x for x in vec))
            norms.append(norm_val)

            if norm_val == 0.0:
                zero_count += 1
                abnormal_count += 1
            elif expected_norm is not None:
                if abs(norm_val - expected_norm) > tolerance:
                    abnormal_count += 1

        n_valid = len(norms)
        mean_n = sum(norms) / float(n_valid) if n_valid > 0 else 0.0
        var_n = sum((x - mean_n) ** 2 for x in norms) / float(n_valid) if n_valid > 0 else 0.0
        std_n = math.sqrt(var_n)

        is_valid = (zero_count == 0) and (nan_inf_count == 0) and (abnormal_count == 0)

        return {
            "mean_norm": round(mean_n, 4),
            "std_dev_norm": round(std_n, 4),
            "zero_norm_count": zero_count,
            "nan_or_inf_count": nan_inf_count,
            "abnormal_norm_count": abnormal_count,
            "is_integrity_valid": is_valid,
        }
