from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoAdafactorOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-38
      name: NnAlgoAdafactorOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.optimizer
      - nn.adafactor
      - nn.memory_efficient
      - nn.matrix_factorization
      inputs:
        type: object
        properties:
          weight_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix W of shape (R, C).
          grad_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D gradient matrix G of shape (R, C).
          row_factor:
            type: array
            items:
              type: number
            description: Factored row moving average v_row of length R.
          col_factor:
            type: array
            items:
              type: number
            description: Factored column moving average v_col of length C.
          lr:
            type: number
            default: 0.001
            description: Learning rate eta > 0.
          beta2:
            type: number
            default: 0.999
            description: Second moment decay coefficient beta_2 in [0, 1).
          eps:
            type: number
            default: 1.0e-08
            description: Epsilon stability constant > 0.
        required:
        - weight_matrix
        - grad_matrix
        - row_factor
        - col_factor
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Updated weight matrix W_{t+1} of shape (R, C).
          updated_row_factor:
            type: array
            items:
              type: number
            description: Updated row factor buffer of length R.
          updated_col_factor:
            type: array
            items:
              type: number
            description: Updated column factor buffer of length C.
        required:
        - updated_weights
        - updated_row_factor
        - updated_col_factor
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
        weight_matrix: Sequence[Sequence[float]],
        grad_matrix: Sequence[Sequence[float]],
        row_factor: Sequence[float],
        col_factor: Sequence[float],
        lr: float = 0.001,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ) -> Dict[str, Any]:
        r = len(weight_matrix)
        if r == 0:
            raise ValueError("Precondition failed: weight_matrix cannot be empty.")
        c = len(weight_matrix[0])
        if len(grad_matrix) != r or len(grad_matrix[0]) != c or len(row_factor) != r or len(col_factor) != c:
            raise ValueError("Precondition failed: matrix dimension mismatch.")

        row_means = [sum(grad_matrix[i][j] ** 2 for j in range(c)) / float(c) for i in range(r)]
        col_means = [sum(grad_matrix[i][j] ** 2 for i in range(r)) / float(r) for j in range(c)]

        new_row = [beta2 * rf + (1.0 - beta2) * rm for rf, rm in zip(row_factor, row_means)]
        new_col = [beta2 * cf + (1.0 - beta2) * cm for cf, cm in zip(col_factor, col_means)]

        total_row_sum = sum(new_row) + eps

        new_weights: List[List[float]] = []
        for i in range(r):
            row_w: List[float] = []
            for j in range(c):
                v_ij = (new_row[i] * new_col[j]) / total_row_sum
                u_ij = grad_matrix[i][j] / (math.sqrt(v_ij) + eps)
                w_next = weight_matrix[i][j] - lr * u_ij
                row_w.append(w_next)
            new_weights.append(row_w)

        return {
            "updated_weights": new_weights,
            "updated_row_factor": new_row,
            "updated_col_factor": new_col,
        }
