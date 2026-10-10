from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoGroupInstanceNorm:
    """
    ---
    contract:
      algo_id: ALGO-NN-54
      name: NnAlgoGroupInstanceNorm
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.group_norm
        - nn.instance_norm
        - nn.cnn
        - nn.diffusion
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 3D activation tensor X of shape (N, C, S) representing batch N, channels C, and spatial elements S.
          num_groups:
            type: integer
            default: 1
            description: Number of channel groups G (1 <= G <= C, where C % G == 0). G=C yields InstanceNorm; G=1 yields LayerNorm.
          gamma:
            type: array
            items:
              type: number
            description: Learned channel scale parameter vector of length C.
          beta:
            type: array
            items:
              type: number
            description: Learned channel shift parameter vector of length C.
          eps:
            type: number
            default: 0.00001
            description: Numerical stability regularizer epsilon > 0.
        required:
          - input_tensor
          - num_groups
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
                type: array
                items:
                  type: number
            description: Normalized output tensor Y of shape (N, C, S).
          group_means:
            type: array
            items:
              type: array
              items:
                type: number
            description: Computed mean per sample and group of shape (N, G).
          group_variances:
            type: array
            items:
              type: array
              items:
                type: number
            description: Computed variance per sample and group of shape (N, G).
        required:
          - normalized_tensor
          - group_means
          - group_variances
      parameters: {}
      input_assumptions:
        - Input tensor must be a non-empty 3D array of shape (N, C, S) with N >= 1, C >= 1, and S >= 1.
        - C must be cleanly divisible by num_groups (C % G == 0).
        - Lengths of gamma and beta must equal C.
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
          N: batch size
          C: channel count
          S: spatial elements per channel
          G: group count
        time_worst: O(N * C * S)
        time_typical: O(N * C * S)
        space: O(N * C * S)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - all(len(c_slice) == len(input_tensor[0]) for c_slice in input_tensor)
        - all(all(len(s_slice) == len(input_tensor[0][0]) for s_slice in c_slice) for c_slice in input_tensor)
        - 1 <= num_groups <= len(input_tensor[0])
        - len(input_tensor[0]) % num_groups == 0
        - len(gamma) == len(input_tensor[0])
        - len(beta) == len(input_tensor[0])
        - eps > 0
      postconditions:
        - len(output.normalized_tensor) == len(input_tensor)
        - len(output.normalized_tensor[0]) == len(input_tensor[0])
        - len(output.normalized_tensor[0][0]) == len(input_tensor[0][0])
        - len(output.group_means) == len(input_tensor)
        - len(output.group_means[0]) == num_groups
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-51
        - ALGO-NN-52
      references:
        - wu2018group
        - ulyanov2016instance
    ---
    """

    @staticmethod
    def normalize(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        num_groups: int,
        gamma: Sequence[float],
        beta: Sequence[float],
        eps: float = 1e-5,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        N = len(input_tensor)
        C = len(input_tensor[0])
        S = len(input_tensor[0][0])

        for n_idx in range(N):
            if len(input_tensor[n_idx]) != C:
                raise ValueError("Precondition failed: inconsistent channel count across samples.")
            for c_idx in range(C):
                if len(input_tensor[n_idx][c_idx]) != S:
                    raise ValueError("Precondition failed: inconsistent spatial count across channels.")

        G = num_groups
        if G < 1 or G > C or (C % G != 0):
            raise ValueError("Precondition failed: num_groups G must satisfy 1 <= G <= C and C % G == 0.")
        if len(gamma) != C or len(beta) != C:
            raise ValueError("Precondition failed: gamma and beta lengths must equal channel count C.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")

        channels_per_group = C // G
        group_elements = channels_per_group * S

        group_means: List[List[float]] = [[0.0] * G for _ in range(N)]
        group_variances: List[List[float]] = [[0.0] * G for _ in range(N)]
        out_tensor: List[List[List[float]]] = [[[0.0] * S for _ in range(C)] for _ in range(N)]

        for n in range(N):
            for g in range(G):
                c_start = g * channels_per_group
                c_end = c_start + channels_per_group

                # Compute group mean
                total_sum = 0.0
                for c in range(c_start, c_end):
                    total_sum += sum(input_tensor[n][c])
                m_ng = total_sum / float(group_elements)
                group_means[n][g] = m_ng

                # Compute group variance
                sq_diff_sum = 0.0
                for c in range(c_start, c_end):
                    sq_diff_sum += sum((x - m_ng) ** 2 for x in input_tensor[n][c])
                v_ng = sq_diff_sum / float(group_elements)
                group_variances[n][g] = v_ng

                std_ng = math.sqrt(v_ng + eps)

                # Normalize and apply affine scale and shift
                for c in range(c_start, c_end):
                    for s in range(S):
                        x_val = input_tensor[n][c][s]
                        x_hat = (x_val - m_ng) / std_ng
                        out_tensor[n][c][s] = gamma[c] * x_hat + beta[c]

        return {
            "normalized_tensor": out_tensor,
            "group_means": group_means,
            "group_variances": group_variances,
        }
