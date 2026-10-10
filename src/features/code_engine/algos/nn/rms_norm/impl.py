from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoRmsNorm:
    """
    ---
    contract:
      algo_id: ALGO-NN-53
      name: NnAlgoRmsNorm
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.rms_norm
        - nn.llm
        - nn.transformer
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
          eps:
            type: number
            default: 0.000001
            description: Numerical stability regularizer epsilon > 0.
        required:
          - input_tensor
          - gamma
      outputs:
        type: object
        properties:
          normalized_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output tensor Y = gamma * (x / RMS(x)) of shape (B, D).
          rms_values:
            type: array
            items:
              type: number
            description: Root mean square value computed for each sample row, vector of length B.
        required:
          - normalized_tensor
          - rms_values
      parameters: {}
      input_assumptions:
        - Input tensor must be a non-empty 2D matrix of shape (B, D) with B >= 1 and D >= 1.
        - Length of gamma must equal D.
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
        - eps > 0
      postconditions:
        - len(output.normalized_tensor) == len(input_tensor)
        - len(output.normalized_tensor[0]) == len(input_tensor[0])
        - len(output.rms_values) == len(input_tensor)
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-52
        - ALGO-NN-57
      references:
        - zhang2019root
    ---
    """

    @staticmethod
    def normalize(
        input_tensor: Sequence[Sequence[float]],
        gamma: Sequence[float],
        eps: float = 1e-6,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 2D array.")
        B = len(input_tensor)
        D = len(input_tensor[0])

        for row in input_tensor:
            if len(row) != D:
                raise ValueError("Precondition failed: all rows in input_tensor must have identical length D.")

        if len(gamma) != D:
            raise ValueError("Precondition failed: gamma vector must have length D.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")

        rms_values: List[float] = [0.0] * B
        out_tensor: List[List[float]] = [[0.0] * D for _ in range(B)]

        for i in range(B):
            row = input_tensor[i]
            mean_sq = sum(x * x for x in row) / float(D)
            rms_i = math.sqrt(mean_sq + eps)
            rms_values[i] = rms_i

            for j in range(D):
                out_tensor[i][j] = (row[j] / rms_i) * gamma[j]

        return {
            "normalized_tensor": out_tensor,
            "rms_values": rms_values,
        }
