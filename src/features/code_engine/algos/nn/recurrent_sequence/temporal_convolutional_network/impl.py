from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoTemporalConvolutionalNetwork:
    """
    ---
    contract:
      algo_id: ALGO-NN-100
      name: NnAlgoTemporalConvolutionalNetwork
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.tcn
        - nn.temporal_conv
        - nn.causal_dilated
        - nn.sequence
      inputs:
        type: object
        required:
          - x_seq
          - weight
        properties:
          x_seq:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input temporal sequence of shape (T, C_in).
          weight:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 1D convolution kernel tensor of shape (C_out, C_in, K).
          bias:
            type: array
            items:
              type: number
            description: Optional bias vector of length C_out.
          dilation:
            type: integer
            description: Dilation factor d >= 1.
      outputs:
        type: object
        required:
          - out_seq
        properties:
          out_seq:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output temporal sequence of shape (T, C_out).
      parameters:
        dilation: 1
      input_assumptions:
        - len(x_seq) >= 1
        - dilation >= 1
        - kernel dimensions match (C_out, C_in, K) with C_in == len(x_seq[0])
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Standard IEEE-754 floating point precision"
      uses_model: false
      complexity:
        variables:
          T: sequence length
          C_in: input channels
          C_out: output channels
          K: kernel size
        time_worst: "O(T * C_out * C_in * K)"
        time_typical: "O(T * C_out * C_in * K)"
        space: "O(T * C_out)"
      preconditions:
        - len(input.x_seq) > 0
        - input.dilation >= 1
        - len(input.weight[0]) == len(input.x_seq[0])
      postconditions:
        - len(output.out_seq) == len(input.x_seq)
        - len(output.out_seq[0]) == len(input.weight)
      certificate: "y_t = \\sum_{k=0}^{K-1} W[k] \\cdot x_{t - d \\cdot k}"
      compatible_adapters:
        - ADAPTER-TCN-BLOCK
        - ADAPTER-CAUSAL-CONV
      related_algos:
        - ALGO-NN-90
        - ALGO-NN-92
        - ALGO-NN-93
      references:
        - "https://arxiv.org/abs/1803.01271"
        - "https://arxiv.org/abs/1609.03499"
    ---
    """

    @staticmethod
    def sigmoid(x: float) -> float:
        if x >= 0.0:
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
        dilation: int = 1,
    ) -> List[List[float]]:
        if not x_seq or len(x_seq) == 0:
            raise ValueError("Precondition failed: x_seq must be non-empty")
        if dilation < 1:
            raise ValueError(f"Precondition failed: dilation {dilation} must be >= 1")

        t_steps = len(x_seq)
        c_in = len(x_seq[0])
        c_out = len(weight)
        k_size = len(weight[0][0])

        if len(weight[0]) != c_in:
            raise ValueError(f"Precondition failed: kernel C_in {len(weight[0])} != input C_in {c_in}")
        if bias is not None and len(bias) != c_out:
            raise ValueError(f"Precondition failed: bias length {len(bias)} != C_out {c_out}")

        out_seq = [[0.0 for _ in range(c_out)] for _ in range(t_steps)]

        for t in range(t_steps):
            for co in range(c_out):
                val = bias[co] if bias is not None else 0.0
                for k in range(k_size):
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
        b_res: Optional[List[float]] = None,
    ) -> List[List[float]]:
        if not x_seq or len(x_seq) == 0:
            raise ValueError("Precondition failed: x_seq must be non-empty")

        t_steps = len(x_seq)
        c = len(x_seq[0])

        conv_f = NnAlgoTemporalConvolutionalNetwork.causal_dilated_conv1d(x_seq, w_filter, b_filter, dilation)
        conv_g = NnAlgoTemporalConvolutionalNetwork.causal_dilated_conv1d(x_seq, w_gate, b_gate, dilation)

        z_seq = [[0.0 for _ in range(c)] for _ in range(t_steps)]
        for t in range(t_steps):
            for ch in range(c):
                f_val = math.tanh(conv_f[t][ch])
                g_val = NnAlgoTemporalConvolutionalNetwork.sigmoid(conv_g[t][ch])
                z_seq[t][ch] = f_val * g_val

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
        if num_layers < 1:
            raise ValueError(f"Precondition failed: num_layers {num_layers} must be >= 1")
        if kernel_size < 2:
            raise ValueError(f"Precondition failed: kernel_size {kernel_size} must be >= 2")
        return 1 + (kernel_size - 1) * ((1 << num_layers) - 1)
