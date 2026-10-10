from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class LayerSpec:
    def __init__(self, name: str, kernel_size: int, stride: int = 1, padding: int = 0, dilation: int = 1):
        if kernel_size < 1:
            raise ValueError("Precondition failed: kernel_size must be >= 1")
        if stride < 1:
            raise ValueError("Precondition failed: stride must be >= 1")
        if padding < 0:
            raise ValueError("Precondition failed: padding must be >= 0")
        if dilation < 1:
            raise ValueError("Precondition failed: dilation must be >= 1")
        self.name = name
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation

    @property
    def effective_kernel_size(self) -> int:
        return self.dilation * (self.kernel_size - 1) + 1


class NnAlgoReceptiveFieldAnalysis:
    """
    ---
    contract:
      algo_id: ALGO-NN-83
      name: NnAlgoReceptiveFieldAnalysis
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.receptive_field
        - nn.spatial_analysis
        - nn.diagnostics
      inputs:
        type: object
        required:
          - layers
        properties:
          layers:
            type: array
            items:
              type: object
            description: Ordered list of layer specifications containing kernel_size, stride, padding, dilation.
      outputs:
        type: object
        required:
          - profile
          - erf_std
        properties:
          profile:
            type: array
            items:
              type: object
            description: Layer-by-layer receptive field metrics including rf_size, cumulative jump, and start coordinate.
          erf_std:
            type: number
            description: Theoretical Gaussian Effective Receptive Field standard deviation sigma.
      parameters: {}
      input_assumptions:
        - layers list contains valid Sequential layer specifications
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact closed-form recurrence"
      uses_model: false
      complexity:
        variables:
          L: number of convolutional layers
        time_worst: O(L)
        time_typical: O(L)
        space: O(L)
      preconditions:
        - len(input.layers) > 0
        - all(layer.kernel_size >= 1 and layer.stride >= 1 for layer in input.layers)
      postconditions:
        - len(output.profile) == len(input.layers) + 1
        - output.erf_std > 0
      certificate: "r_l = r_{l-1} + (k'_l - 1) * j_{l-1} and j_l = j_{l-1} * s_l"
      compatible_adapters:
        - ADAPTER-RECEPTIVE-FIELD
        - ADAPTER-MODEL-PROFILER
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-70
        - ALGO-NN-80
      references:
        - "https://doi.org/10.23915/distill.00021"
        - "https://arxiv.org/abs/1701.04128"
    ---
    """

    @staticmethod
    def compute_rf_profile(layers: List[LayerSpec]) -> Dict[str, Any]:
        if not layers or len(layers) == 0:
            raise ValueError("Precondition failed: len(input.layers) > 0")

        r = 1.0
        j = 1.0
        start = 0.5

        history = [{
            "layer": "input",
            "rf_size": r,
            "jump": j,
            "start": start,
        }]

        var_sum = 0.0
        for layer in layers:
            k_eff = float(layer.effective_kernel_size)
            s = float(layer.stride)
            p = float(layer.padding)

            r_next = r + (k_eff - 1.0) * j
            start_next = start + ((k_eff - 1.0) / 2.0 - p) * j

            k = float(layer.kernel_size)
            k_var = (k * k - 1.0) / 12.0
            var_sum += k_var * (j * j)

            j_next = j * s

            r = r_next
            start = start_next
            j = j_next

            history.append({
                "layer": layer.name,
                "rf_size": r,
                "jump": j,
                "start": start,
                "kernel_size": layer.kernel_size,
                "effective_kernel_size": layer.effective_kernel_size,
                "stride": layer.stride,
                "padding": layer.padding,
                "dilation": layer.dilation,
            })

        erf_std = math.sqrt(max(1e-9, var_sum))
        return {
            "profile": history,
            "erf_std": erf_std,
        }

    @staticmethod
    def output_to_input_span(
        out_idx: int,
        rf_size: float,
        jump: float,
        start: float,
    ) -> Tuple[float, float, float]:
        center = start + float(out_idx) * jump
        half_rf = (rf_size - 1.0) / 2.0
        min_coord = center - half_rf
        max_coord = center + half_rf
        return center, min_coord, max_coord
