from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoDepthwiseSeparableConvolution:
    """
    ---
    contract:
      algo_id: ALGO-NN-71
      name: NnAlgoDepthwiseSeparableConvolution
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.depthwise_separable
        - nn.mobilenet
        - nn.efficient_inference
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
          depthwise_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 3D depthwise spatial kernel tensor W_dw of shape (C_in, K_h, K_w).
          pointwise_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D pointwise 1x1 projection matrix W_pw of shape (C_out, C_in).
          stride:
            type: integer
            default: 1
            description: Spatial sliding stride s >= 1 applied in the depthwise stage.
          padding:
            type: integer
            default: 0
            description: Spatial zero-padding p >= 0 applied in the depthwise stage.
          bias:
            type: array
            items:
              type: number
            description: Optional 1D pointwise bias vector of length C_out.
        required:
          - input_tensor
          - depthwise_weights
          - pointwise_weights
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
          depthwise_intermediate:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Intermediate feature tensor Z of shape (C_in, H_out, W_out) after depthwise pass.
          out_height:
            type: integer
            description: Output spatial height H_out.
          out_width:
            type: integer
            description: Output spatial width W_out.
        required:
          - output_tensor
          - depthwise_intermediate
          - out_height
          - out_width
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H_in, W_in).
        - depthwise_weights must be a 3D array of shape (C_in, K_h, K_w).
        - pointwise_weights must be a 2D array of shape (C_out, C_in).
        - stride must be >= 1; padding must be >= 0.
        - Padded input dimensions must be >= depthwise kernel dimensions.
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
          K_h: depthwise kernel height
          K_w: depthwise kernel width
        time_worst: O(C_in * H_out * W_out * (K_h * K_w + C_out))
        time_typical: O(C_in * H_out * W_out * (K_h * K_w + C_out))
        space: O(C_in * H_out * W_out + C_out * H_out * W_out)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(depthwise_weights) == len(input_tensor)
        - len(depthwise_weights[0]) > 0 and len(depthwise_weights[0][0]) > 0
        - len(pointwise_weights) > 0 and len(pointwise_weights[0]) == len(input_tensor)
        - stride >= 1 and padding >= 0
      postconditions:
        - len(output.output_tensor) == len(pointwise_weights)
        - len(output.output_tensor[0]) == output.out_height
        - len(output.output_tensor[0][0]) == output.out_width
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-73
        - ALGO-NN-76
      references:
        - howard2017mobilenets
        - chollet2017xception
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        depthwise_weights: Sequence[Sequence[Sequence[float]]],
        pointwise_weights: Sequence[Sequence[float]],
        stride: int = 1,
        padding: int = 0,
        bias: Optional[Sequence[float]] = None,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")
        if not depthwise_weights or not depthwise_weights[0] or not depthwise_weights[0][0]:
            raise ValueError("Precondition failed: depthwise_weights must be non-empty 3D array.")
        if not pointwise_weights or not pointwise_weights[0]:
            raise ValueError("Precondition failed: pointwise_weights must be non-empty 2D array.")

        C_in = len(input_tensor)
        H_in = len(input_tensor[0])
        W_in = len(input_tensor[0][0])

        if len(depthwise_weights) != C_in:
            raise ValueError("Precondition failed: depthwise channel count must match C_in.")
        K_h = len(depthwise_weights[0])
        K_w = len(depthwise_weights[0][0])

        C_out = len(pointwise_weights)
        if len(pointwise_weights[0]) != C_in:
            raise ValueError("Precondition failed: pointwise input dimension must match C_in.")

        if stride < 1 or padding < 0:
            raise ValueError("Precondition failed: stride must be >= 1 and padding >= 0.")

        padded_H = H_in + 2 * padding
        padded_W = W_in + 2 * padding

        if padded_H < K_h or padded_W < K_w:
            raise ValueError("Precondition failed: padded input dimensions must be >= kernel size.")

        H_out = (padded_H - K_h) // stride + 1
        W_out = (padded_W - K_w) // stride + 1

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

        # Step 1: Depthwise Convolution
        depthwise_intermediate: List[List[List[float]]] = [
            [[0.0] * W_out for _ in range(H_out)]
            for _ in range(C_in)
        ]
        for cin in range(C_in):
            kernel_cin = depthwise_weights[cin]
            pad_cin = padded[cin]
            for hout in range(H_out):
                h_start = hout * stride
                for wout in range(W_out):
                    w_start = wout * stride
                    acc = 0.0
                    for kh in range(K_h):
                        for kw in range(K_w):
                            acc += kernel_cin[kh][kw] * pad_cin[h_start + kh][w_start + kw]
                    depthwise_intermediate[cin][hout][wout] = acc

        # Step 2: Pointwise 1x1 Convolution
        out_tensor: List[List[List[float]]] = [
            [[bias_vec[cout]] * W_out for _ in range(H_out)]
            for cout in range(C_out)
        ]
        for cout in range(C_out):
            pw_row = pointwise_weights[cout]
            for hout in range(H_out):
                for wout in range(W_out):
                    acc = bias_vec[cout]
                    for cin in range(C_in):
                        acc += pw_row[cin] * depthwise_intermediate[cin][hout][wout]
                    out_tensor[cout][hout][wout] = acc

        return {
            "output_tensor": out_tensor,
            "depthwise_intermediate": depthwise_intermediate,
            "out_height": H_out,
            "out_width": W_out,
        }
