from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoRmspropOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-34
      name: NnAlgoRmspropOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.optimizer
      - nn.rmsprop
      - nn.adaptive_learning_rate
      - nn.ema
      inputs:
        type: object
        properties:
          parameters:
            type: array
            items:
              type: number
            description: Parameter vector theta of length P.
          gradients:
            type: array
            items:
              type: number
            description: Parameter gradient vector g of length P.
          moving_average:
            type: array
            items:
              type: number
            description: Exponential moving average second moment buffer v of length P.
          lr:
            type: number
            default: 0.001
            description: Learning rate eta > 0.
          alpha:
            type: number
            default: 0.99
            description: Smoothing factor alpha in [0, 1).
          eps:
            type: number
            default: 1.0e-08
            description: Denominator epsilon > 0.
        required:
        - parameters
        - gradients
        - moving_average
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
          updated_moving_average:
            type: array
            items:
              type: number
            description: Updated moving average second moment v_{t+1} of length P.
        required:
        - updated_parameters
        - updated_moving_average
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
        parameters: Sequence[float],
        gradients: Sequence[float],
        moving_average: Sequence[float],
        lr: float = 0.001,
        alpha: float = 0.99,
        eps: float = 1e-8,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p or len(moving_average) != p:
            raise ValueError("Precondition failed: buffers must have identical non-zero length.")
        if lr <= 0.0 or eps <= 0.0:
            raise ValueError("Precondition failed: lr and eps must be > 0.")
        if not (0.0 <= alpha < 1.0):
            raise ValueError(f"Precondition failed: alpha must be in [0, 1), got {alpha}.")

        new_params: List[float] = []
        new_v: List[float] = []

        for theta, g, v in zip(parameters, gradients, moving_average):
            v_next = alpha * v + (1.0 - alpha) * (g ** 2)
            theta_next = theta - (lr / (math.sqrt(v_next) + eps)) * g
            new_params.append(theta_next)
            new_v.append(v_next)

        return {
            "updated_parameters": new_params,
            "updated_moving_average": new_v,
        }
