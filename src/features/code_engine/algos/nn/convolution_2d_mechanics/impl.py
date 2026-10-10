from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoConvolution2dMechanics:
    """
    ---
    contract:
      algo_id: ALGO-NN-67
      name: NnAlgoConvolution2dMechanics
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.conv2d
        - nn.vision
        - nn.feature_extraction
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
          weight_kernels:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D filter weight tensor W of shape (C_out, C_in, K_h, K_w).
          bias:
            type: array
            items:
              type: number
            description: Optional 1D bias vector of length C_out (defaults to zeros if omitted).
          stride_h:
            type: integer
            default: 1
            description: Vertical sliding step stride s_h >= 1.
          stride_w:
            type: integer
            default: 1
            description: Horizontal sliding step stride s_w >= 1.
          pad_h:
            type: integer
            default: 0
            description: Symmetric vertical zero-padding p_h >= 0.
          pad_w:
            type: integer
            default: 0
            description: Symmetric horizontal zero-padding p_w >= 0.
        required:
          - input_tensor
          - weight_kernels
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
            description: 3D convolved feature map tensor Y of shape (C_out, H_out, W_out).
          out_height:
            type: integer
            description: Computed spatial output height H_out.
          out_width:
            type: integer
            description: Computed spatial output width W_out.
        required:
          - output_tensor
          - out_height
          - out_width
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - weight_kernels must be a non-empty 4D array of shape (C_out, C_in, K_h, K_w).
        - C_in in weight_kernels must match C_in of input_tensor.
        - stride_h, stride_w must be >= 1.
        - pad_h, pad_w must be >= 0.
        - H_in + 2*pad_h >= K_h and W_in + 2*pad_w >= K_w.
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
          K_h: kernel height
          K_w: kernel width
        time_worst: O(C_out * C_in * H_out * W_out * K_h * K_w)
        time_typical: O(C_out * C_in * H_out * W_out * K_h * K_w)
        space: O(C_out * H_out * W_out)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(weight_kernels) > 0 and len(weight_kernels[0]) == len(input_tensor)
        - len(weight_kernels[0][0]) > 0 and len(weight_kernels[0][0][0]) > 0
        - stride_h >= 1 and stride_w >= 1
        - pad_h >= 0 and pad_w >= 0
        - len(input_tensor[0]) + 2 * pad_h >= len(weight_kernels[0][0])
        - len(input_tensor[0][0]) + 2 * pad_w >= len(weight_kernels[0][0][0])
      postconditions:
        - len(output.output_tensor) == len(weight_kernels)
        - len(output.output_tensor[0]) == output.out_height
        - len(output.output_tensor[0][0]) == output.out_width
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-68
        - ALGO-NN-69
        - ALGO-NN-70
        - ALGO-NN-71
      references:
        - lecun1998gradient
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        weight_kernels: Sequence[Sequence[Sequence[Sequence[float]]]],
        bias: Optional[Sequence[float]] = None,
        stride_h: int = 1,
        stride_w: int = 1,
        pad_h: int = 0,
        pad_w: int = 0,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")
        if not weight_kernels or not weight_kernels[0] or not weight_kernels[0][0] or not weight_kernels[0][0][0]:
            raise ValueError("Precondition failed: weight_kernels must be non-empty 4D array.")

        C_in = len(input_tensor)
        H_in = len(input_tensor[0])
        W_in = len(input_tensor[0][0])

        C_out = len(weight_kernels)
        if len(weight_kernels[0]) != C_in:
            raise ValueError("Precondition failed: kernel input channel count must match input_tensor channel count.")
        K_h = len(weight_kernels[0][0])
        K_w = len(weight_kernels[0][0][0])

        if stride_h < 1 or stride_w < 1:
            raise ValueError("Precondition failed: stride values must be >= 1.")
        if pad_h < 0 or pad_w < 0:
            raise ValueError("Precondition failed: pad values must be >= 0.")

        padded_H = H_in + 2 * pad_h
        padded_W = W_in + 2 * pad_w

        if padded_H < K_h or padded_W < K_w:
            raise ValueError("Precondition failed: padded input dimensions must be >= kernel dimensions.")

        H_out = (padded_H - K_h) // stride_h + 1
        W_out = (padded_W - K_w) // stride_w + 1

        bias_vec = list(bias) if bias is not None and len(bias) > 0 else [0.0] * C_out
        if len(bias_vec) != C_out:
            raise ValueError("Precondition failed: bias vector length must equal C_out.")

        # Construct padded input representation
        padded_input: List[List[List[float]]] = [
            [[0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C_in)
        ]
        for c in range(C_in):
            for h in range(H_in):
                for w in range(W_in):
                    padded_input[c][h + pad_h][w + pad_w] = float(input_tensor[c][h][w])

        out_tensor: List[List[List[float]]] = [
            [[bias_vec[cout]] * W_out for _ in range(H_out)]
            for cout in range(C_out)
        ]

        for cout in range(C_out):
            kernel_cout = weight_kernels[cout]
            for hout in range(H_out):
                h_start = hout * stride_h
                for wout in range(W_out):
                    w_start = wout * stride_w
                    acc = bias_vec[cout]
                    for cin in range(C_in):
                        kernel_cin = kernel_cout[cin]
                        pad_cin = padded_input[cin]
                        for kh in range(K_h):
                            for kw in range(K_w):
                                acc += kernel_cin[kh][kw] * pad_cin[h_start + kh][w_start + kw]
                    out_tensor[cout][hout][wout] = acc

        return {
            "output_tensor": out_tensor,
            "out_height": H_out,
            "out_width": W_out,
        }
