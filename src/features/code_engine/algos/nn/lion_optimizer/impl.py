from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLionOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-39
      name: NnAlgoLionOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimizer
        - nn.lion
        - nn.sign_momentum
        - nn.memory_efficiency
      inputs:
        type: object
        properties:
          parameters:
            type: array
            items:
              type: number
            description: Parameter coordinate vector theta of length P.
          gradients:
            type: array
            items:
              type: number
            description: Gradient vector g of length P.
          exp_avg:
            type: array
            items:
              type: number
            description: Momentum buffer m of length P.
          lr:
            type: number
            default: 0.0001
            description: Learning rate eta > 0.
          beta1:
            type: number
            default: 0.9
            description: Interpolation momentum factor beta_1 in [0, 1).
          beta2:
            type: number
            default: 0.99
            description: Tracking momentum factor beta_2 in [0, 1).
          weight_decay:
            type: number
            default: 0.1
            description: Decoupled weight decay coefficient lambda >= 0.
        required:
          - parameters
          - gradients
          - exp_avg
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
          updated_exp_avg:
            type: array
            items:
              type: number
            description: Updated momentum buffer m_{t+1} of length P.
        required:
          - updated_parameters
          - updated_exp_avg
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        parameters: Sequence[float],
        gradients: Sequence[float],
        exp_avg: Sequence[float],
        lr: float = 1e-4,
        beta1: float = 0.9,
        beta2: float = 0.99,
        weight_decay: float = 0.1,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p or len(exp_avg) != p:
            raise ValueError("Precondition failed: buffers must have identical non-zero length P.")
        if lr <= 0.0:
            raise ValueError(f"Precondition failed: lr must be > 0, got {lr}.")

        new_params: List[float] = []
        new_m: List[float] = []

        for theta, g, m in zip(parameters, gradients, exp_avg):
            # Compute update direction using sign of interpolated momentum
            interp = beta1 * m + (1.0 - beta1) * g
            sign_update = 1.0 if interp > 0.0 else (-1.0 if interp < 0.0 else 0.0)

            # Update weights: theta = theta * (1 - lr * lambda) - lr * sign_update
            theta_next = theta * (1.0 - lr * weight_decay) - lr * sign_update

            # Update momentum buffer: m = beta2 * m + (1 - beta2) * g
            m_next = beta2 * m + (1.0 - beta2) * g

            new_params.append(theta_next)
            new_m.append(m_next)

        return {
            "updated_parameters": new_params,
            "updated_exp_avg": new_m,
        }
