"""Temporal Convolutional Networks (TCN) with Dilated Causal Residual Blocks.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: temporal_convolutional_network
  category: neural_network_architecture
  subcategory: sequence_models
  id: ALGO-NN-100
  equation: |
    y_t = \\sum_{k=0}^{K-1} W[k] \\cdot x_{t - d \\cdot k} \\quad \\text{where } d = 2^l
    z_t = \\tanh(W_f *_{d} x)_t \\odot \\sigma(W_g *_{d} x)_t
    \\text{ReceptiveField} = 1 + \\sum_{l=0}^{L-1} (K - 1) \\cdot 2^l = 1 + (K - 1)(2^L - 1)
  domain:
    sequence_length: T
    dilation_factor: "d = 2^l \\ge 1"
    kernel_size: K >= 2
    hidden_channels: C
  properties:
    strictly_causal_no_future_leakage: true
    exponential_receptive_field_growth: true
    parallel_temporal_training: true
    gated_residual_connections: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class TemporalConvolutionalNetwork:
    """Temporal Convolutional Network (TCN) Causal Dilated Residual Block Engine."""

    @staticmethod
    def sigmoid(x: float) -> float:
        """Stable scalar sigmoid function."""
        if x >= 0:
            z = math.exp(-x)
            return 1.0 / (1.0 + z)
        else:
            z = math.exp(x)
            return z / (1.0 + z)

    @staticmethod
    def causal_dilated_conv1d(
        x_seq: List[List[float]],
        weight: List[List[List[float]]],
        bias: Optional[List[float]] = None,
        dilation: int = 1
    ) -> List[List[float]]:
        """Compute 1D Causal Dilated Convolution across temporal sequence.

        Output at time t depends only on inputs at t, t - d, t - 2d, ..., t - (K-1)*d.
        Causal left-padding ensures output length equals input length T.

        Args:
            x_seq: Input sequence of shape [T, C_in].
            weight: Filter kernel of shape [C_out, C_in, K].
            bias: Optional bias vector of length C_out.
            dilation: Dilation factor d >= 1.

        Returns:
            Output sequence of shape [T, C_out].
        """
        t_steps = len(x_seq)
        c_in = len(x_seq[0])
        c_out = len(weight)
        k_size = len(weight[0][0])
        assert len(weight[0]) == c_in, "Kernel C_in mismatch."

        out_seq = [[0.0 for _ in range(c_out)] for _ in range(t_steps)]

        for t in range(t_steps):
            for co in range(c_out):
                val = bias[co] if bias is not None else 0.0
                for k in range(k_size):
                    # Causal historical index
                    src_t = t - (k_size - 1 - k) * dilation
                    if src_t >= 0:
                        x_vec = x_seq[src_t]
                        for ci in range(c_in):
                            val += weight[co][ci][k] * x_vec[ci]
                out_seq[t][co] = val

        return out_seq

    @staticmethod
    def gated_residual_block(
        x_seq: List[List[float]],
        w_filter: List[List[List[float]]],
        w_gate: List[List[List[float]]],
        w_res: List[List[float]],
        dilation: int = 1,
        b_filter: Optional[List[float]] = None,
        b_gate: Optional[List[float]] = None,
        b_res: Optional[List[float]] = None
    ) -> List[List[float]]:
        """Execute a WaveNet/TCN style Gated Dilated Residual Block.

        Formula:
          f_t = tanh(Conv_dilated(x; W_filter))
          g_t = sigmoid(Conv_dilated(x; W_gate))
          z_t = f_t * g_t
          y_t = x_t + 1x1_Conv(z_t)

        Args:
            x_seq: Input sequence [T, C].
            w_filter, w_gate: Dilated conv weights [C, C, K].
            w_res: 1x1 residual projection matrix [C, C].
            dilation: Dilation rate d.
            b_filter, b_gate, b_res: Optional biases.

        Returns:
            Residual output sequence [T, C].
        """
        t_steps = len(x_seq)
        c = len(x_seq[0])

        # 1. Dilated convolutions for filter and gate branches
        conv_f = TemporalConvolutionalNetwork.causal_dilated_conv1d(x_seq, w_filter, b_filter, dilation)
        conv_g = TemporalConvolutionalNetwork.causal_dilated_conv1d(x_seq, w_gate, b_gate, dilation)

        # 2. Gated non-linearity: z = tanh(f) * sigmoid(g)
        z_seq = [[0.0 for _ in range(c)] for _ in range(t_steps)]
        for t in range(t_steps):
            for ch in range(c):
                f_val = math.tanh(conv_f[t][ch])
                g_val = TemporalConvolutionalNetwork.sigmoid(conv_g[t][ch])
                z_seq[t][ch] = f_val * g_val

        # 3. 1x1 Linear projection + Residual addition
        out_seq = [[0.0 for _ in range(c)] for _ in range(t_steps)]
        for t in range(t_steps):
            for co in range(c):
                res_val = b_res[co] if b_res is not None else 0.0
                for ci in range(c):
                    res_val += w_res[co][ci] * z_seq[t][ci]
                out_seq[t][co] = x_seq[t][co] + res_val

        return out_seq

    @staticmethod
    def compute_receptive_field(num_layers: int, kernel_size: int) -> int:
        """Compute theoretical receptive field for a stack of L layers with dilation doubling d = 2^l."""
        assert num_layers >= 1 and kernel_size >= 2
        return 1 + (kernel_size - 1) * ( (1 << num_layers) - 1 )
