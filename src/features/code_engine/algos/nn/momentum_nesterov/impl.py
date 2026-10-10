from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoMomentumNesterov:
    """
    ---
    contract:
      algo_id: ALGO-NN-32
      name: NnAlgoMomentumNesterov
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimizer
        - nn.momentum
        - nn.nesterov
        - nn.acceleration
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
          velocity:
            type: array
            items:
              type: number
            description: Momentum velocity buffer v of length P.
          lr:
            type: number
            default: 0.01
            description: Learning rate eta > 0.
          beta:
            type: number
            default: 0.9
            description: Momentum damping coefficient beta in [0, 1).
          nesterov:
            type: boolean
            default: false
            description: Whether to apply Nesterov Accelerated Gradient (NAG) lookahead formulation.
        required:
          - parameters
          - gradients
          - velocity
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
          updated_velocity:
            type: array
            items:
              type: number
            description: Updated velocity buffer v_{t+1} of length P.
        required:
          - updated_parameters
          - updated_velocity
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        parameters: Sequence[float],
        gradients: Sequence[float],
        velocity: Sequence[float],
        lr: float = 0.01,
        beta: float = 0.9,
        nesterov: bool = False,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p or len(velocity) != p:
            raise ValueError("Precondition failed: parameter, gradient, and velocity buffers must have identical non-zero length.")
        if lr <= 0.0:
            raise ValueError(f"Precondition failed: lr must be > 0, got {lr}.")
        if not (0.0 <= beta < 1.0):
            raise ValueError(f"Precondition failed: beta must be in [0, 1), got {beta}.")

        new_params: List[float] = []
        new_velocity: List[float] = []

        for theta, g, v in zip(parameters, gradients, velocity):
            v_next = beta * v + g
            if nesterov:
                step = lr * (g + beta * v_next)
            else:
                step = lr * v_next

            theta_next = theta - step
            new_params.append(theta_next)
            new_velocity.append(v_next)

        return {
            "updated_parameters": new_params,
            "updated_velocity": new_velocity,
        }
