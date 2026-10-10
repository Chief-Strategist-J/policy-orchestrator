from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoInceptionMultibranchBlocks:
    """
    ---
    contract:
      algo_id: ALGO-NN-75
      name: NnAlgoInceptionMultibranchBlocks
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.inception
        - nn.multi_branch
        - nn.multi_scale
        - nn.googlenet
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
          branch1_w1x1:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_1, C_in) for direct 1x1 branch.
          branch2_w_red:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_3red, C_in) for 3x3 reduction branch.
          branch2_w3x3:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel of shape (C_3, C_3red, 3, 3) for 3x3 convolution.
          branch3_w_red:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_5red, C_in) for 5x5 reduction branch.
          branch3_w5x5:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel of shape (C_5, C_5red, 5, 5) (or 3x3) for branch 3.
          branch4_w1x1:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D weight matrix of shape (C_pool, C_in) for post-pooling projection.
        required:
          - input_tensor
          - branch1_w1x1
          - branch2_w_red
          - branch2_w3x3
          - branch3_w_red
          - branch3_w5x5
          - branch4_w1x1
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
            description: 3D concatenated feature tensor of shape (C_out, H, W) where C_out = C_1 + C_3 + C_5 + C_pool.
          branch_outputs:
            type: object
            description: Dictionary containing individual branch tensors {b1, b2, b3, b4}.
        required:
          - output_tensor
          - branch_outputs
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H, W).
        - Filter weights must match respective channel dimensions.
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
          C_out: total output channels
          H: height
          W: width
        time_worst: O(H * W * C_in * C_out)
        time_typical: O(H * W * C_in * C_out)
        space: O(C_out * H * W)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(branch1_w1x1) > 0 and len(branch1_w1x1[0]) == len(input_tensor)
        - len(branch2_w_red) > 0 and len(branch2_w_red[0]) == len(input_tensor)
        - len(branch2_w3x3) > 0 and len(branch2_w3x3[0]) == len(branch2_w_red)
        - len(branch3_w_red) > 0 and len(branch3_w_red[0]) == len(input_tensor)
        - len(branch3_w5x5) > 0 and len(branch3_w5x5[0]) == len(branch3_w_red)
        - len(branch4_w1x1) > 0 and len(branch4_w1x1[0]) == len(input_tensor)
      postconditions:
        - len(output.output_tensor) == len(branch1_w1x1) + len(branch2_w3x3) + len(branch3_w5x5) + len(branch4_w1x1)
        - len(output.output_tensor[0]) == len(input_tensor[0])
        - len(output.output_tensor[0][0]) == len(input_tensor[0][0])
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-73
        - ALGO-NN-74
      references:
        - "https://doi.org/10.1109/CVPR.2015.7298594"
        - "https://doi.org/search?q=szegedy2016rethinking"
    ---
    """

    @staticmethod
    def _conv1x1(x: Sequence[Sequence[Sequence[float]]], w: Sequence[Sequence[float]]) -> List[List[List[float]]]:
        C_in = len(x)
        H = len(x[0])
        W = len(x[0][0])
        C_out = len(w)
        out = [[[0.0] * W for _ in range(H)] for _ in range(C_out)]
        for cout in range(C_out):
            w_row = w[cout]
            for h in range(H):
                for w_idx in range(W):
                    acc = 0.0
                    for cin in range(C_in):
                        acc += w_row[cin] * x[cin][h][w_idx]
                    out[cout][h][w_idx] = acc
        return out

    @staticmethod
    def _conv2d_padded(
        x: Sequence[Sequence[Sequence[float]]],
        w: Sequence[Sequence[Sequence[Sequence[float]]]],
        pad: int,
    ) -> List[List[List[float]]]:
        C_in = len(x)
        H = len(x[0])
        W = len(x[0][0])
        C_out = len(w)
        K_h = len(w[0][0])
        K_w = len(w[0][0][0])

        padded_H = H + 2 * pad
        padded_W = W + 2 * pad
        padded = [[[0.0] * padded_W for _ in range(padded_H)] for _ in range(C_in)]
        for c in range(C_in):
            for h in range(H):
                for w_idx in range(W):
                    padded[c][h + pad][w_idx + pad] = float(x[c][h][w_idx])

        out = [[[0.0] * W for _ in range(H)] for _ in range(C_out)]
        for cout in range(C_out):
            w_cout = w[cout]
            for h in range(H):
                for w_idx in range(W):
                    acc = 0.0
                    for cin in range(C_in):
                        w_cin = w_cout[cin]
                        pad_cin = padded[cin]
                        for kh in range(K_h):
                            for kw in range(K_w):
                                acc += w_cin[kh][kw] * pad_cin[h + kh][w_idx + kw]
                    out[cout][h][w_idx] = acc
        return out

    @staticmethod
    def _maxpool3x3_same(x: Sequence[Sequence[Sequence[float]]]) -> List[List[List[float]]]:
        C = len(x)
        H = len(x[0])
        W = len(x[0][0])
        pad = 1
        padded = [[[-float("inf")] * (W + 2) for _ in range(H + 2)] for _ in range(C)]
        for c in range(C):
            for h in range(H):
                for w in range(W):
                    padded[c][h + pad][w + pad] = float(x[c][h][w])

        out = [[[0.0] * W for _ in range(H)] for _ in range(C)]
        for c in range(C):
            for h in range(H):
                for w in range(W):
                    m_val = -float("inf")
                    for kh in range(3):
                        for kw in range(3):
                            v = padded[c][h + kh][w + kw]
                            if v > m_val:
                                m_val = v
                    out[c][h][w] = m_val
        return out

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        branch1_w1x1: Sequence[Sequence[float]],
        branch2_w_red: Sequence[Sequence[float]],
        branch2_w3x3: Sequence[Sequence[Sequence[Sequence[float]]]],
        branch3_w_red: Sequence[Sequence[float]],
        branch3_w5x5: Sequence[Sequence[Sequence[Sequence[float]]]],
        branch4_w1x1: Sequence[Sequence[float]],
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        C_in = len(input_tensor)
        H = len(input_tensor[0])
        W = len(input_tensor[0][0])

        b1 = NnAlgoInceptionMultibranchBlocks._conv1x1(input_tensor, branch1_w1x1)

        b2_red = NnAlgoInceptionMultibranchBlocks._conv1x1(input_tensor, branch2_w_red)
        b2 = NnAlgoInceptionMultibranchBlocks._conv2d_padded(b2_red, branch2_w3x3, pad=1)

        pad3 = len(branch3_w5x5[0][0]) // 2
        b3_red = NnAlgoInceptionMultibranchBlocks._conv1x1(input_tensor, branch3_w_red)
        b3 = NnAlgoInceptionMultibranchBlocks._conv2d_padded(b3_red, branch3_w5x5, pad=pad3)

        b4_pool = NnAlgoInceptionMultibranchBlocks._maxpool3x3_same(input_tensor)
        b4 = NnAlgoInceptionMultibranchBlocks._conv1x1(b4_pool, branch4_w1x1)

        out_tensor: List[List[List[float]]] = []
        for ch in b1:
            out_tensor.append(ch)
        for ch in b2:
            out_tensor.append(ch)
        for ch in b3:
            out_tensor.append(ch)
        for ch in b4:
            out_tensor.append(ch)

        return {
            "output_tensor": out_tensor,
            "branch_outputs": {
                "branch1": b1,
                "branch2": b2,
                "branch3": b3,
                "branch4": b4,
            },
        }
