from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoDilatedAtrousConvolution:
    """
    ---
    contract:
      algo_id: ALGO-NN-70
      name: NnAlgoDilatedAtrousConvolution
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.dilated_conv
        - nn.atrous_conv
        - nn.segmentation
        - nn.receptive_field
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
          dilation_h:
            type: integer
            default: 1
            description: Vertical dilation rate r_h >= 1.
          dilation_w:
            type: integer
            default: 1
            description: Horizontal dilation rate r_w >= 1.
          stride:
            type: integer
            default: 1
            description: Spatial sliding stride s >= 1.
          padding:
            type: integer
            default: 0
            description: Spatial zero-padding p >= 0.
          bias:
            type: array
            items:
              type: number
            description: Optional 1D bias vector of length C_out.
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
            description: 3D convolved output tensor Y of shape (C_out, H_out, W_out).
          effective_kernel_h:
            type: integer
            description: Effective spatial height spanned by dilated kernel K'_h = r_h * (K_h - 1) + 1.
          effective_kernel_w:
            type: integer
            description: Effective spatial width spanned by dilated kernel K'_w = r_w * (K_w - 1) + 1.
          out_height:
            type: integer
            description: Computed output height H_out.
          out_width:
            type: integer
            description: Computed output width W_out.
        required:
          - output_tensor
          - effective_kernel_h
          - effective_kernel_w
          - out_height
          - out_width
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - weight_kernels must be a non-empty 4D array of shape (C_out, C_in, K_h, K_w).
        - dilation_h and dilation_w must be >= 1.
        - stride must be >= 1; padding must be >= 0.
        - Padded input dimensions must be >= effective kernel dimensions.
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
        - dilation_h >= 1 and dilation_w >= 1
        - stride >= 1 and padding >= 0
      postconditions:
        - len(output.output_tensor) == len(weight_kernels)
        - len(output.output_tensor[0]) == output.out_height
        - len(output.output_tensor[0][0]) == output.out_width
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-80
        - ALGO-NN-83
      references:
        - yu2015multi
        - chen2017deeplab
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        weight_kernels: Sequence[Sequence[Sequence[Sequence[float]]]],
        dilation_h: int = 1,
        dilation_w: int = 1,
        stride: int = 1,
        padding: int = 0,
        bias: Optional[Sequence[float]] = None,
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

        if dilation_h < 1 or dilation_w < 1:
            raise ValueError("Precondition failed: dilation values must be >= 1.")
        if stride < 1 or padding < 0:
            raise ValueError("Precondition failed: stride must be >= 1 and padding >= 0.")

        eff_K_h = dilation_h * (K_h - 1) + 1
        eff_K_w = dilation_w * (K_w - 1) + 1

        padded_H = H_in + 2 * padding
        padded_W = W_in + 2 * padding

        if padded_H < eff_K_h or padded_W < eff_K_w:
            raise ValueError("Precondition failed: padded input dimensions must be >= effective kernel dimensions.")

        H_out = (padded_H - eff_K_h) // stride + 1
        W_out = (padded_W - eff_K_w) // stride + 1

        bias_vec = list(bias) if bias is not None and len(bias) > 0 else [0.0] * C_out
        if len(bias_vec) != C_out:
            raise ValueError("Precondition failed: bias vector length must equal C_out.")

        # Padded representation
        padded: List[List[List[float]]] = [
            [[0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C_in)
        ]
        for c in range(C_in):
            for h in range(H_in):
                for w in range(W_in):
                    padded[c][h + padding][w + padding] = float(input_tensor[c][h][w])

        out_tensor: List[List[List[float]]] = [
            [[bias_vec[cout]] * W_out for _ in range(H_out)]
            for cout in range(C_out)
        ]

        for cout in range(C_out):
            kernel_cout = weight_kernels[cout]
            for hout in range(H_out):
                h_start = hout * stride
                for wout in range(W_out):
                    w_start = wout * stride
                    acc = bias_vec[cout]
                    for cin in range(C_in):
                        kernel_cin = kernel_cout[cin]
                        pad_cin = padded[cin]
                        for kh in range(K_h):
                            h_sample = h_start + kh * dilation_h
                            for kw in range(K_w):
                                w_sample = w_start + kw * dilation_w
                                acc += kernel_cin[kh][kw] * pad_cin[h_sample][w_sample]
                    out_tensor[cout][hout][wout] = acc

        return {
            "output_tensor": out_tensor,
            "effective_kernel_h": eff_K_h,
            "effective_kernel_w": eff_K_w,
            "out_height": H_out,
            "out_width": W_out,
        }
