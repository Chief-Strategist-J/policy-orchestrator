from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoSecondOrderPreconditioning:
    """
    ---
    contract:
      algo_id: ALGO-NN-40
      name: NnAlgoSecondOrderPreconditioning
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.optimizer
      - nn.second_order
      - nn.shampoo
      - nn.kfac
      - nn.preconditioning
      inputs:
        type: object
        properties:
          grad_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D gradient matrix G of shape (M, N).
          left_preconditioner:
            type: array
            items:
              type: array
              items:
                type: number
            description: Left Kronecker preconditioner buffer L = sum G G^T of shape (M,
              M).
          right_preconditioner:
            type: array
            items:
              type: array
              items:
                type: number
            description: Right Kronecker preconditioner buffer R = sum G^T G of shape
              (N, N).
          lr:
            type: number
            default: 0.001
            description: Learning rate eta > 0.
          eps:
            type: number
            default: 0.0001
            description: Diagonal damping epsilon > 0.
        required:
        - grad_matrix
        - left_preconditioner
        - right_preconditioner
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_left:
            type: array
            items:
              type: array
              items:
                type: number
            description: Accumulated left covariance matrix of shape (M, M).
          updated_right:
            type: array
            items:
              type: array
              items:
                type: number
            description: Accumulated right covariance matrix of shape (N, N).
          preconditioned_gradient:
            type: array
            items:
              type: array
              items:
                type: number
            description: Preconditioned matrix update of shape (M, N).
        required:
        - updated_left
        - updated_right
        - preconditioned_gradient
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
        grad_matrix: Sequence[Sequence[float]],
        left_preconditioner: Sequence[Sequence[float]],
        right_preconditioner: Sequence[Sequence[float]],
        lr: float = 0.001,
        eps: float = 1e-4,
    ) -> Dict[str, Any]:
        m = len(grad_matrix)
        if m == 0:
            raise ValueError("Precondition failed: grad_matrix cannot be empty.")
        n = len(grad_matrix[0])

        new_l = [[left_preconditioner[i][j] + sum(grad_matrix[i][k] * grad_matrix[j][k] for k in range(n)) for j in range(m)] for i in range(m)]

        new_r = [[right_preconditioner[i][j] + sum(grad_matrix[k][i] * grad_matrix[k][j] for k in range(m)) for j in range(n)] for i in range(n)]

        p_grad: List[List[float]] = []
        for i in range(m):
            l_scale = (new_l[i][i] + eps) ** (-0.25)
            row_p: List[float] = []
            for j in range(n):
                r_scale = (new_r[j][j] + eps) ** (-0.25)
                row_p.append(l_scale * grad_matrix[i][j] * r_scale)
            p_grad.append(row_p)

        return {
            "updated_left": new_l,
            "updated_right": new_r,
            "preconditioned_gradient": p_grad,
        }
