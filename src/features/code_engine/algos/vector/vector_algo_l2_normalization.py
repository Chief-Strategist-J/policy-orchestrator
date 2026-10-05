"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: L2 VECTOR NORMALIZATION (ALGO-VEC-01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Scales input vectors to unit Euclidean norm (length 1.0) so that Euclidean distance
   and dot product become mathematically equivalent to cosine similarity.
   Safely detects and handles near-zero/all-zero vectors with configurable epsilon.

2. MATHEMATICAL FORMULA:
   Given vector v in R^D:
   norm(v) = sqrt(sum(v_i^2) for i in 1..D)
   v_normalized = v / max(norm(v), epsilon) if norm(v) >= epsilon else rejected/zeroed.

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Preserves deterministic floating-point precision (IEEE 754 64-bit).
================================================================================
"""

from __future__ import annotations
import math
from typing import List, Union


class VectorAlgoL2Normalization:
    """
    ---
    contract:
      algo_id: ALGO-VEC-01
      name: VectorAlgoL2Normalization
      version: 1.0.0
      category: vector
      capability_tags: [vector, normalization, l2, cosine_prep]
      inputs:
        type: object
        required: [vector]
        properties:
          vector:
            type: array
            items: {type: number}
      outputs:
        type: object
        required: [normalized_vector, original_norm]
        properties:
          normalized_vector:
            type: array
            items: {type: number}
          original_norm:
            type: number
      parameters:
        epsilon: {type: number, default: 1e-12}
        raise_on_zero: {type: boolean, default: false}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(D)
        space: O(D)
      preconditions:
        - len(vector) > 0
      postconditions:
        - abs(sum(x*x for x in normalized_vector) - 1.0) < 1e-5 or original_norm < epsilon
    ---
    """

    @staticmethod
    def normalize_single(
        vector: List[float],
        epsilon: float = 1e-12,
        raise_on_zero: bool = False,
    ) -> List[float]:
        if not vector:
            return []
        sq_sum = sum(x * x for x in vector)
        norm = math.sqrt(sq_sum)
        if norm < epsilon:
            if raise_on_zero:
                raise ValueError(f"Cannot L2-normalize near-zero vector with norm {norm} < {epsilon}")
            return [0.0] * len(vector)
        inv_norm = 1.0 / norm
        return [x * inv_norm for x in vector]

    @staticmethod
    def normalize_batch(
        vectors: List[List[float]],
        epsilon: float = 1e-12,
        raise_on_zero: bool = False,
    ) -> List[List[float]]:
        return [
            VectorAlgoL2Normalization.normalize_single(v, epsilon=epsilon, raise_on_zero=raise_on_zero)
            for v in vectors
        ]
