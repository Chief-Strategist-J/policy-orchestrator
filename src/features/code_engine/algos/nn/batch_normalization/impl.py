from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoBatchNormalization:
    """
    ---
    contract:
      algo_id: ALGO-NN-51
      name: NnAlgoBatchNormalization
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.batch_norm
        - nn.regularization
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D activation matrix X of shape (B, D) where B is batch size and D is feature dimension.
          gamma:
            type: array
            items:
              type: number
            description: Learned scale parameter vector of length D.
          beta:
            type: array
            items:
              type: number
            description: Learned shift (bias) parameter vector of length D.
          running_mean:
            type: array
            items:
              type: number
            description: Running mean vector of length D accumulated across training iterations.
          running_var:
            type: array
            items:
              type: number
            description: Running variance vector of length D accumulated across training iterations.
          training:
            type: boolean
            default: true
            description: Mode flag (true for training batch statistics, false for inference running statistics).
          momentum:
            type: number
            default: 0.1
            description: Running average momentum factor in (0, 1].
          eps:
            type: number
            default: 0.00001
            description: Numerical stability constant epsilon > 0.
        required:
          - input_tensor
          - gamma
          - beta
          - running_mean
          - running_var
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
          updated_running_mean:
            type: array
            items:
              type: number
            description: Updated running mean vector of length D.
          updated_running_var:
            type: array
            items:
              type: number
            description: Updated running variance vector of length D.
          batch_mean:
            type: array
            items:
              type: number
            description: Mean computed on the current batch (or used running mean if eval).
          batch_var:
            type: array
            items:
              type: number
            description: Variance computed on the current batch (or used running variance if eval).
        required:
          - normalized_tensor
          - updated_running_mean
          - updated_running_var
          - batch_mean
          - batch_var
      parameters: {}
      input_assumptions:
        - Input tensor must be a non-empty 2D matrix of shape (B, D) with B >= 1 and D >= 1.
        - In training mode with sample variance calculation, B >= 2 is recommended, but B >= 1 is supported with biased variance.
        - Lengths of gamma, beta, running_mean, and running_var must all equal D.
        - running_var entries must be non-negative.
        - eps must be strictly positive.
        - momentum must be in (0, 1].
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
          B: batch size
          D: feature dimension
        time_worst: O(B * D)
        time_typical: O(B * D)
        space: O(B * D)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0
        - all(len(row) == len(input_tensor[0]) for row in input_tensor)
        - len(gamma) == len(input_tensor[0])
        - len(beta) == len(input_tensor[0])
        - len(running_mean) == len(input_tensor[0])
        - len(running_var) == len(input_tensor[0])
        - all(v >= 0 for v in running_var)
        - eps > 0
        - 0.0 < momentum <= 1.0
      postconditions:
        - len(output.normalized_tensor) == len(input_tensor)
        - len(output.normalized_tensor[0]) == len(input_tensor[0])
        - len(output.updated_running_mean) == len(input_tensor[0])
        - len(output.updated_running_var) == len(input_tensor[0])
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-52
        - ALGO-NN-53
        - ALGO-NN-54
      references:
        - ioffe2015batch
    ---
    """

    @staticmethod
    def normalize(
        input_tensor: Sequence[Sequence[float]],
        gamma: Sequence[float],
        beta: Sequence[float],
        running_mean: Sequence[float],
        running_var: Sequence[float],
        training: bool = True,
        momentum: float = 0.1,
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
        if len(running_mean) != D or len(running_var) != D:
            raise ValueError("Precondition failed: running_mean and running_var vectors must have length D.")
        if any(v < 0.0 for v in running_var):
            raise ValueError("Precondition failed: running_var elements must be non-negative.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")
        if not (0.0 < momentum <= 1.0):
            raise ValueError("Precondition failed: momentum must be in (0, 1].")

        updated_mean = list(running_mean)
        updated_var = list(running_var)
        out_tensor: List[List[float]] = [[0.0] * D for _ in range(B)]

        if training:
            # Compute batch mean and batch variance per feature column
            mean_vec = [0.0] * D
            var_vec = [0.0] * D
            for j in range(D):
                col_sum = sum(input_tensor[i][j] for i in range(B))
                m_j = col_sum / float(B)
                mean_vec[j] = m_j

                sq_diff = sum((input_tensor[i][j] - m_j) ** 2 for i in range(B))
                v_j = sq_diff / float(B)
                var_vec[j] = v_j

                # Update running statistics
                updated_mean[j] = (1.0 - momentum) * running_mean[j] + momentum * m_j
                # Sample variance adjustment for running variance if B > 1
                unbiased_v_j = (sq_diff / float(B - 1)) if B > 1 else v_j
                updated_var[j] = (1.0 - momentum) * running_var[j] + momentum * unbiased_v_j

            for i in range(B):
                for j in range(D):
                    x_hat = (input_tensor[i][j] - mean_vec[j]) / math.sqrt(var_vec[j] + eps)
                    out_tensor[i][j] = gamma[j] * x_hat + beta[j]

            curr_mean = mean_vec
            curr_var = var_vec
        else:
            # Inference mode uses running statistics
            curr_mean = list(running_mean)
            curr_var = list(running_var)
            for i in range(B):
                for j in range(D):
                    x_hat = (input_tensor[i][j] - curr_mean[j]) / math.sqrt(curr_var[j] + eps)
                    out_tensor[i][j] = gamma[j] * x_hat + beta[j]

        return {
            "normalized_tensor": out_tensor,
            "updated_running_mean": updated_mean,
            "updated_running_var": updated_var,
            "batch_mean": curr_mean,
            "batch_var": curr_var,
        }
