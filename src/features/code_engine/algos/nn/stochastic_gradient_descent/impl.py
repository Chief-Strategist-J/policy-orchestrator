from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoStochasticGradientDescent:
    """
    ---
    contract:
      algo_id: ALGO-NN-31
      name: NnAlgoStochasticGradientDescent
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimizer
        - nn.sgd
        - nn.gradient_descent
        - nn.weight_decay
      inputs:
        type: object
        properties:
          parameters:
            type: array
            items:
              type: number
            description: Current parameter vector theta of length P.
          gradients:
            type: array
            items:
              type: number
            description: Parameter gradient vector g of length P.
          lr:
            type: number
            default: 0.01
            description: Learning rate step size eta > 0.
          weight_decay:
            type: number
            default: 0.0
            description: L2 weight decay regularization coefficient lambda >= 0.
        required:
          - parameters
          - gradients
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
          step_norm:
            type: number
            description: L2 Euclidean norm of the parameter displacement step.
        required:
          - updated_parameters
          - step_norm
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        parameters: Sequence[float],
        gradients: Sequence[float],
        lr: float = 0.01,
        weight_decay: float = 0.0,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0:
            raise ValueError("Precondition failed: parameters list cannot be empty.")
        if len(gradients) != p:
            raise ValueError(f"Precondition failed: gradients length ({len(gradients)}) must match parameters ({p}).")
        if lr <= 0.0:
            raise ValueError(f"Precondition failed: learning rate lr must be > 0, got {lr}.")
        if weight_decay < 0.0:
            raise ValueError(f"Precondition failed: weight_decay must be >= 0, got {weight_decay}.")

        new_params: List[float] = []
        step_sq = 0.0

        for theta, g in zip(parameters, gradients):
            grad_eff = g + weight_decay * theta
            delta = lr * grad_eff
            theta_new = theta - delta
            new_params.append(theta_new)
            step_sq += delta ** 2

        return {
            "updated_parameters": new_params,
            "step_norm": math.sqrt(step_sq),
        }
