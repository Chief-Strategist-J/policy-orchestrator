"""
================================================================================
ALGORITHM BLUEPRINT: SCORE CALIBRATION (ALGO-VEC-TRFM-20)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calibrates raw retrieval scores (cosine similarities, dot products, or L2 distances)
   into well-behaved posterior probabilities or standardized confidence ranges in [0.0, 1.0].
   Supports Platt scaling (sigmoid), softmax temperature scaling, and min-max linear scaling.

2. ARCHITECTURAL ROLE:
   Transformer & Retriever role (Layer 1). Essential before hybrid score fusion (#86, #88)
   to ensure heterogeneous score distributions can be blended without scale dominance.

3. EXECUTION FLOW:
   a. Check input raw score array.
   b. If method == "sigmoid" (Platt scaling), apply 1.0 / (1.0 + exp(-(a * s + b))).
   c. If method == "temperature", apply softmax(s / T).
   d. If method == "minmax", linearly map [min_s, max_s] to [0.0, 1.0].
   e. Return calibrated scores with transformation coefficients.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoScoreCalibration:
    """
    --- contract:
      id: ALGO-VEC-TRFM-20
      name: VectorTransformAlgoScoreCalibration
      category: transform
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        scores: list[float]
        method: str
        temperature: float
        sigmoid_slope: float
        sigmoid_bias: float
      output_schema:
        total_scores: int
        method: str
        calibrated_scores: list[float]
    ---
    """

    @staticmethod
    def calibrate(
        scores: List[float],
        method: str = "sigmoid",
        temperature: float = 1.0,
        sigmoid_slope: float = 1.0,
        sigmoid_bias: float = 0.0,
    ) -> Dict[str, Any]:
        if not scores:
            return {"total_scores": 0, "method": method, "calibrated_scores": []}

        method_lower = method.lower()
        calibrated: List[float] = []

        if method_lower == "sigmoid":
            for s in scores:
                logit = sigmoid_slope * s + sigmoid_bias
                prob = 1.0 / (1.0 + math.exp(-max(-50.0, min(50.0, logit))))
                calibrated.append(round(prob, 6))

        elif method_lower in ("softmax", "temperature"):
            t = max(1e-4, temperature)
            scaled = [s / t for s in scores]
            max_s = max(scaled)
            exps = [math.exp(v - max_s) for v in scaled]
            sum_exp = sum(exps)
            calibrated = [round(e / sum_exp, 6) for e in exps]

        elif method_lower == "minmax":
            min_v = min(scores)
            max_v = max(scores)
            rng = max_v - min_v if max_v > min_v else 1.0
            calibrated = [round((s - min_v) / rng, 6) for s in scores]

        else:
            calibrated = list(scores)

        return {
            "total_scores": len(scores),
            "method": method_lower,
            "calibrated_scores": calibrated,
        }
