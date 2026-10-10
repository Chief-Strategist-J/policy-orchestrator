from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoWeightSpectralNorm:
    """
    ---
    contract:
      algo_id: ALGO-NN-55
      name: NnAlgoWeightSpectralNorm
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.spectral_norm
        - nn.weight_norm
        - nn.lipschitz_continuity
        - nn.gan
      inputs:
        type: object
        properties:
          weight_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight parameter matrix W of shape (M, N).
          u_vector:
            type: array
            items:
              type: number
            description: Left singular vector accumulator u of length M (used in spectral norm mode).
          v_vector:
            type: array
            items:
              type: number
            description: Right singular vector accumulator v of length N (or direction vector in weight_norm mode).
          mode:
            type: string
            enum:
              - spectral
              - weight_norm
            default: spectral
            description: Normalization mode ('spectral' for Lipschitz bounding, 'weight_norm' for scale/direction decoupling).
          g_scale:
            type: number
            default: 1.0
            description: Explicit magnitude scale scalar g used in weight_norm mode (g > 0).
          num_power_iterations:
            type: integer
            default: 1
            description: Number of power iteration steps for spectral norm estimation.
          eps:
            type: number
            default: 0.000001
            description: Numerical stability regularizer epsilon > 0.
        required:
          - weight_matrix
          - u_vector
          - v_vector
      outputs:
        type: object
        properties:
          normalized_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized weight matrix of shape (M, N).
          sigma:
            type: number
            description: Estimated spectral norm (largest singular value) or L2 norm.
          updated_u:
            type: array
            items:
              type: number
            description: Updated left singular vector u of length M.
          updated_v:
            type: array
            items:
              type: number
            description: Updated right singular vector v of length N.
        required:
          - normalized_weights
          - sigma
          - updated_u
          - updated_v
      parameters: {}
      input_assumptions:
        - weight_matrix must be a non-empty 2D array of shape (M, N) with M >= 1 and N >= 1.
        - Length of u_vector must equal M.
        - Length of v_vector must equal N.
        - In spectral mode, at least one of u_vector or v_vector must have non-zero norm.
        - num_power_iterations must be >= 1.
        - eps must be strictly positive.
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: any
      exactness: approximate
      error_bound: Geometric convergence with rate (sigma_2 / sigma_1)^(2k)
      uses_model: false
      complexity:
        variables:
          M: row dimension of weight matrix
          N: column dimension of weight matrix
          K: power iteration steps
        time_worst: O(K * M * N)
        time_typical: O(K * M * N)
        space: O(M * N)
      preconditions:
        - len(weight_matrix) > 0 and len(weight_matrix[0]) > 0
        - all(len(row) == len(weight_matrix[0]) for row in weight_matrix)
        - len(u_vector) == len(weight_matrix)
        - len(v_vector) == len(weight_matrix[0])
        - mode in ["spectral", "weight_norm"]
        - num_power_iterations >= 1
        - g_scale > 0.0
        - eps > 0
      postconditions:
        - len(output.normalized_weights) == len(weight_matrix)
        - len(output.normalized_weights[0]) == len(weight_matrix[0])
        - len(output.updated_u) == len(weight_matrix)
        - len(output.updated_v) == len(weight_matrix[0])
        - output.sigma > 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-51
        - ALGO-NN-52
      references:
        - miyato2018spectral
        - salimans2016weight
    ---
    """

    @staticmethod
    def normalize(
        weight_matrix: Sequence[Sequence[float]],
        u_vector: Sequence[float],
        v_vector: Sequence[float],
        mode: Literal["spectral", "weight_norm"] = "spectral",
        g_scale: float = 1.0,
        num_power_iterations: int = 1,
        eps: float = 1e-6,
    ) -> Dict[str, Any]:
        if not weight_matrix or not weight_matrix[0]:
            raise ValueError("Precondition failed: weight_matrix must be non-empty 2D array.")
        M = len(weight_matrix)
        N = len(weight_matrix[0])

        for row in weight_matrix:
            if len(row) != N:
                raise ValueError("Precondition failed: all rows in weight_matrix must have equal length N.")

        if len(u_vector) != M:
            raise ValueError("Precondition failed: u_vector length must equal M.")
        if len(v_vector) != N:
            raise ValueError("Precondition failed: v_vector length must equal N.")
        if mode not in ["spectral", "weight_norm"]:
            raise ValueError("Precondition failed: mode must be 'spectral' or 'weight_norm'.")
        if num_power_iterations < 1:
            raise ValueError("Precondition failed: num_power_iterations must be >= 1.")
        if g_scale <= 0.0:
            raise ValueError("Precondition failed: g_scale must be strictly positive.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")

        norm_weights: List[List[float]] = [[0.0] * N for _ in range(M)]

        if mode == "spectral":
            u_curr = list(u_vector)
            v_curr = list(v_vector)

            # Ensure u_curr has non-zero norm
            u_norm = math.sqrt(sum(x * x for x in u_curr))
            if u_norm < eps:
                u_curr = [1.0 / math.sqrt(float(M))] * M

            for _ in range(num_power_iterations):
                # v = W^T u / ||W^T u||
                v_unnorm = [0.0] * N
                for j in range(N):
                    v_unnorm[j] = sum(weight_matrix[i][j] * u_curr[i] for i in range(M))
                v_norm = math.sqrt(sum(x * x for x in v_unnorm)) + eps
                v_curr = [x / v_norm for x in v_unnorm]

                # u = W v / ||W v||
                u_unnorm = [0.0] * M
                for i in range(M):
                    u_unnorm[i] = sum(weight_matrix[i][j] * v_curr[j] for j in range(N))
                u_norm = math.sqrt(sum(x * x for x in u_unnorm)) + eps
                u_curr = [x / u_norm for x in u_unnorm]

            # sigma = u^T W v
            # W v
            wv = [sum(weight_matrix[i][j] * v_curr[j] for j in range(N)) for i in range(M)]
            sigma_val = sum(u_curr[i] * wv[i] for i in range(M))
            sigma_val = max(sigma_val, eps)

            for i in range(M):
                for j in range(N):
                    norm_weights[i][j] = weight_matrix[i][j] / sigma_val

            return {
                "normalized_weights": norm_weights,
                "sigma": sigma_val,
                "updated_u": u_curr,
                "updated_v": v_curr,
            }
        else:
            # weight_norm mode: per-row direction vector normalization scaled by g_scale
            # Treats each row of W as direction vector v_i: w_i = g * (v_i / ||v_i||)
            # Or Frobenius norm of matrix
            frob_norm = math.sqrt(sum(sum(x * x for x in row) for row in weight_matrix)) + eps
            for i in range(M):
                for j in range(N):
                    norm_weights[i][j] = g_scale * (weight_matrix[i][j] / frob_norm)

            return {
                "normalized_weights": norm_weights,
                "sigma": frob_norm,
                "updated_u": list(u_vector),
                "updated_v": list(v_vector),
            }
