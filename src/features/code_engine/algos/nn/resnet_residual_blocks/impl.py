from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoResnetResidualBlocks:
    """
    ---
    contract:
      algo_id: ALGO-NN-74
      name: NnAlgoResnetResidualBlocks
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.resnet
        - nn.residual_connection
        - nn.basic_block
        - nn.bottleneck_block
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
          block_type:
            type: string
            enum:
              - basic
              - bottleneck
            default: basic
            description: ResNet building block topology.
          conv1_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel for first convolution in main branch.
          conv2_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel for second convolution in main branch.
          conv3_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel for third convolution (required for bottleneck blocks).
          shortcut_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: Optional 4D weight kernel of shape (C_out, C_in, 1, 1) for projection shortcut.
          stride:
            type: integer
            default: 1
            description: Downsampling stride s >= 1 applied in first or second layer.
        required:
          - input_tensor
          - conv1_weights
          - conv2_weights
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
            description: 3D output tensor Y = ReLU(F(X) + Shortcut(X)) of shape (C_out, H_out, W_out).
          residual_branch:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Transformation tensor F(X) before residual addition.
          shortcut_branch:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Shortcut tensor aligned with residual branch.
        required:
          - output_tensor
          - residual_branch
          - shortcut_branch
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - conv1_weights, conv2_weights must be non-empty 4D arrays.
        - In bottleneck mode, conv3_weights is required.
        - stride must be >= 1.
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
          C_out: output channels
          H_out: output height
          W_out: output width
        time_worst: O(H_out * W_out * C_in * C_out)
        time_typical: O(H_out * W_out * C_in * C_out)
        space: O(C_out * H_out * W_out)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(conv1_weights) > 0 and len(conv1_weights[0]) == len(input_tensor)
        - len(conv2_weights) > 0
        - block_type in ["basic", "bottleneck"]
        - stride >= 1
      postconditions:
        - len(output.output_tensor) > 0
        - len(output.output_tensor[0]) > 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-73
        - ALGO-NN-76
      references:
        - "https://doi.org/10.1109/CVPR.2016.90"
        - "https://doi.org/search?q=he2016identity"
    ---
    """

    @staticmethod
    def _conv2d(
        x: Sequence[Sequence[Sequence[float]]],
        w: Sequence[Sequence[Sequence[Sequence[float]]]]],
        stride: int = 1,
        padding: int = 0,
    ) -> List[List[List[float]]]:
        C_in = len(x)
        H_in = len(x[0])
        W_in = len(x[0][0])
        C_out = len(w)
        K_h = len(w[0][0])
        K_w = len(w[0][0][0])

        padded_H = H_in + 2 * padding
        padded_W = W_in + 2 * padding
        H_out = (padded_H - K_h) // stride + 1
        W_out = (padded_W - K_w) // stride + 1

        padded = [
            [[0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C_in)
        ]
        for c in range(C_in):
            for h in range(H_in):
                for w_idx in range(W_in):
                    padded[c][h + padding][w_idx + padding] = float(x[c][h][w_idx])

        out: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_out)
        ]

        for cout in range(C_out):
            w_cout = w[cout]
            for hout in range(H_out):
                h_start = hout * stride
                for wout in range(W_out):
                    w_start = wout * stride
                    acc = 0.0
                    for cin in range(C_in):
                        w_cin = w_cout[cin]
                        pad_cin = padded[cin]
                        for kh in range(K_h):
                            for kw in range(K_w):
                                acc += w_cin[kh][kw] * pad_cin[h_start + kh][w_start + kw]
                    out[cout][hout][wout] = acc
        return out

    @staticmethod
    def _relu(x: Sequence[Sequence[Sequence[float]]]) -> List[List[List[float]]]:
        return [
            [[max(0.0, float(v)) for v in row] for row in channel]
            for channel in x
        ]

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        conv1_weights: Sequence[Sequence[Sequence[Sequence[float]]]]],
        conv2_weights: Sequence[Sequence[Sequence[Sequence[float]]]]],
        block_type: Literal["basic", "bottleneck"] = "basic",
        conv3_weights: Optional[Sequence[Sequence[Sequence[Sequence[float]]]]]] = None,
        shortcut_weights: Optional[Sequence[Sequence[Sequence[Sequence[float]]]]]] = None,
        stride: int = 1,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")
        if block_type not in ["basic", "bottleneck"]:
            raise ValueError("Precondition failed: block_type must be 'basic' or 'bottleneck'.")

        C_in = len(input_tensor)
        H_in = len(input_tensor[0])
        W_in = len(input_tensor[0][0])

        if block_type == "basic":
            f1 = NnAlgoResnetResidualBlocks._conv2d(input_tensor, conv1_weights, stride=stride, padding=1)
            a1 = NnAlgoResnetResidualBlocks._relu(f1)
            residual_branch = NnAlgoResnetResidualBlocks._conv2d(a1, conv2_weights, stride=1, padding=1)
        else:
            if not conv3_weights:
                raise ValueError("Precondition failed: conv3_weights required for bottleneck block.")
            f1 = NnAlgoResnetResidualBlocks._conv2d(input_tensor, conv1_weights, stride=1, padding=0)
            a1 = NnAlgoResnetResidualBlocks._relu(f1)
            f2 = NnAlgoResnetResidualBlocks._conv2d(a1, conv2_weights, stride=stride, padding=1)
            a2 = NnAlgoResnetResidualBlocks._relu(f2)
            residual_branch = NnAlgoResnetResidualBlocks._conv2d(a2, conv3_weights, stride=1, padding=0)

        C_out = len(residual_branch)
        H_out = len(residual_branch[0])
        W_out = len(residual_branch[0][0])

        if shortcut_weights is not None:
            shortcut_branch = NnAlgoResnetResidualBlocks._conv2d(input_tensor, shortcut_weights, stride=stride, padding=0)
        else:
            if stride == 1 and C_in == C_out:
                shortcut_branch = [
                    [[float(input_tensor[c][h][w]) for w in range(W_in)] for h in range(H_in)]
                    for c in range(C_in)
                ]
            else:
                shortcut_branch = [
                    [[float(input_tensor[c][h * stride][w * stride]) for w in range(W_out)] for h in range(H_out)]
                    for c in range(min(C_in, C_out))
                ]

        out_tensor: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_out)
        ]
        for c in range(C_out):
            for h in range(H_out):
                for w in range(W_out):
                    s_val = shortcut_branch[c][h][w] if c < len(shortcut_branch) else 0.0
                    r_val = residual_branch[c][h][w]
                    out_tensor[c][h][w] = max(0.0, r_val + s_val)

        return {
            "output_tensor": out_tensor,
            "residual_branch": residual_branch,
            "shortcut_branch": shortcut_branch,
        }
