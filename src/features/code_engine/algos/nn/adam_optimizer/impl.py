from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoAdamOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-35
      name: NnAlgoAdamOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimizer
        - nn.adam
        - nn.first_moment
        - nn.second_moment
        - nn.bias_correction
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
          exp_avg:
            type: array
            items:
              type: number
            description: First moment moving average m of length P.
          exp_avg_sq:
            type: array
            items:
              type: number
            description: Second moment moving average v of length P.
          step:
            type: integer
            description: Current optimizer step count t >= 1.
          lr:
            type: number
            default: 0.001
            description: Learning rate eta > 0.
          beta1:
            type: number
            default: 0.9
            description: First moment decay coefficient beta_1 in [0, 1).
          beta2:
            type: number
            default: 0.999
            description: Second moment decay coefficient beta_2 in [0, 1).
          eps:
            type: number
            default: 0.00000001
            description: Numerical stability denominator epsilon > 0.
        required:
          - parameters
          - gradients
          - exp_avg
          - exp_avg_sq
          - step
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
            description: Updated first moment buffer m_{t+1} of length P.
          updated_exp_avg_sq:
            type: array
            items:
              type: number
            description: Updated second moment buffer v_{t+1} of length P.
        required:
          - updated_parameters
          - updated_exp_avg
          - updated_exp_avg_sq
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        parameters: Sequence[float],
        gradients: Sequence[float],
        exp_avg: Sequence[float],
        exp_avg_sq: Sequence[float],
        step: int,
        lr: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p or len(exp_avg) != p or len(exp_avg_sq) != p:
            raise ValueError("Precondition failed: buffers must have identical non-zero length P.")
        if step < 1:
            raise ValueError(f"Precondition failed: step must be >= 1, got {step}.")
        if lr <= 0.0 or eps <= 0.0:
            raise ValueError("Precondition failed: lr and eps must be > 0.")
        if not (0.0 <= beta1 < 1.0) or not (0.0 <= beta2 < 1.0):
            raise ValueError("Precondition failed: beta1 and beta2 must be in [0, 1).")

        bias_correction1 = 1.0 - (beta1 ** step)
        bias_correction2 = 1.0 - (beta2 ** step)

        new_params: List[float] = []
        new_m: List[float] = []
        new_v: List[float] = []

        for theta, g, m, v in zip(parameters, gradients, exp_avg, exp_avg_sq):
            m_next = beta1 * m + (1.0 - beta1) * g
            v_next = beta2 * v + (1.0 - beta2) * (g ** 2)

            m_hat = m_next / bias_correction1
            v_hat = v_next / bias_correction2

            theta_next = theta - (lr * m_hat) / (math.sqrt(v_hat) + eps)

            new_params.append(theta_next)
            new_m.append(m_next)
            new_v.append(v_next)

        return {
            "updated_parameters": new_params,
            "updated_exp_avg": new_m,
            "updated_exp_avg_sq": new_v,
        }
