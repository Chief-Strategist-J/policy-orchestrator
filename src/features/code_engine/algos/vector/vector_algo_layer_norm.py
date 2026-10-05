"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR LAYER NORMALIZATION (ALGO-VEC-03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardizes individual embedding vectors to zero mean and unit variance across
   their hidden dimensions, optionally applying learned or static gain (gamma)
   and bias (beta) affine transformations.

2. MATHEMATICAL FORMULA:
   Given vector x in R^D:
   mu = (1 / D) * sum(x_i for i in 1..D)
   sigma^2 = (1 / D) * sum((x_i - mu)^2 for i in 1..D)
   x_norm = gamma * (x - mu) / sqrt(sigma^2 + epsilon) + beta

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Robust against zero variance with configurable epsilon.
================================================================================
"""

from __future__ import annotations
import math
from typing import List, Optional


class VectorAlgoLayerNorm:
    """
    ---
    contract:
      algo_id: ALGO-VEC-03
      name: VectorAlgoLayerNorm
      version: 1.0.0
      category: vector
      capability_tags: [vector, normalization, layer_norm, standardization]
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
        epsilon: {type: number, default: 1e-5}
        gamma: {type: array, items: {type: number}, default: null}
        beta: {type: array, items: {type: number}, default: null}
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
        - len(output) == len(vector)
    ---
    """

    @staticmethod
    def normalize_single(
        vector: List[float],
        epsilon: float = 1e-5,
        gamma: Optional[List[float]] = None,
        beta: Optional[List[float]] = None,
    ) -> List[float]:
        dim = len(vector)
        if dim == 0:
            return []
        mu = sum(vector) / dim
        var = sum((x - mu) ** 2 for x in vector) / dim
        std = math.sqrt(var + epsilon)
        inv_std = 1.0 / std

        normalized = [(x - mu) * inv_std for x in vector]
        if gamma is not None and len(gamma) == dim:
            normalized = [n * g for n, g in zip(normalized, gamma)]
        if beta is not None and len(beta) == dim:
            normalized = [n + b for n, b in zip(normalized, beta)]
        return normalized

    @staticmethod
    def normalize_batch(
        vectors: List[List[float]],
        epsilon: float = 1e-5,
        gamma: Optional[List[float]] = None,
        beta: Optional[List[float]] = None,
    ) -> List[List[float]]:
        return [
            VectorAlgoLayerNorm.normalize_single(v, epsilon=epsilon, gamma=gamma, beta=beta)
            for v in vectors
        ]
