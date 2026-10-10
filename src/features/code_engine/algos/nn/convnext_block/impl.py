from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoConvNeXtBlock:
    """
    ---
    contract:
      algo_id: ALGO-NN-81
      name: NnAlgoConvNeXtBlock
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.modern_cnn
        - nn.vision_transformer_parity
        - nn.residual
      inputs:
        type: object
        required:
          - x
          - dw_weight
          - pw1_weight
          - pw2_weight
        properties:
          x:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Input feature map tensor of shape (C, H, W).
          dw_weight:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 7x7 Depthwise convolution weights of shape (C, 7, 7).
          pw1_weight:
            type: array
            items:
              type: array
              items:
                type: number
            description: First 1x1 inverted bottleneck expansion matrix of shape (4C, C).
          pw2_weight:
            type: array
            items:
              type: array
              items:
                type: number
            description: Second 1x1 contraction projection matrix of shape (C, 4C).
          dw_bias:
            type: array
            items:
              type: number
            description: Optional depthwise bias of length C.
          pw1_bias:
            type: array
            items:
              type: number
            description: Optional expansion bias of length 4C.
          pw2_bias:
            type: array
            items:
              type: number
            description: Optional contraction bias of length C.
          ln_gamma:
            type: array
            items:
              type: number
            description: Optional LayerNorm scale parameters of length C.
          ln_beta:
            type: array
            items:
              type: number
            description: Optional LayerNorm bias parameters of length C.
          layer_scale:
            type: array
            items:
              type: number
            description: Optional LayerScale multiplier vector gamma of length C.
      outputs:
        type: object
        required:
          - output
        properties:
          output:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Output residual block tensor Y of shape (C, H, W).
      parameters: {}
      input_assumptions:
        - x is a non-empty 3D tensor of shape [C, H, W]
        - dw_weight has shape [C, 7, 7]
        - pw1_weight has shape [4C, C] and pw2_weight has shape [C, 4C]
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Bounded by numerical precision of GELU and LayerNorm implementations"
      uses_model: false
      complexity:
        variables:
          C: channel capacity
          H: height
          W: width
        time_worst: "O((49 * C + 8 * C^2) * H * W)"
        time_typical: "O((49 * C + 8 * C^2) * H * W)"
        space: "O(4 * C * H * W)"
      preconditions:
        - len(input.x) > 0 and len(input.x[0]) > 0 and len(input.x[0][0]) > 0
        - len(input.dw_weight) == len(input.x) and len(input.dw_weight[0]) == 7 and len(input.dw_weight[0][0]) == 7
        - len(input.pw1_weight) == 4 * len(input.x) and len(input.pw1_weight[0]) == len(input.x)
        - len(input.pw2_weight) == len(input.x) and len(input.pw2_weight[0]) == 4 * len(input.x)
      postconditions:
        - len(output.output) == len(input.x)
        - len(output.output[0]) == len(input.x[0])
        - len(output.output[0][0]) == len(input.x[0][0])
      certificate: "Y = X + gamma * W2(GELU(W1(LayerNorm(DepthwiseConv7x7(X)))))"
      compatible_adapters:
        - ADAPTER-CONVNEXT
        - ADAPTER-VISION-BACKBONE
      related_algos:
        - ALGO-NN-71
        - ALGO-NN-76
        - ALGO-NN-52
      references:
        - "https://doi.org/10.1109/CVPR52688.2022.01167"
        - "https://arxiv.org/abs/2201.03545"
    ---
    """

    @staticmethod
    def gelu(x: float) -> float:
        return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def layer_norm_channels(
        x: List[List[List[float]]],
        gamma: Optional[List[float]] = None,
        beta: Optional[List[float]] = None,
        eps: float = 1e-6,
    ) -> List[List[List[float]]]:
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])

        out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c)]
        for i in range(h):
            for j in range(w):
                vals = [x[ch][i][j] for ch in range(c)]
                mean = sum(vals) / c
                var = sum((v - mean) ** 2 for v in vals) / c
                std = math.sqrt(var + eps)

                for ch in range(c):
                    g = gamma[ch] if gamma is not None else 1.0
                    b = beta[ch] if beta is not None else 0.0
                    out[ch][i][j] = ((x[ch][i][j] - mean) / std) * g + b
        return out

    @staticmethod
    def depthwise_conv7x7(
        x: List[List[List[float]]],
        weights: List[List[List[float]]],
        bias: Optional[List[float]] = None,
    ) -> List[List[List[float]]]:
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])
        if len(weights) != c or len(weights[0]) != 7 or len(weights[0][0]) != 7:
            raise ValueError("Precondition failed: weights must be [C, 7, 7]")

        out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c)]
        pad = 3
        for ch in range(c):
            b_val = bias[ch] if bias is not None else 0.0
            w_kernel = weights[ch]
            for i in range(h):
                for j in range(w):
                    s = b_val
                    for di in range(7):
                        ni = i + di - pad
                        if 0 <= ni < h:
                            for dj in range(7):
                                nj = j + dj - pad
                                if 0 <= nj < w:
                                    s += w_kernel[di][dj] * x[ch][ni][nj]
                    out[ch][i][j] = s
        return out

    @staticmethod
    def pointwise_linear(
        x: List[List[List[float]]],
        weight: List[List[float]],
        bias: Optional[List[float]] = None,
    ) -> List[List[List[float]]]:
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])
        c_out = len(weight)
        if len(weight[0]) != c_in:
            raise ValueError("Precondition failed: weight matrix inner dimension must match C_in")

        out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c_out)]
        for co in range(c_out):
            b_val = bias[co] if bias is not None else 0.0
            w_row = weight[co]
            for i in range(h):
                for j in range(w):
                    val = b_val
                    for ci in range(c_in):
                        val += w_row[ci] * x[ci][i][j]
                    out[co][i][j] = val
        return out

    @staticmethod
    def forward(
        x: List[List[List[float]]],
        dw_weight: List[List[List[float]]],
        pw1_weight: List[List[float]],
        pw2_weight: List[List[float]],
        dw_bias: Optional[List[float]] = None,
        pw1_bias: Optional[List[float]] = None,
        pw2_bias: Optional[List[float]] = None,
        ln_gamma: Optional[List[float]] = None,
        ln_beta: Optional[List[float]] = None,
        layer_scale: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not x or len(x) == 0 or len(x[0]) == 0 or len(x[0][0]) == 0:
            raise ValueError("Precondition failed: x must be non-empty [C, H, W]")
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])

        out_dw = NnAlgoConvNeXtBlock.depthwise_conv7x7(x, dw_weight, dw_bias)
        out_ln = NnAlgoConvNeXtBlock.layer_norm_channels(out_dw, ln_gamma, ln_beta)
        out_pw1 = NnAlgoConvNeXtBlock.pointwise_linear(out_ln, pw1_weight, pw1_bias)

        c_exp = len(out_pw1)
        out_gelu = [
            [[NnAlgoConvNeXtBlock.gelu(out_pw1[ci][i][j]) for j in range(w)] for i in range(h)]
            for ci in range(c_exp)
        ]

        out_pw2 = NnAlgoConvNeXtBlock.pointwise_linear(out_gelu, pw2_weight, pw2_bias)

        y = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c)]
        for ch in range(c):
            scale = layer_scale[ch] if layer_scale is not None else 1.0
            for i in range(h):
                for j in range(w):
                    y[ch][i][j] = x[ch][i][j] + scale * out_pw2[ch][i][j]

        return {"output": y}
