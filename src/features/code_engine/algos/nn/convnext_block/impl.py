"""ConvNeXt Modernized Convolutional Block Architecture.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: convnext_block
  category: neural_network_architecture
  subcategory: convolutional_networks
  id: ALGO-NN-81
  equation: |
    X_1 = \\text{DepthwiseConv}_{7 \\times 7}(X)
    X_2 = \\text{LayerNorm}(X_1)
    X_3 = \\text{Linear}_{C \\to 4C}(X_2)
    X_4 = \\text{GELU}(X_3)
    X_5 = \\text{Linear}_{4C \\to C}(X_4)
    Y = X + \\gamma \\odot X_5
  domain:
    input_shape: "3D tensor [C, H, W]"
    expansion_factor: 4
    kernel_size: 7
  properties:
    inverted_bottleneck: true
    large_kernel_depthwise: true
    layer_norm_channels_last: true
    layer_scale_stabilized: true
"""

from typing import List, Optional, Tuple
import math


class ConvNeXtBlock:
    """Modernized Pure-Convolutional Block matching Vision Transformer design principles."""

    @staticmethod
    def gelu(x: float) -> float:
        """GELU (Gaussian Error Linear Unit) standard approximation."""
        return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def layer_norm_channels(
        x: List[List[List[float]]],
        gamma: Optional[List[float]] = None,
        beta: Optional[List[float]] = None,
        eps: float = 1e-6
    ) -> List[List[List[float]]]:
        """Apply LayerNorm across the channel dimension at each spatial location (channels-last LN).

        Args:
            x: Feature map [C, H, W].
            gamma: Scale parameter vector of length C.
            beta: Bias parameter vector of length C.
            eps: Numerical stability constant.

        Returns:
            Normalized tensor [C, H, W].
        """
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])

        out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c)]
        for i in range(h):
            for j in range(w):
                # Compute spatial-pixel mean and variance across channels
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
        bias: Optional[List[float]] = None
    ) -> List[List[List[float]]]:
        """7x7 depthwise convolution with symmetric padding=3.

        Args:
            x: Input feature map [C, H, W].
            weights: Per-channel 7x7 filters of shape [C, 7, 7].
            bias: Optional bias vector of length C.

        Returns:
            Filtered output [C, H, W].
        """
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])
        assert len(weights) == c and len(weights[0]) == 7 and len(weights[0][0]) == 7, "Weights must be [C, 7, 7]."

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
        bias: Optional[List[float]] = None
    ) -> List[List[List[float]]]:
        """Pointwise 1x1 linear transformation [C_in, H, W] -> [C_out, H, W].

        Args:
            x: Input feature map [C_in, H, W].
            weight: Matrix [C_out, C_in].
            bias: Optional bias vector [C_out].

        Returns:
            Output tensor [C_out, H, W].
        """
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])
        c_out = len(weight)
        assert len(weight[0]) == c_in, "Weight matrix inner dimension must match C_in."

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
        layer_scale: Optional[List[float]] = None
    ) -> List[List[List[float]]]:
        """Execute full ConvNeXt block forward transformation.

        Workflow:
          1. 7x7 Depthwise conv
          2. LayerNorm
          3. Pointwise 1 (C -> 4C)
          4. GELU
          5. Pointwise 2 (4C -> C)
          6. LayerScale scaling
          7. Residual addition

        Args:
            x: Input tensor [C, H, W].
            dw_weight: 7x7 Depthwise weights [C, 7, 7].
            pw1_weight: Inverted bottleneck expansion [4C, C].
            pw2_weight: Projection contraction [C, 4C].
            dw_bias, pw1_bias, pw2_bias: Optional bias vectors.
            ln_gamma, ln_beta: LayerNorm parameters.
            layer_scale: Per-channel scale multipliers of length C.

        Returns:
            Output tensor of shape [C, H, W].
        """
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])

        # 1. 7x7 Depthwise Conv
        out_dw = ConvNeXtBlock.depthwise_conv7x7(x, dw_weight, dw_bias)

        # 2. LayerNorm (channels-last style)
        out_ln = ConvNeXtBlock.layer_norm_channels(out_dw, ln_gamma, ln_beta)

        # 3. 1x1 Conv (C -> 4C)
        out_pw1 = ConvNeXtBlock.pointwise_linear(out_ln, pw1_weight, pw1_bias)

        # 4. GELU activation
        c_exp = len(out_pw1)
        out_gelu = [[[ConvNeXtBlock.gelu(out_pw1[ci][i][j]) for j in range(w)] for i in range(h)] for ci in range(c_exp)]

        # 5. 1x1 Conv (4C -> C)
        out_pw2 = ConvNeXtBlock.pointwise_linear(out_gelu, pw2_weight, pw2_bias)

        # 6 & 7. LayerScale and Residual connection
        y = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c)]
        for ch in range(c):
            scale = layer_scale[ch] if layer_scale is not None else 1.0
            for i in range(h):
                for j in range(w):
                    y[ch][i][j] = x[ch][i][j] + scale * out_pw2[ch][i][j]

        return y
