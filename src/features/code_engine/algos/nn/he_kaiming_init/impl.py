from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoHeKaimingInit:
    """
    ---
    contract:
      algo_id: ALGO-NN-48
      name: NnAlgoHeKaimingInit
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.initialization
      - nn.kaiming
      - nn.he_init
      - nn.relu_init
      inputs:
        type: object
        properties:
          fan_in:
            type: integer
            description: Input connection dimension fan_in >= 1.
          mode:
            type: string
            enum:
            - fan_in
            - fan_out
            default: fan_in
            description: Forward variance preservation (fan_in) vs backward gradient variance
              preservation (fan_out).
          fan_out:
            type: integer
            default: 1
            description: Output connection dimension (required if mode is fan_out).
          nonlinearity:
            type: string
            enum:
            - relu
            - leaky_relu
            default: relu
            description: Rectification activation function.
          negative_slope:
            type: number
            default: 0.0
            description: Negative slope alpha for Leaky ReLU.
        required:
        - fan_in
        additionalProperties: false
      outputs:
        type: object
        properties:
          std_dev:
            type: number
            description: Standard deviation sigma for normal initialization.
          uniform_bound:
            type: number
            description: Bound a for uniform initialization in [-a, a].
          gain:
            type: number
            description: Non-linearity compensation gain factor.
        required:
        - std_dev
        - uniform_bound
        - gain
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
        mode: Literal["fan_in", "fan_out"] = "fan_in",
        fan_out: int = 1,
        nonlinearity: Literal["relu", "leaky_relu"] = "relu",
        negative_slope: float = 0.0,
    ) -> Dict[str, Any]:
        if fan_in < 1 or fan_out < 1:
            raise ValueError("Precondition failed: fan dimensions must be >= 1.")

        if nonlinearity == "relu":
            gain = math.sqrt(2.0)
        elif nonlinearity == "leaky_relu":
            gain = math.sqrt(2.0 / (1.0 + negative_slope ** 2))
        else:
            raise ValueError(f"Precondition failed: unknown nonlinearity {nonlinearity}")

        fan = fan_in if mode == "fan_in" else fan_out
        std = gain / math.sqrt(fan)
        bound = math.sqrt(3.0) * std

        return {
            "std_dev": std,
            "uniform_bound": bound,
            "gain": gain,
        }
