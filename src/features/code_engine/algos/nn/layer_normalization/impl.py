from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLayerNormalization:
    """
    ---
    contract:
      algo_id: ALGO-NN-52
      name: NnAlgoLayerNormalization
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.layer_norm
        - nn.transformer
        - nn.recurrent
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D activation matrix X of shape (B, D) where B is batch/sequence size and D is hidden feature dimension.
          gamma:
            type: array
            items:
              type: number
            description: Learned gain parameter vector of length D.
          beta:
            type: array
            items:
              type: number
            description: Learned bias parameter vector of length D.
          eps:
            type: number
            default: 0.00001
            description: Numerical regularization constant epsilon > 0.
        required:
          - input_tensor
          - gamma
          - beta
      outputs:
        type: object
        properties:
          normalized_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output tensor Y = gamma * x_hat + beta of shape (B, D).
          means:
            type: array
            items:
              type: number
            description: Mean computed for each sample row, vector of length B.
          variances:
            type: array
            items:
              type: number
            description: Variance computed for each sample row, vector of length B.
        required:
          - normalized_tensor
          - means
          - variances
      parameters: {}
      input_assumptions:
        - Input tensor must be a non-empty 2D matrix of shape (B, D) with B >= 1 and D >= 1.
        - Lengths of gamma and beta must equal D.
        - eps must be strictly positive.
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: any
      exactness: exact
      error_bound: n/a
      uses_model: false
      complexity:
        variables:
          B: batch or sequence length
          D: feature dimension
        time_worst: O(B * D)
        time_typical: O(B * D)
        space: O(B * D)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0
        - all(len(row) == len(input_tensor[0]) for row in input_tensor)
        - len(gamma) == len(input_tensor[0])
        - len(beta) == len(input_tensor[0])
        - eps > 0
      postconditions:
        - len(output.normalized_tensor) == len(input_tensor)
        - len(output.normalized_tensor[0]) == len(input_tensor[0])
        - len(output.means) == len(input_tensor)
        - len(output.variances) == len(input_tensor)
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-51
        - ALGO-NN-53
        - ALGO-NN-54
      references:
        - "https://arxiv.org/abs/1607.06450"
    ---
    """

    @staticmethod
    def normalize(
        input_tensor: Sequence[Sequence[float]],
        gamma: Sequence[float],
        beta: Sequence[float],
        eps: float = 1e-5,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 2D array.")
        B = len(input_tensor)
        D = len(input_tensor[0])

        for row in input_tensor:
            if len(row) != D:
                raise ValueError("Precondition failed: all rows in input_tensor must have identical length D.")

        if len(gamma) != D or len(beta) != D:
            raise ValueError("Precondition failed: gamma and beta vectors must have length D.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")

        means: List[float] = [0.0] * B
        variances: List[float] = [0.0] * B
        out_tensor: List[List[float]] = [[0.0] * D for _ in range(B)]

        for i in range(B):
            row = input_tensor[i]
            m_i = sum(row) / float(D)
            means[i] = m_i

            v_i = sum((x - m_i) ** 2 for x in row) / float(D)
            variances[i] = v_i

            std_i = math.sqrt(v_i + eps)
            for j in range(D):
                x_hat = (row[j] - m_i) / std_i
                out_tensor[i][j] = gamma[j] * x_hat + beta[j]

        return {
            "normalized_tensor": out_tensor,
            "means": means,
            "variances": variances,
        }
