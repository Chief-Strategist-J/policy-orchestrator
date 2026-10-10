from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoUnetEncoderDecoder:
    """
    ---
    contract:
      algo_id: ALGO-NN-79
      name: NnAlgoUnetEncoderDecoder
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.unet
        - nn.encoder_decoder
        - nn.skip_connections
        - nn.segmentation
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
            description: 3D input image tensor X of shape (C_in, H, W).
          enc1_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel for Encoder level 1 convolution (C_1, C_in, 3, 3).
          enc2_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel for Encoder level 2 convolution (C_2, C_1, 3, 3).
          dec1_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D weight kernel for Decoder fusion convolution (C_out, C_2 + C_1, 3, 3).
        required:
          - input_tensor
          - enc1_weights
          - enc2_weights
          - dec1_weights
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
            description: 3D segmentation map output tensor of shape (C_out, H, W).
          skip_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: High-resolution skip feature map from Encoder level 1 of shape (C_1, H, W).
          bottleneck_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Low-resolution bottleneck feature map from Encoder level 2 of shape (C_2, H/2, W/2).
        required:
          - output_tensor
          - skip_tensor
          - bottleneck_tensor
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C_in, H, W) where H and W are even.
        - Kernel weights must match specified channel dimensions.
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
          C_1: level 1 channels
          C_2: level 2 bottleneck channels
          C_out: output channels
          H: height
          W: width
        time_worst: O(H * W * (C_in * C_1 + C_1 * C_2 + (C_2 + C_1) * C_out))
        time_typical: O(H * W * (C_in * C_1 + C_1 * C_2 + (C_2 + C_1) * C_out))
        space: O(H * W * (C_1 + C_out) + (H/2) * (W/2) * C_2)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(input_tensor[0]) % 2 == 0 and len(input_tensor[0][0]) % 2 == 0
        - len(enc1_weights) > 0 and len(enc1_weights[0]) == len(input_tensor)
        - len(enc2_weights) > 0 and len(enc2_weights[0]) == len(enc1_weights)
        - len(dec1_weights) > 0 and len(dec1_weights[0]) == len(enc2_weights) + len(enc1_weights)
      postconditions:
        - len(output.output_tensor) == len(dec1_weights)
        - len(output.output_tensor[0]) == len(input_tensor[0])
        - len(output.output_tensor[0][0]) == len(input_tensor[0][0])
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-72
        - ALGO-NN-80
      references:
        - "https://doi.org/10.1007/978-3-319-24574-4_28"
    ---
    """

    @staticmethod
    def _conv2d_same(
        x: Sequence[Sequence[Sequence[float]]],
        w: Sequence[Sequence[Sequence[Sequence[float]]]],
    ) -> List[List[List[float]]]:
        C_in = len(x)
        H = len(x[0])
        W = len(x[0][0])
        C_out = len(w)
        K_h = len(w[0][0])
        K_w = len(w[0][0][0])
        pad_h = K_h // 2
        pad_w = K_w // 2

        padded = [
            [[0.0] * (W + 2 * pad_w) for _ in range(H + 2 * pad_h)]
            for _ in range(C_in)
        ]
        for c in range(C_in):
            for h in range(H):
                for w_idx in range(W):
                    padded[c][h + pad_h][w_idx + pad_w] = float(x[c][h][w_idx])

        out: List[List[List[float]]] = [[[0.0] * W for _ in range(H)] for _ in range(C_out)]
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
                    out[cout][h][w_idx] = max(0.0, acc)
        return out

    @staticmethod
    def _maxpool2x2(x: Sequence[Sequence[Sequence[float]]]) -> List[List[List[float]]]:
        C = len(x)
        H = len(x[0])
        W = len(x[0][0])
        H_out = H // 2
        W_out = W // 2
        out = [[[0.0] * W_out for _ in range(H_out)] for _ in range(C)]
        for c in range(C):
            for h in range(H_out):
                for w in range(W_out):
                    out[c][h][w] = max(
                        x[c][2 * h][2 * w],
                        x[c][2 * h + 1][2 * w],
                        x[c][2 * h][2 * w + 1],
                        x[c][2 * h + 1][2 * w + 1],
                    )
        return out

    @staticmethod
    def _nearest_upsample2x(x: Sequence[Sequence[Sequence[float]]]) -> List[List[List[float]]]:
        C = len(x)
        H = len(x[0])
        W = len(x[0][0])
        H_out = H * 2
        W_out = W * 2
        out = [[[0.0] * W_out for _ in range(H_out)] for _ in range(C)]
        for c in range(C):
            for h in range(H_out):
                hin = h // 2
                for w in range(W_out):
                    win = w // 2
                    out[c][h][w] = float(x[c][hin][win])
        return out

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        enc1_weights: Sequence[Sequence[Sequence[Sequence[float]]]],
        enc2_weights: Sequence[Sequence[Sequence[Sequence[float]]]],
        dec1_weights: Sequence[Sequence[Sequence[Sequence[float]]]],
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        H = len(input_tensor[0])
        W = len(input_tensor[0][0])

        if H % 2 != 0 or W % 2 != 0:
            raise ValueError("Precondition failed: input spatial dimensions must be even numbers.")

        skip_tensor = NnAlgoUnetEncoderDecoder._conv2d_same(input_tensor, enc1_weights)

        pooled_1 = NnAlgoUnetEncoderDecoder._maxpool2x2(skip_tensor)

        bottleneck_tensor = NnAlgoUnetEncoderDecoder._conv2d_same(pooled_1, enc2_weights)

        upsampled = NnAlgoUnetEncoderDecoder._nearest_upsample2x(bottleneck_tensor)

        fused_channels: List[List[List[float]]] = []
        for ch in upsampled:
            fused_channels.append(ch)
        for ch in skip_tensor:
            fused_channels.append(ch)

        output_tensor = NnAlgoUnetEncoderDecoder._conv2d_same(fused_channels, dec1_weights)

        return {
            "output_tensor": output_tensor,
            "skip_tensor": skip_tensor,
            "bottleneck_tensor": bottleneck_tensor,
        }
