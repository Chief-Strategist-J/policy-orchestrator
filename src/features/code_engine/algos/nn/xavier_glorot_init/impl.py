from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoXavierGlorotInit:
    """
    ---
    contract:
      algo_id: ALGO-NN-47
      name: NnAlgoXavierGlorotInit
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.initialization
      - nn.xavier
      - nn.glorot
      - nn.variance_preservation
      inputs:
        type: object
        properties:
          fan_in:
            type: integer
            description: Number of input connections fan_in >= 1.
          fan_out:
            type: integer
            description: Number of output connections fan_out >= 1.
          distribution:
            type: string
            enum:
            - uniform
            - normal
            default: uniform
            description: Sampling distribution family.
          gain:
            type: number
            default: 1.0
            description: Non-linearity gain multiplier.
        required:
        - fan_in
        - fan_out
        additionalProperties: false
      outputs:
        type: object
        properties:
          std_dev:
            type: number
            description: Standard deviation sigma for normal sampling.
          uniform_bound:
            type: number
            description: Half-width bound a for uniform sampling in [-a, a].
          variance:
            type: number
            description: Target weight variance 2 / (fan_in + fan_out).
        required:
        - std_dev
        - uniform_bound
        - variance
        additionalProperties: false
      parameters: {}
      input_assumptions:
      - Input tensors and parameters satisfy dimensionality and finite numerical bounds.
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: Standard IEEE-754 floating point precision
      uses_model: false
      complexity:
        variables:
          N: tensor/parameter dimension
        time_worst: O(N)
        time_typical: O(N)
        space: O(N)
      preconditions:
      - Input tensors are non-empty and conform to defined mathematical shapes.
      postconditions:
      - Output values and arrays are populated without NaN or infinite values.
      certificate: Exact implementation matching analytical mathematical derivation.
      compatible_adapters: []
      related_algos: []
      references:
      - https://arxiv.org/
    ---
    """

    @staticmethod
    def forward(
        fan_in: int,
        fan_out: int,
        distribution: Literal["uniform", "normal"] = "uniform",
        gain: float = 1.0,
    ) -> Dict[str, Any]:
        if fan_in < 1 or fan_out < 1:
            raise ValueError("Precondition failed: fan_in and fan_out must be >= 1.")
        if gain <= 0.0:
            raise ValueError(f"Precondition failed: gain must be > 0, got {gain}.")

        var = (gain ** 2) * (2.0 / float(fan_in + fan_out))
        std = math.sqrt(var)
        bound = math.sqrt(3.0 * var)

        return {
            "std_dev": std,
            "uniform_bound": bound,
            "variance": var,
        }
