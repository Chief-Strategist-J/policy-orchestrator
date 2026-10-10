from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoSqueezeExcitationCbam:
    """
    ---
    contract:
      algo_id: ALGO-NN-77
      name: NnAlgoSqueezeExcitationCbam
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.attention
        - nn.squeeze_excitation
        - nn.cbam
        - nn.channel_attention
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
            description: 3D input activation tensor X of shape (C, H, W).
          mode:
            type: string
            enum:
              - se
              - cbam
            default: se
            description: Attention module type ('se' for Squeeze-and-Excitation, 'cbam' for Channel + Spatial CBAM).
          w1_reduce:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D MLP weight matrix of shape (C_mid, C) for channel reduction (C_mid = C / r).
          w2_expand:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D MLP weight matrix of shape (C, C_mid) for channel excitation expansion.
          spatial_conv_weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 3D weight kernel of shape (2, K_s, K_s) used in CBAM spatial attention (e.g. 7x7 or 3x3).
        required:
          - input_tensor
          - w1_reduce
          - w2_expand
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
            description: Recalibrated 3D feature tensor Y of shape (C, H, W).
          channel_weights:
            type: array
            items:
              type: number
            description: 1D channel attention scaling vector s of length C.
          spatial_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D spatial attention weight map M_s of shape (H, W) if in CBAM mode.
        required:
          - output_tensor
          - channel_weights
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 3D array of shape (C, H, W).
        - w1_reduce must have shape (C_mid, C); w2_expand must have shape (C, C_mid).
        - In cbam mode, spatial_conv_weights must be non-empty with 2 input channels.
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
          C: channel count
          C_mid: bottleneck channels
          H: height
          W: width
        time_worst: O(C * H * W + C * C_mid)
        time_typical: O(C * H * W + C * C_mid)
        space: O(C * H * W)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0 and len(input_tensor[0][0]) > 0
        - len(w1_reduce) > 0 and len(w1_reduce[0]) == len(input_tensor)
        - len(w2_expand) == len(input_tensor) and len(w2_expand[0]) == len(w1_reduce)
        - mode in ["se", "cbam"]
      postconditions:
        - len(output.output_tensor) == len(input_tensor)
        - len(output.channel_weights) == len(input_tensor)
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-69
        - ALGO-NN-73
        - ALGO-NN-74
      references:
        - "https://doi.org/10.1109/CVPR.2018.00745"
        - "https://doi.org/search?q=woo2018cbam"
    ---
    """

    @staticmethod
    def _sigmoid(z: float) -> float:
        if z < -60.0:
            return 0.0
        if z > 60.0:
            return 1.0
        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def _mlp_forward(
        vec: Sequence[float],
        w1: Sequence[Sequence[float]],
        w2: Sequence[Sequence[float]],
    ) -> List[float]:
        C = len(vec)
        C_mid = len(w1)
        h1 = [0.0] * C_mid
        for cm in range(C_mid):
            acc = sum(w1[cm][c] * vec[c] for c in range(C))
            h1[cm] = max(0.0, acc)
        h2 = [0.0] * C
        for c in range(C):
            h2[c] = sum(w2[c][cm] * h1[cm] for cm in range(C_mid))
        return h2

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[Sequence[float]]],
        w1_reduce: Sequence[Sequence[float]],
        w2_expand: Sequence[Sequence[float]],
        mode: Literal["se", "cbam"] = "se",
        spatial_conv_weights: Optional[Sequence[Sequence[Sequence[float]]]]] = None,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0] or not input_tensor[0][0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 3D array.")

        C = len(input_tensor)
        H = len(input_tensor[0])
        W = len(input_tensor[0][0])
        total_pixels = float(H * W)

        if not w1_reduce or len(w1_reduce[0]) != C:
            raise ValueError("Precondition failed: w1_reduce shape must match (C_mid, C).")
        C_mid = len(w1_reduce)

        if len(w2_expand) != C or len(w2_expand[0]) != C_mid:
            raise ValueError("Precondition failed: w2_expand shape must match (C, C_mid).")

        if mode == "se":
            z_gap = [0.0] * C
            for c in range(C):
                z_gap[c] = sum(sum(input_tensor[c][h][w] for w in range(W)) for h in range(H)) / total_pixels

            logits = NnAlgoSqueezeExcitationCbam._mlp_forward(z_gap, w1_reduce, w2_expand)
            channel_weights = [NnAlgoSqueezeExcitationCbam._sigmoid(val) for val in logits]

            out_tensor: List[List[List[float]]] = [
                [[channel_weights[c] * input_tensor[c][h][w] for w in range(W)] for h in range(H)]
                for c in range(C)
            ]

            return {
                "output_tensor": out_tensor,
                "channel_weights": channel_weights,
            }

        else:
            z_avg = [0.0] * C
            z_max = [-float("inf")] * C
            for c in range(C):
                total_sum = 0.0
                max_v = -float("inf")
                for h in range(H):
                    for w in range(W):
                        val = input_tensor[c][h][w]
                        total_sum += val
                        if val > max_v:
                            max_v = val
                z_avg[c] = total_sum / total_pixels
                z_max[c] = max_v

            mlp_avg = NnAlgoSqueezeExcitationCbam._mlp_forward(z_avg, w1_reduce, w2_expand)
            mlp_max = NnAlgoSqueezeExcitationCbam._mlp_forward(z_max, w1_reduce, w2_expand)

            channel_weights = [
                NnAlgoSqueezeExcitationCbam._sigmoid(mlp_avg[c] + mlp_max[c])
                for c in range(C)
            ]

            scaled_channels: List[List[List[float]]] = [
                [[channel_weights[c] * input_tensor[c][h][w] for w in range(W)] for h in range(H)]
                for c in range(C)
            ]

            spatial_weights: List[List[float]] = [[1.0] * W for _ in range(H)]
            if spatial_conv_weights is not None and len(spatial_conv_weights) == 2:
                K_s = len(spatial_conv_weights[0])
                pad_s = K_s // 2

                avg_map = [[0.0] * W for _ in range(H)]
                max_map = [[0.0] * W for _ in range(H)]
                for h in range(H):
                    for w in range(W):
                        pix_sum = sum(scaled_channels[c][h][w] for c in range(C))
                        pix_max = max(scaled_channels[c][h][w] for c in range(C))
                        avg_map[h][w] = pix_sum / float(C)
                        max_map[h][w] = pix_max

                padded_avg = [[0.0] * (W + 2 * pad_s) for _ in range(H + 2 * pad_s)]
                padded_max = [[0.0] * (W + 2 * pad_s) for _ in range(H + 2 * pad_s)]
                for h in range(H):
                    for w in range(W):
                        padded_avg[h + pad_s][w + pad_s] = avg_map[h][w]
                        padded_max[h + pad_s][w + pad_s] = max_map[h][w]

                w_avg_k = spatial_conv_weights[0]
                w_max_k = spatial_conv_weights[1]

                for h in range(H):
                    for w in range(W):
                        acc = 0.0
                        for kh in range(K_s):
                            for kw in range(K_s):
                                acc += w_avg_k[kh][kw] * padded_avg[h + kh][w + kw]
                                acc += w_max_k[kh][kw] * padded_max[h + kh][w + kw]
                        spatial_weights[h][w] = NnAlgoSqueezeExcitationCbam._sigmoid(acc)

            out_tensor = [
                [[scaled_channels[c][h][w] * spatial_weights[h][w] for w in range(W)] for h in range(H)]
                for c in range(C)
            ]

            return {
                "output_tensor": out_tensor,
                "channel_weights": channel_weights,
                "spatial_weights": spatial_weights,
            }
