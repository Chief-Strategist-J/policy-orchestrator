from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoOneByOneConvolutionBottleneck:
    """
    ---
    contract:
      algo_id: ALGO-NN-73
      name: NnAlgoOneByOneConvolutionBottleneck
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.1x1_conv
        - nn.bottleneck
        - nn.resnet
        - nn.channel_mixing
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
            description: 3D input activation tensor X of shape (C_in, H, W).
          w_reduce:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_mid, C_in) for 1x1 channel reduction.
          w_spatial:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel tensor of shape (C_mid, C_mid, K_h, K_w) for spatial convolution.
          w_expand:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_out, C_mid) for 1x1 channel expansion.
          padding:
            type: integer
            default: 1
            description: Symmetric spatial zero-padding p >= 0 applied during 3x3 spatial convolution.
        required:
          - input_tensor
          - w_reduce
          - w_spatial
          - w_expand
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
          reduced_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Intermediate reduced feature tensor of shape (C_mid, H, W).
          spatial_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Intermediate spatially convolved tensor of shape (C_mid, H_out, W_out).
          compression_ratio:
            type: number
            description: Bottleneck channel reduction ratio C_mid / C_in.
        required:
          - output_tensor
          - reduced_tensor
          - spatial_tensor
          - compression_ratio
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H, W).
        - w_reduce must have shape (C_mid, C_in).
        - w_spatial must have shape (C_mid, C_mid, K_h, K_w).
        - w_expand must have shape (C_out, C_mid).
        - padding must be >= 0.
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
          C_mid: bottleneck channels
          C_out: output channels
          H: height
          W: width
          K_h: kernel height
          K_w: kernel width
        time_worst: O(H * W * C_mid * (C_in + K_h * K_w * C_mid + C_out))
        time_typical: O(H * W * C_mid * (C_in + K_h * K_w * C_mid + C_out))
        space: O(H * W * (C_mid + C_out))
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(w_reduce) > 0 and len(w_reduce[0]) == len(input_tensor)
        - len(w_spatial) == len(w_reduce) and len(w_spatial[0]) == len(w_reduce)
        - len(w_spatial[0][0]) > 0 and len(w_spatial[0][0][0]) > 0
        - len(w_expand) > 0 and len(w_expand[0]) == len(w_reduce)
        - padding >= 0
      postconditions:
        - len(output.output_tensor) == len(w_expand)
        - len(output.reduced_tensor) == len(w_reduce)
        - len(output.spatial_tensor) == len(w_reduce)
        - output.compression_ratio > 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-71
        - ALGO-NN-74
      references:
        - "https://arxiv.org/abs/1312.4400"
        - "https://doi.org/10.1109/CVPR.2016.90"
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        w_reduce: Sequence[Sequence[float]],
        w_spatial: Sequence[Sequence[Sequence[Sequence[float]]]]],
        w_expand: Sequence[Sequence[float]],
        padding: int = 1,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        C_in = len(input_tensor)
        H = len(input_tensor[0])
        W = len(input_tensor[0][0])

        if not w_reduce or len(w_reduce[0]) != C_in:
            raise ValueError("Precondition failed: w_reduce must have shape (C_mid, C_in).")
        C_mid = len(w_reduce)

        if len(w_spatial) != C_mid or len(w_spatial[0]) != C_mid:
            raise ValueError("Precondition failed: w_spatial must have shape (C_mid, C_mid, K_h, K_w).")
        K_h = len(w_spatial[0][0])
        K_w = len(w_spatial[0][0][0])

        if not w_expand or len(w_expand[0]) != C_mid:
            raise ValueError("Precondition failed: w_expand must have shape (C_out, C_mid).")
        C_out = len(w_expand)

        if padding < 0:
            raise ValueError("Precondition failed: padding must be >= 0.")

        reduced_tensor: List[List[List[float]]] = [
            [[0.0] * W for _ in range(H)]
            for _ in range(C_mid)
        ]
        for cm in range(C_mid):
            row_w = w_reduce[cm]
            for h in range(H):
                for w in range(W):
                    acc = 0.0
                    for cin in range(C_in):
                        acc += row_w[cin] * input_tensor[cin][h][w]
                    reduced_tensor[cm][h][w] = acc

        padded_H = H + 2 * padding
        padded_W = W + 2 * padding
        H_out = padded_H - K_h + 1
        W_out = padded_W - K_w + 1

        padded_red: List[List[List[float]]] = [
            [[0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C_mid)
        ]
        for cm in range(C_mid):
            for h in range(H):
                for w in range(W):
                    padded_red[cm][h + padding][w + padding] = reduced_tensor[cm][h][w]

        spatial_tensor: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_mid)
        ]
        for cm_out in range(C_mid):
            kernel_cm = w_spatial[cm_out]
            for hout in range(H_out):
                for wout in range(W_out):
                    acc = 0.0
                    for cm_in in range(C_mid):
                        k_in = kernel_cm[cm_in]
                        pad_in = padded_red[cm_in]
                        for kh in range(K_h):
                            for kw in range(K_w):
                                acc += k_in[kh][kw] * pad_in[hout + kh][wout + kw]
                    spatial_tensor[cm_out][hout][wout] = acc

        out_tensor: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_out)
        ]
        for cout in range(C_out):
            row_exp = w_expand[cout]
            for hout in range(H_out):
                for wout in range(W_out):
                    acc = 0.0
                    for cm in range(C_mid):
                        acc += row_exp[cm] * spatial_tensor[cm][hout][wout]
                    out_tensor[cout][hout][wout] = acc

        return {
            "output_tensor": out_tensor,
            "reduced_tensor": reduced_tensor,
            "spatial_tensor": spatial_tensor,
            "compression_ratio": float(C_mid) / float(C_in),
        }
