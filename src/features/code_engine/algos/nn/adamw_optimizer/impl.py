from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoAdamwOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-36
      name: NnAlgoAdamwOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimizer
        - nn.adamw
        - nn.decoupled_weight_decay
        - nn.transformer_training
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
            description: First moment buffer m of length P.
          exp_avg_sq:
            type: array
            items:
              type: number
            description: Second moment buffer v of length P.
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
            description: First moment decay beta_1 in [0, 1).
          beta2:
            type: number
            default: 0.999
            description: Second moment decay beta_2 in [0, 1).
          eps:
            type: number
            default: 0.00000001
            description: Stability constant epsilon > 0.
          weight_decay:
            type: number
            default: 0.01
            description: Decoupled weight decay coefficient lambda >= 0.
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
        weight_decay: float = 0.01,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p or len(exp_avg) != p or len(exp_avg_sq) != p:
            raise ValueError("Precondition failed: buffers must have identical non-zero length P.")
        if step < 1:
            raise ValueError(f"Precondition failed: step must be >= 1, got {step}.")
        if lr <= 0.0 or eps <= 0.0:
            raise ValueError("Precondition failed: lr and eps must be > 0.")
        if weight_decay < 0.0:
            raise ValueError(f"Precondition failed: weight_decay must be >= 0, got {weight_decay}.")

        bias_correction1 = 1.0 - (beta1 ** step)
        bias_correction2 = 1.0 - (beta2 ** step)

        new_params: List[float] = []
        new_m: List[float] = []
        new_v: List[float] = []

        for theta, g, m, v in zip(parameters, gradients, exp_avg, exp_avg_sq):
            theta_decayed = theta * (1.0 - lr * weight_decay)

            m_next = beta1 * m + (1.0 - beta1) * g
            v_next = beta2 * v + (1.0 - beta2) * (g ** 2)

            m_hat = m_next / bias_correction1
            v_hat = v_next / bias_correction2

            theta_next = theta_decayed - (lr * m_hat) / (math.sqrt(v_hat) + eps)

            new_params.append(theta_next)
            new_m.append(m_next)
            new_v.append(v_next)

        return {
            "updated_parameters": new_params,
            "updated_exp_avg": new_m,
            "updated_exp_avg_sq": new_v,
        }
