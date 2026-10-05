"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MIN-MAX & Z-SCORE NORMALIZATION (ALGO-VEC-04)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides bounded range mapping [min_val, max_val] via Min-Max scaling and
   statistical population standardization via Z-score scaling across vector dimensions.

2. MATHEMATICAL FORMULAS:
   - Min-Max Scaling to [A, B]:
     x_scaled = A + (x - min(X)) * (B - A) / max(max(X) - min(X), epsilon)
   - Z-Score Scaling:
     z = (x - mean(X)) / max(std(X), epsilon)

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Robust against uniform/flat vectors where max == min.
================================================================================
"""

from __future__ import annotations
import math
from typing import List, Tuple


class VectorAlgoMinMaxZScore:
    """
    ---
    contract:
      algo_id: ALGO-VEC-04
      name: VectorAlgoMinMaxZScore
      version: 1.0.0
      category: vector
      capability_tags: [vector, normalization, minmax, zscore, scaling]
      inputs:
        type: object
        required: [vector]
        properties:
          vector:
            type: array
            items: {type: number}
      outputs:
        type: array
        items: {type: number}
      parameters:
        target_range: {type: array, items: {type: number}, default: [0.0, 1.0]}
        epsilon: {type: number, default: 1e-12}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: reversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(D)
        space: O(D)
      preconditions:
        - len(vector) > 0
      postconditions:
        - len(output) == len(vector)
    ---
    """

    @staticmethod
    def min_max_scale(
        vector: List[float],
        target_range: Tuple[float, float] = (0.0, 1.0),
        epsilon: float = 1e-12,
    ) -> List[float]:
        if not vector:
            return []
        v_min = min(vector)
        v_max = max(vector)
        range_span = v_max - v_min
        target_min, target_max = target_range
        target_span = target_max - target_min

        if range_span < epsilon:
            return [target_min] * len(vector)

        scale = target_span / range_span
        return [target_min + (x - v_min) * scale for x in vector]

    @staticmethod
    def z_score_scale(
        vector: List[float],
        epsilon: float = 1e-12,
    ) -> List[float]:
        dim = len(vector)
        if dim == 0:
            return []
        mean_val = sum(vector) / dim
        variance = sum((x - mean_val) ** 2 for x in vector) / dim
        std_dev = math.sqrt(variance)
        if std_dev < epsilon:
            return [0.0] * dim
        inv_std = 1.0 / std_dev
        return [(x - mean_val) * inv_std for x in vector]
