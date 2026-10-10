from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoAdagradOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-33
      name: NnAlgoAdagradOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimizer
        - nn.adagrad
        - nn.adaptive_learning_rate
        - nn.sparse_features
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
            description: Coordinate gradient vector g of length P.
          state_accumulator:
            type: array
            items:
              type: number
            description: Accumulated squared gradient buffer G of length P.
          lr:
            type: number
            default: 0.01
            description: Global learning rate eta > 0.
          eps:
            type: number
            default: 0.00000001
            description: Numerical stability denominator epsilon > 0.
        required:
          - parameters
          - gradients
          - state_accumulator
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
          updated_accumulator:
            type: array
            items:
              type: number
            description: Updated squared gradient accumulator G_{t+1} of length P.
        required:
          - updated_parameters
          - updated_accumulator
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        parameters: Sequence[float],
        gradients: Sequence[float],
        state_accumulator: Sequence[float],
        lr: float = 0.01,
        eps: float = 1e-8,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p or len(state_accumulator) != p:
            raise ValueError("Precondition failed: buffers must have identical non-zero length.")
        if lr <= 0.0 or eps <= 0.0:
            raise ValueError("Precondition failed: lr and eps must be > 0.")

        new_params: List[float] = []
        new_accum: List[float] = []

        for theta, g, G in zip(parameters, gradients, state_accumulator):
            G_next = G + g ** 2
            theta_next = theta - (lr / (math.sqrt(G_next) + eps)) * g
            new_params.append(theta_next)
            new_accum.append(G_next)

        return {
            "updated_parameters": new_params,
            "updated_accumulator": new_accum,
        }
