from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoTransposedConvolutionPixelShuffle:
    """
    ---
    contract:
      algo_id: ALGO-NN-72
      name: NnAlgoTransposedConvolutionPixelShuffle
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.transposed_conv
        - nn.pixel_shuffle
        - nn.upsampling
        - nn.super_resolution
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
            description: 3D input tensor X of shape (C_in, H_in, W_in).
          mode:
            type: string
            enum:
              - transposed_conv
              - pixel_shuffle
            default: transposed_conv
            description: Upsampling mode ('transposed_conv' for learned fractionally strided conv, 'pixel_shuffle' for sub-pixel periodic rearrangement).
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
            description: 4D filter weight tensor W of shape (C_in, C_out, K_h, K_w) required for transposed_conv mode.
          stride:
            type: integer
            default: 2
            description: Spatial stride s >= 1 for transposed_conv.
          padding:
            type: integer
            default: 0
            description: Spatial zero-padding p >= 0 for transposed_conv.
          upscale_factor:
            type: integer
            default: 2
            description: Spatial magnification factor r >= 1 for pixel_shuffle mode (requires C_in % (r^2) == 0).
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
            description: 3D upsampled output tensor Y of shape (C_out, H_out, W_out).
          out_height:
            type: integer
            description: Output spatial height H_out.
          out_width:
            type: integer
            description: Output spatial width W_out.
        required:
          - output_tensor
          - out_height
          - out_width
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - In pixel_shuffle mode, C_in must be divisible by upscale_factor^2.
        - In transposed_conv mode, weight_kernels must have shape (C_in, C_out, K_h, K_w).
        - stride must be >= 1; upscale_factor must be >= 1.
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
        time_worst: O(C_in * C_out * H_out * W_out * K_h * K_w)
        time_typical: O(C_in * C_out * H_out * W_out * K_h * K_w)
        space: O(C_out * H_out * W_out)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - mode in ["transposed_conv", "pixel_shuffle"]
        - stride >= 1
        - upscale_factor >= 1
      postconditions:
        - len(output.output_tensor) > 0
        - len(output.output_tensor[0]) == output.out_height
        - len(output.output_tensor[0][0]) == output.out_width
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-79
      references:
        - shi2016real
        - dumoulin2016guide
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        mode: Literal["transposed_conv", "pixel_shuffle"] = "transposed_conv",
        weight_kernels: Optional[Sequence[Sequence[Sequence[Sequence[float]]]]] = None,
        stride: int = 2,
        padding: int = 0,
        upscale_factor: int = 2,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        C_in = len(input_tensor)
        H_in = len(input_tensor[0])
        W_in = len(input_tensor[0][0])

        for c_idx in range(C_in):
            if len(input_tensor[c_idx]) != H_in:
                raise ValueError("Precondition failed: inconsistent height across channels.")
            for h_idx in range(H_in):
                if len(input_tensor[c_idx][h_idx]) != W_in:
                    raise ValueError("Precondition failed: inconsistent width across rows.")

        if mode not in ["transposed_conv", "pixel_shuffle"]:
            raise ValueError("Precondition failed: mode must be 'transposed_conv' or 'pixel_shuffle'.")

        if mode == "pixel_shuffle":
            r = upscale_factor
            if r < 1:
                raise ValueError("Precondition failed: upscale_factor must be >= 1.")
            r2 = r * r
            if C_in % r2 != 0:
                raise ValueError("Precondition failed: C_in must be divisible by upscale_factor^2.")

            C_out = C_in // r2
            H_out = H_in * r
            W_out = W_in * r

            out_tensor: List[List[List[float]]] = [
                [[0.0] * W_out for _ in range(H_out)]
                for _ in range(C_out)
            ]

            for cout in range(C_out):
                for hin in range(H_in):
                    for win in range(W_in):
                        for v in range(r):
                            for u in range(r):
                                cin = cout * r2 + v * r + u
                                hout = hin * r + v
                                wout = win * r + u
                                out_tensor[cout][hout][wout] = float(input_tensor[cin][hin][win])

            return {
                "output_tensor": out_tensor,
                "out_height": H_out,
                "out_width": W_out,
            }

        else:
            # transposed_conv mode
            if not weight_kernels or not weight_kernels[0] or not weight_kernels[0][0] or not weight_kernels[0][0][0]:
                raise ValueError("Precondition failed: weight_kernels required for transposed_conv mode.")

            if len(weight_kernels) != C_in:
                raise ValueError("Precondition failed: weight_kernels dim 0 must match C_in.")

            C_out = len(weight_kernels[0])
            K_h = len(weight_kernels[0][0])
            K_w = len(weight_kernels[0][0][0])

            if stride < 1 or padding < 0:
                raise ValueError("Precondition failed: stride must be >= 1 and padding >= 0.")

            H_out = (H_in - 1) * stride - 2 * padding + K_h
            W_out = (W_in - 1) * stride - 2 * padding + K_w

            if H_out <= 0 or W_out <= 0:
                raise ValueError("Precondition failed: computed H_out and W_out must be > 0.")

            out_tensor = [[[0.0] * W_out for _ in range(H_out)] for _ in range(C_out)]

            for cin in range(C_in):
                for cout in range(C_out):
                    kernel = weight_kernels[cin][cout]
                    for hin in range(H_in):
                        h_top = hin * stride - padding
                        for win in range(W_in):
                            w_left = win * stride - padding
                            x_val = input_tensor[cin][hin][win]
                            for kh in range(K_h):
                                h_pos = h_top + kh
                                if 0 <= h_pos < H_out:
                                    for kw in range(K_w):
                                        w_pos = w_left + kw
                                        if 0 <= w_pos < W_out:
                                            out_tensor[cout][h_pos][w_pos] += x_val * kernel[kh][kw]

            return {
                "output_tensor": out_tensor,
                "out_height": H_out,
                "out_width": W_out,
            }
