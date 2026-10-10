from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoInvertedResidualsLinearBottleneck:
    """
    ---
    contract:
      algo_id: ALGO-NN-76
      name: NnAlgoInvertedResidualsLinearBottleneck
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.mobilenet_v2
        - nn.inverted_residuals
        - nn.linear_bottleneck
        - nn.depthwise
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
            description: 3D input activation tensor X of shape (C_in, H_in, W_in).
          w_expand:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_exp, C_in) for 1x1 expansion (C_exp = t * C_in).
          w_depthwise:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 3D depthwise kernel tensor of shape (C_exp, K_h, K_w).
          w_project:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_out, C_exp) for linear 1x1 projection.
          stride:
            type: integer
            default: 1
            description: Spatial stride s >= 1 for depthwise stage.
          padding:
            type: integer
            default: 1
            description: Spatial zero-padding p >= 0 for depthwise stage.
        required:
          - input_tensor
          - w_expand
          - w_depthwise
          - w_project
      outputs:
        type: object
        properties:
          output_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 3D output tensor Y of shape (C_out, H_out, W_out).
          expanded_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Intermediate expanded tensor after 1x1 conv and ReLU6 of shape (C_exp, H_in, W_in).
          depthwise_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Intermediate depthwise tensor after 3x3 conv and ReLU6 of shape (C_exp, H_out, W_out).
          has_residual:
            type: boolean
            description: True if identity residual shortcut was added (stride == 1 and C_in == C_out).
        required:
          - output_tensor
          - expanded_tensor
          - depthwise_tensor
          - has_residual
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - w_expand must have shape (C_exp, C_in).
        - w_depthwise must have shape (C_exp, K_h, K_w).
        - w_project must have shape (C_out, C_exp).
        - stride must be >= 1; padding must be >= 0.
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
          C_in: input channels
          C_exp: expanded channels
          C_out: output channels
          H_out: output height
          W_out: output width
        time_worst: O(H_out * W_out * C_exp * (C_in + 9 + C_out))
        time_typical: O(H_out * W_out * C_exp * (C_in + 9 + C_out))
        space: O(H_out * W_out * (C_exp + C_out))
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(w_expand) > 0 and len(w_expand[0]) == len(input_tensor)
        - len(w_depthwise) == len(w_expand) and len(w_depthwise[0]) > 0 and len(w_depthwise[0][0]) > 0
        - len(w_project) > 0 and len(w_project[0]) == len(w_expand)
        - stride >= 1 and padding >= 0
      postconditions:
        - len(output.output_tensor) == len(w_project)
        - len(output.expanded_tensor) == len(w_expand)
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-71
        - ALGO-NN-73
        - ALGO-NN-74
      references:
        - sandler2018mobilenetv2
    ---
    """

    @staticmethod
    def _relu6(val: float) -> float:
        return min(max(0.0, val), 6.0)

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        w_expand: Sequence[Sequence[float]],
        w_depthwise: Sequence[Sequence[Sequence[float]]],
        w_project: Sequence[Sequence[float]],
        stride: int = 1,
        padding: int = 1,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        C_in = len(input_tensor)
        H_in = len(input_tensor[0])
        W_in = len(input_tensor[0][0])

        if not w_expand or len(w_expand[0]) != C_in:
            raise ValueError("Precondition failed: w_expand shape must match (C_exp, C_in).")
        C_exp = len(w_expand)

        if len(w_depthwise) != C_exp:
            raise ValueError("Precondition failed: w_depthwise channels must match C_exp.")
        K_h = len(w_depthwise[0])
        K_w = len(w_depthwise[0][0])

        if not w_project or len(w_project[0]) != C_exp:
            raise ValueError("Precondition failed: w_project shape must match (C_out, C_exp).")
        C_out = len(w_project)

        if stride < 1 or padding < 0:
            raise ValueError("Precondition failed: stride must be >= 1 and padding >= 0.")

        # Stage 1: 1x1 Expansion + ReLU6
        expanded_tensor: List[List[List[float]]] = [
            [[0.0] * W_in for _ in range(H_in)]
            for _ in range(C_exp)
        ]
        for ce in range(C_exp):
            row_exp = w_expand[ce]
            for h in range(H_in):
                for w in range(W_in):
                    acc = 0.0
                    for cin in range(C_in):
                        acc += row_exp[cin] * input_tensor[cin][h][w]
                    expanded_tensor[ce][h][w] = NnAlgoInvertedResidualsLinearBottleneck._relu6(acc)

        # Stage 2: Depthwise 3x3 Conv + ReLU6
        padded_H = H_in + 2 * padding
        padded_W = W_in + 2 * padding
        H_out = (padded_H - K_h) // stride + 1
        W_out = (padded_W - K_w) // stride + 1

        padded_exp: List[List[List[float]]] = [
            [[0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C_exp)
        ]
        for ce in range(C_exp):
            for h in range(H_in):
                for w in range(W_in):
                    padded_exp[ce][h + padding][w + padding] = expanded_tensor[ce][h][w]

        depthwise_tensor: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_exp)
        ]
        for ce in range(C_exp):
            k_ce = w_depthwise[ce]
            for hout in range(H_out):
                h_start = hout * stride
                for wout in range(W_out):
                    w_start = wout * stride
                    acc = 0.0
                    for kh in range(K_h):
                        for kw in range(K_w):
                            acc += k_ce[kh][kw] * padded_exp[ce][h_start + kh][w_start + kw]
                    depthwise_tensor[ce][hout][wout] = NnAlgoInvertedResidualsLinearBottleneck._relu6(acc)

        # Stage 3: Linear 1x1 Pointwise Projection (NO activation function)
        linear_projected: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_out)
        ]
        for cout in range(C_out):
            row_proj = w_project[cout]
            for hout in range(H_out):
                for wout in range(W_out):
                    acc = 0.0
                    for ce in range(C_exp):
                        acc += row_proj[ce] * depthwise_tensor[ce][hout][wout]
                    linear_projected[cout][hout][wout] = acc

        # Stage 4: Residual Shortcut (only if stride == 1 and C_in == C_out)
        has_residual = (stride == 1 and C_in == C_out)
        out_tensor: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_out)
        ]
        for cout in range(C_out):
            for hout in range(H_out):
                for wout in range(W_out):
                    val = linear_projected[cout][hout][wout]
                    if has_residual:
                        val += input_tensor[cout][hout][wout]
                    out_tensor[cout][hout][wout] = val

        return {
            "output_tensor": out_tensor,
            "expanded_tensor": expanded_tensor,
            "depthwise_tensor": depthwise_tensor,
            "has_residual": has_residual,
        }
