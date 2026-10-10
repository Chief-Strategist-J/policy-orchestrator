from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoNormalizationPlacement:
    """
    ---
    contract:
      algo_id: ALGO-NN-56
      name: NnAlgoNormalizationPlacement
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.transformer
        - nn.pre_norm
        - nn.post_norm
        - nn.deep_norm
        - nn.sandwich_norm
      inputs:
        type: object
        properties:
          x_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D input residual stream tensor X of shape (B, D).
          sublayer_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Linear transformation matrix W of shape (D, D) representing the sublayer F(z) = z W.
          placement:
            type: string
            enum:
              - pre_norm
              - post_norm
              - sandwich_norm
              - deep_norm
            default: pre_norm
            description: Architectural normalization placement pattern.
          gamma:
            type: array
            items:
              type: number
            description: Gain parameter vector of length D for normalization.
          beta:
            type: array
            items:
              type: number
            description: Bias parameter vector of length D for normalization.
          alpha_residual:
            type: number
            default: 1.0
            description: Residual scale factor alpha used in deep_norm mode.
          beta_sublayer:
            type: number
            default: 1.0
            description: Sublayer branch scale factor beta_s used in deep_norm mode.
          eps:
            type: number
            default: 0.00001
            description: Numerical stability regularizer epsilon > 0.
        required:
          - x_tensor
          - sublayer_weights
          - gamma
          - beta
      outputs:
        type: object
        properties:
          output_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output residual block tensor of shape (B, D).
          sublayer_output:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output of the sublayer computation F(z) of shape (B, D).
        required:
          - output_tensor
          - sublayer_output
      parameters: {}
      input_assumptions:
        - x_tensor must be a non-empty 2D array of shape (B, D) with B >= 1 and D >= 1.
        - sublayer_weights must be a 2D square matrix of shape (D, D).
        - Lengths of gamma and beta must equal D.
        - eps must be strictly positive.
        - alpha_residual and beta_sublayer must be positive numbers.
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
          D: hidden dimension
        time_worst: O(B * D^2)
        time_typical: O(B * D^2)
        space: O(B * D)
      preconditions:
        - len(x_tensor) > 0 and len(x_tensor[0]) > 0
        - all(len(row) == len(x_tensor[0]) for row in x_tensor)
        - len(sublayer_weights) == len(x_tensor[0])
        - all(len(row) == len(x_tensor[0]) for row in sublayer_weights)
        - len(gamma) == len(x_tensor[0])
        - len(beta) == len(x_tensor[0])
        - placement in ["pre_norm", "post_norm", "sandwich_norm", "deep_norm"]
        - alpha_residual > 0.0
        - beta_sublayer > 0.0
        - eps > 0
      postconditions:
        - len(output.output_tensor) == len(x_tensor)
        - len(output.output_tensor[0]) == len(x_tensor[0])
        - len(output.sublayer_output) == len(x_tensor)
        - len(output.sublayer_output[0]) == len(x_tensor[0])
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-52
        - ALGO-NN-53
        - ALGO-NN-57
      references:
        - "https://arxiv.org/abs/2002.04745"
        - "https://doi.org/search?q=wang2022deepnet"
        - "https://arxiv.org/abs/1706.03762"
    ---
    """

    @staticmethod
    def _layer_norm_row(
        row: Sequence[float],
        gamma: Sequence[float],
        beta: Sequence[float],
        eps: float,
    ) -> List[float]:
        D = len(row)
        m = sum(row) / float(D)
        v = sum((x - m) ** 2 for x in row) / float(D)
        std_val = math.sqrt(v + eps)
        return [gamma[j] * ((row[j] - m) / std_val) + beta[j] for j in range(D)]

    @staticmethod
    def _apply_sublayer(
        matrix: Sequence[Sequence[float]],
        weights: Sequence[Sequence[float]],
    ) -> List[List[float]]:
        B = len(matrix)
        D = len(weights)
        res = [[0.0] * D for _ in range(B)]
        for i in range(B):
            for j in range(D):
                res[i][j] = sum(matrix[i][k] * weights[k][j] for k in range(D))
        return res

    @staticmethod
    def forward(
        x_tensor: Sequence[Sequence[float]],
        sublayer_weights: Sequence[Sequence[float]],
        gamma: Sequence[float],
        beta: Sequence[float],
        placement: Literal["pre_norm", "post_norm", "sandwich_norm", "deep_norm"] = "pre_norm",
        alpha_residual: float = 1.0,
        beta_sublayer: float = 1.0,
        eps: float = 1e-5,
    ) -> Dict[str, Any]:
        if not x_tensor or not x_tensor[0]:
            raise ValueError("Precondition failed: x_tensor must be non-empty 2D array.")
        B = len(x_tensor)
        D = len(x_tensor[0])

        for row in x_tensor:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in x_tensor.")

        if len(sublayer_weights) != D or any(len(r) != D for r in sublayer_weights):
            raise ValueError("Precondition failed: sublayer_weights must be a (D, D) square matrix.")
        if len(gamma) != D or len(beta) != D:
            raise ValueError("Precondition failed: gamma and beta vectors must have length D.")
        if placement not in ["pre_norm", "post_norm", "sandwich_norm", "deep_norm"]:
            raise ValueError("Precondition failed: invalid placement option.")
        if alpha_residual <= 0.0 or beta_sublayer <= 0.0:
            raise ValueError("Precondition failed: alpha_residual and beta_sublayer must be positive.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")

        out_tensor: List[List[float]] = [[0.0] * D for _ in range(B)]
        sub_out: List[List[float]] = [[0.0] * D for _ in range(B)]

        if placement == "pre_norm":
            normed_x = [NnAlgoNormalizationPlacement._layer_norm_row(x_tensor[i], gamma, beta, eps) for i in range(B)]
            sub_out = NnAlgoNormalizationPlacement._apply_sublayer(normed_x, sublayer_weights)
            for i in range(B):
                for j in range(D):
                    out_tensor[i][j] = x_tensor[i][j] + sub_out[i][j]

        elif placement == "post_norm":
            sub_out = NnAlgoNormalizationPlacement._apply_sublayer(x_tensor, sublayer_weights)
            sum_tensor = [
                [x_tensor[i][j] + sub_out[i][j] for j in range(D)]
                for i in range(B)
            ]
            out_tensor = [
                NnAlgoNormalizationPlacement._layer_norm_row(sum_tensor[i], gamma, beta, eps)
                for i in range(B)
            ]

        elif placement == "sandwich_norm":
            normed_x = [NnAlgoNormalizationPlacement._layer_norm_row(x_tensor[i], gamma, beta, eps) for i in range(B)]
            raw_sub = NnAlgoNormalizationPlacement._apply_sublayer(normed_x, sublayer_weights)
            sub_out = [NnAlgoNormalizationPlacement._layer_norm_row(raw_sub[i], gamma, beta, eps) for i in range(B)]
            for i in range(B):
                for j in range(D):
                    out_tensor[i][j] = x_tensor[i][j] + sub_out[i][j]

        elif placement == "deep_norm":
            raw_sub = NnAlgoNormalizationPlacement._apply_sublayer(x_tensor, sublayer_weights)
            sub_out = [[beta_sublayer * raw_sub[i][j] for j in range(D)] for i in range(B)]
            sum_tensor = [
                [alpha_residual * x_tensor[i][j] + sub_out[i][j] for j in range(D)]
                for i in range(B)
            ]
            out_tensor = [
                NnAlgoNormalizationPlacement._layer_norm_row(sum_tensor[i], gamma, beta, eps)
                for i in range(B)
            ]

        return {
            "output_tensor": out_tensor,
            "sublayer_output": sub_out,
        }
