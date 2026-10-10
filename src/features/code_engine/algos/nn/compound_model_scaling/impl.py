from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoCompoundModelScaling:
    """
    ---
    contract:
      algo_id: ALGO-NN-78
      name: NnAlgoCompoundModelScaling
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.efficientnet
        - nn.compound_scaling
        - nn.model_architecture
        - nn.resource_allocation
      inputs:
        type: object
        properties:
          base_depths:
            type: array
            items:
              type: integer
            description: Base number of layer repeats per stage [d_1, ..., d_S].
          base_channels:
            type: array
            items:
              type: integer
            description: Base channel counts per stage [c_1, ..., c_S].
          base_resolution:
            type: integer
            default: 224
            description: Base input image spatial resolution (height/width).
          phi:
            type: number
            default: 1.0
            description: User compound scaling coefficient phi >= 0.0.
          alpha:
            type: number
            default: 1.2
            description: Depth scaling base constant alpha >= 1.0.
          beta:
            type: number
            default: 1.1
            description: Width scaling base constant beta >= 1.0.
          gamma:
            type: number
            default: 1.15
            description: Resolution scaling base constant gamma >= 1.0.
          divisor:
            type: integer
            default: 8
            description: Channel alignment divisor (channels rounded to nearest multiple of divisor).
        required:
          - base_depths
          - base_channels
      outputs:
        type: object
        properties:
          scaled_depths:
            type: array
            items:
              type: integer
            description: Scaled integer layer repeat counts per stage.
          scaled_channels:
            type: array
            items:
              type: integer
            description: Scaled integer channel counts per stage rounded to nearest multiple of divisor.
          scaled_resolution:
            type: integer
            description: Scaled integer input spatial resolution.
          total_flop_ratio:
            type: number
            description: Theoretical computational FLOP scaling ratio relative to base model (~2^phi).
        required:
          - scaled_depths
          - scaled_channels
          - scaled_resolution
          - total_flop_ratio
      parameters: {}
      input_assumptions:
        - base_depths and base_channels must be non-empty 1D integer arrays of matching length S >= 1.
        - phi must be >= 0.0.
        - alpha, beta, gamma must be >= 1.0.
        - divisor must be >= 1.
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
          S: number of network stages
        time_worst: O(S)
        time_typical: O(S)
        space: O(S)
      preconditions:
        - len(base_depths) > 0 and len(base_channels) == len(base_depths)
        - all(d >= 1 for d in base_depths)
        - all(c >= 1 for c in base_channels)
        - phi >= 0.0
        - alpha >= 1.0 and beta >= 1.0 and gamma >= 1.0
        - divisor >= 1
      postconditions:
        - len(output.scaled_depths) == len(base_depths)
        - len(output.scaled_channels) == len(base_channels)
        - output.scaled_resolution >= base_resolution
        - output.total_flop_ratio >= 1.0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-76
        - ALGO-NN-77
      references:
        - tan2019efficientnet
    ---
    """

    @staticmethod
    def _round_channels(ch: float, divisor: int) -> int:
        # Round channel to nearest multiple of divisor, preserving at least 90% of value
        new_ch = max(divisor, int(ch + divisor / 2) // divisor * divisor)
        if new_ch < 0.9 * ch:
            new_ch += divisor
        return int(new_ch)

    @staticmethod
    def scale_architecture(
        base_depths: Sequence[int],
        base_channels: Sequence[int],
        base_resolution: int = 224,
        phi: float = 1.0,
        alpha: float = 1.2,
        beta: float = 1.1,
        gamma: float = 1.15,
        divisor: int = 8,
    ) -> Dict[str, Any]:
        if not base_depths or len(base_channels) != len(base_depths):
            raise ValueError("Precondition failed: base_depths and base_channels must be non-empty matching arrays.")
        if any(d < 1 for d in base_depths) or any(c < 1 for c in base_channels):
            raise ValueError("Precondition failed: depth and channel counts must be >= 1.")
        if phi < 0.0:
            raise ValueError("Precondition failed: phi must be >= 0.0.")
        if alpha < 1.0 or beta < 1.0 or gamma < 1.0:
            raise ValueError("Precondition failed: alpha, beta, gamma must be >= 1.0.")
        if divisor < 1:
            raise ValueError("Precondition failed: divisor must be >= 1.")

        depth_mult = alpha ** phi
        width_mult = beta ** phi
        res_mult = gamma ** phi

        scaled_depths: List[int] = [max(1, int(math.ceil(d * depth_mult))) for d in base_depths]
        scaled_channels: List[int] = [
            NnAlgoCompoundModelScaling._round_channels(c * width_mult, divisor)
            for c in base_channels
        ]
        scaled_res = int(round(base_resolution * res_mult))

        # Flop scaling: Flops ~ depth * width^2 * resolution^2 = alpha^phi * (beta^phi)^2 * (gamma^phi)^2
        flop_ratio = (depth_mult) * (width_mult ** 2) * (res_mult ** 2)

        return {
            "scaled_depths": scaled_depths,
            "scaled_channels": scaled_channels,
            "scaled_resolution": scaled_res,
            "total_flop_ratio": flop_ratio,
        }
