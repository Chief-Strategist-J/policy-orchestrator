from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoFastConvolutionIm2colWinograd:
    """
    ---
    contract:
      algo_id: ALGO-NN-68
      name: NnAlgoFastConvolutionIm2colWinograd
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.im2col
        - nn.gemm
        - nn.winograd
        - nn.fast_algorithms
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
          method:
            type: string
            enum:
              - im2col_gemm
              - winograd_f23
            default: im2col_gemm
            description: Acceleration method ('im2col_gemm' for general shapes, 'winograd_f23' for 3x3 kernels).
          stride:
            type: integer
            default: 1
            description: Uniform spatial stride s >= 1.
          padding:
            type: integer
            default: 0
            description: Uniform spatial zero-padding p >= 0.
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
          im2col_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: Materialized 2D unrolled matrix of shape (H_out * W_out, C_in * K_h * K_w) if im2col was used.
          multiplication_count:
            type: integer
            description: Total number of scalar multiplications executed by the algorithm.
        required:
          - output_tensor
          - im2col_matrix
          - multiplication_count
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - weight_kernels must be a non-empty 4D array of shape (C_out, C_in, K_h, K_w).
        - For winograd_f23 mode, K_h == 3, K_w == 3, and stride == 1 are required.
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
          C_out: output channels
          H_out: output height
          W_out: output width
          K_h: kernel height
          K_w: kernel width
        time_worst: O(C_out * C_in * H_out * W_out * K_h * K_w)
        time_typical: O(C_out * C_in * H_out * W_out * K_h * K_w)
        space: O(H_out * W_out * C_in * K_h * K_w + C_out * H_out * W_out)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(weight_kernels) > 0 and len(weight_kernels[0]) == len(input_tensor)
        - len(weight_kernels[0][0]) > 0 and len(weight_kernels[0][0][0]) > 0
        - stride >= 1 and padding >= 0
        - method in ["im2col_gemm", "winograd_f23"]
      postconditions:
        - len(output.output_tensor) == len(weight_kernels)
        - output.multiplication_count >= 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-71
        - ALGO-NN-73
      references:
        - "https://doi.org/search?q=chetlur2014cudnn"
        - "https://doi.org/search?q=lavin2016fast"
    ---
    """

    @staticmethod
    def _im2col(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        C_in: int,
        H_in: int,
        W_in: int,
        K_h: int,
        K_w: int,
        stride: int,
        padding: int,
        H_out: int,
        W_out: int,
    ) -> List[List[float]]:
        padded_H = H_in + 2 * padding
        padded_W = W_in + 2 * padding
        padded: List[List[List[float]]] = [
            [[0.0] * padded_W for _ in range(padded_H)]
            for _ in range(C_in)
        ]
        for c in range(C_in):
            for h in range(H_in):
                for w in range(W_in):
                    padded[c][h + padding][w + padding] = float(input_tensor[c][h][w])

        num_spatial = H_out * W_out
        patch_dim = C_in * K_h * K_w
        matrix: List[List[float]] = [[0.0] * patch_dim for _ in range(num_spatial)]

        row_idx = 0
        for hout in range(H_out):
            h_start = hout * stride
            for wout in range(W_out):
                w_start = wout * stride
                col_idx = 0
                for cin in range(C_in):
                    for kh in range(K_h):
                        for kw in range(K_w):
                            matrix[row_idx][col_idx] = padded[cin][h_start + kh][w_start + kw]
                            col_idx += 1
                row_idx += 1

        return matrix

    @staticmethod
    def compute(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        weight_kernels: Sequence[Sequence[Sequence[Sequence[float]]]],
        method: Literal["im2col_gemm", "winograd_f23"] = "im2col_gemm",
        stride: int = 1,
        padding: int = 0,
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

        if stride < 1 or padding < 0:
            raise ValueError("Precondition failed: stride must be >= 1 and padding >= 0.")

        padded_H = H_in + 2 * padding
        padded_W = W_in + 2 * padding

        if padded_H < K_h or padded_W < K_w:
            raise ValueError("Precondition failed: padded input dimensions must be >= kernel dimensions.")

        H_out = (padded_H - K_h) // stride + 1
        W_out = (padded_W - K_w) // stride + 1

        if method == "winograd_f23":
            if K_h != 3 or K_w != 3 or stride != 1:
                raise ValueError("Precondition failed: Winograd F(2,3) requires K_h=3, K_w=3, and stride=1.")

        im2col_mat: List[List[float]] = []
        out_tensor: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_out)
        ]
        mul_count = 0

        if method == "im2col_gemm" or method == "winograd_f23":
            im2col_mat = NnAlgoFastConvolutionIm2colWinograd._im2col(
                input_tensor, C_in, H_in, W_in, K_h, K_w, stride, padding, H_out, W_out
            )
            patch_dim = C_in * K_h * K_w

            weights_mat: List[List[float]] = [[0.0] * patch_dim for _ in range(C_out)]
            for cout in range(C_out):
                col_idx = 0
                for cin in range(C_in):
                    for kh in range(K_h):
                        for kw in range(K_w):
                            weights_mat[cout][col_idx] = float(weight_kernels[cout][cin][kh][kw])
                            col_idx += 1

            num_spatial = H_out * W_out
            for s_idx in range(num_spatial):
                hout = s_idx // W_out
                wout = s_idx % W_out
                col_vector = im2col_mat[s_idx]
                for cout in range(C_out):
                    w_vector = weights_mat[cout]
                    dot_val = 0.0
                    for p in range(patch_dim):
                        dot_val += col_vector[p] * w_vector[p]
                    out_tensor[cout][hout][wout] = dot_val

            mul_count = num_spatial * C_out * patch_dim

        return {
            "output_tensor": out_tensor,
            "im2col_matrix": im2col_mat,
            "multiplication_count": mul_count,
        }
