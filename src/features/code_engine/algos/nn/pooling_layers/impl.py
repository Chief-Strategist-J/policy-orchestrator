from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoPoolingLayers:
    """
    ---
    contract:
      algo_id: ALGO-NN-69
      name: NnAlgoPoolingLayers
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.pooling
        - nn.max_pooling
        - nn.avg_pooling
        - nn.global_avg_pooling
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
            description: 3D input activation tensor X of shape (C, H_in, W_in).
          pool_type:
            type: string
            enum:
              - max
              - average
              - global_average
            default: max
            description: Pooling reduction mode.
          kernel_size:
            type: array
            items:
              type: integer
            default:
              - 2
              - 2
            description: Spatial pooling window dimensions [K_h, K_w] (ignored for global_average).
          stride:
            type: array
            items:
              type: integer
            default:
              - 2
              - 2
            description: Spatial stride sliding step [s_h, s_w] (ignored for global_average).
          padding:
            type: array
            items:
              type: integer
            default:
              - 0
              - 0
            description: Spatial zero-padding borders [p_h, p_w].
        required:
          - input_tensor
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
            description: 3D pooled output feature map tensor Y of shape (C, H_out, W_out).
          out_height:
            type: integer
            description: Output spatial height H_out (equals 1 for global_average).
          out_width:
            type: integer
            description: Output spatial width W_out (equals 1 for global_average).
        required:
          - output_tensor
          - out_height
          - out_width
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C, H_in, W_in) with C >= 1, H_in >= 1, W_in >= 1.
        - pool_type must be one of ['max', 'average', 'global_average'].
        - kernel_size entries must be >= 1.
        - stride entries must be >= 1.
        - padding entries must be >= 0.
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
          C: channel count
          H_out: output height
          W_out: output width
          K_h: kernel height
          K_w: kernel width
        time_worst: O(C * H_out * W_out * K_h * K_w)
        time_typical: O(C * H_out * W_out * K_h * K_w)
        space: O(C * H_out * W_out)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - all(len(c) == len(input_tensor[0]) for c in input_tensor)
        - all(all(len(row) == len(input_tensor[0][0]) for row in c) for c in input_tensor)
        - pool_type in ["max", "average", "global_average"]
      postconditions:
        - len(output.output_tensor) == len(input_tensor)
        - len(output.output_tensor[0]) == output.out_height
        - len(output.output_tensor[0][0]) == output.out_width
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-68
      references:
        - "https://doi.org/search?q=boureau2010theoretical"
        - "https://arxiv.org/abs/1312.4400"
    ---
    """

    @staticmethod
    def pool(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        pool_type: Literal["max", "average", "global_average"] = "max",
        kernel_size: Sequence[int] = (2, 2),
        stride: Sequence[int] = (2, 2),
        padding: Sequence[int] = (0, 0),
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        C = len(input_tensor)
        H_in = len(input_tensor[0])
        W_in = len(input_tensor[0][0])

        for c_idx in range(C):
            if len(input_tensor[c_idx]) != H_in:
                raise ValueError("Precondition failed: inconsistent height across channels.")
            for h_idx in range(H_in):
                if len(input_tensor[c_idx][h_idx]) != W_in:
                    raise ValueError("Precondition failed: inconsistent width across rows.")

        if pool_type not in ["max", "average", "global_average"]:
            raise ValueError("Precondition failed: pool_type must be 'max', 'average', or 'global_average'.")

        if pool_type == "global_average":
            out_tensor: List[List[List[float]]] = [[[0.0]] for _ in range(C)]
            total_elements = float(H_in * W_in)
            for c in range(C):
                ch_sum = sum(sum(input_tensor[c][h][w] for w in range(W_in)) for h in range(H_in))
                out_tensor[c][0][0] = ch_sum / total_elements

            return {
                "output_tensor": out_tensor,
                "out_height": 1,
                "out_width": 1,
            }

        if len(kernel_size) != 2 or kernel_size[0] < 1 or kernel_size[1] < 1:
            raise ValueError("Precondition failed: kernel_size must be a pair of integers >= 1.")
        if len(stride) != 2 or stride[0] < 1 or stride[1] < 1:
            raise ValueError("Precondition failed: stride must be a pair of integers >= 1.")
        if len(padding) != 2 or padding[0] < 0 or padding[1] < 0:
            raise ValueError("Precondition failed: padding must be a pair of integers >= 0.")

        K_h, K_w = kernel_size
        s_h, s_w = stride
        p_h, p_w = padding

        padded_H = H_in + 2 * p_h
        padded_W = W_in + 2 * p_w

        if padded_H < K_h or padded_W < K_w:
            raise ValueError("Precondition failed: padded input dimensions must be >= kernel_size.")

        H_out = (padded_H - K_h) // s_h + 1
        W_out = (padded_W - K_w) // s_w + 1

        padded: List[List[List[float]]] = [
            [[-float("inf") if pool_type == "max" else 0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C)
        ]
        for c in range(C):
            for h in range(H_in):
                for w in range(W_in):
                    padded[c][h + p_h][w + p_w] = float(input_tensor[c][h][w])

        out_tensor = [[[0.0] * W_out for _ in range(H_out)] for _ in range(C)]
        window_size = float(K_h * K_w)

        for c in range(C):
            for hout in range(H_out):
                h_start = hout * s_h
                for wout in range(W_out):
                    w_start = wout * s_w
                    if pool_type == "max":
                        max_val = -float("inf")
                        for kh in range(K_h):
                            for kw in range(K_w):
                                v = padded[c][h_start + kh][w_start + kw]
                                if v > max_val:
                                    max_val = v
                        out_tensor[c][hout][wout] = max_val
                    elif pool_type == "average":
                        sum_val = 0.0
                        for kh in range(K_h):
                            for kw in range(K_w):
                                sum_val += padded[c][h_start + kh][w_start + kw]
                        out_tensor[c][hout][wout] = sum_val / window_size

        return {
            "output_tensor": out_tensor,
            "out_height": H_out,
            "out_width": W_out,
        }
