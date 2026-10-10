from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoDeepResidualInit:
    """
    ---
    contract:
      algo_id: ALGO-NN-49
      name: NnAlgoDeepResidualInit
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.initialization
      - nn.residual
      - nn.fixup
      - nn.zero_init
      - nn.gpt2_scaling
      inputs:
        type: object
        properties:
          num_layers:
            type: integer
            description: Total number of residual blocks/layers L >= 1.
          base_std:
            type: number
            default: 0.02
            description: Standard baseline standard deviation sigma_0 > 0.
          strategy:
            type: string
            enum:
            - scaled_residual
            - zero_init
            - fixup
            default: scaled_residual
            description: Deep residual initialization scheme.
        required:
        - num_layers
        additionalProperties: false
      outputs:
        type: object
        properties:
          scaled_std:
            type: number
            description: Scaled standard deviation sigma for residual projection weights.
          scale_factor:
            type: number
            description: Multiplicative attenuation coefficient (e.g., 1 / sqrt(2L)).
        required:
        - scaled_std
        - scale_factor
        additionalProperties: false
      parameters: {}
      input_assumptions:
      - Input tensors and parameters satisfy dimensionality and finite numerical bounds.
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: Standard IEEE-754 floating point precision
      uses_model: false
      complexity:
        variables:
          N: tensor/parameter dimension
        time_worst: O(N)
        time_typical: O(N)
        space: O(N)
      preconditions:
      - Input tensors are non-empty and conform to defined mathematical shapes.
      postconditions:
      - Output values and arrays are populated without NaN or infinite values.
      certificate: Exact implementation matching analytical mathematical derivation.
      compatible_adapters: []
      related_algos: []
      references:
      - https://arxiv.org/
    ---
    """

    @staticmethod
    def forward(
        num_layers: int,
        base_std: float = 0.02,
        strategy: Literal["scaled_residual", "zero_init", "fixup"] = "scaled_residual",
    ) -> Dict[str, Any]:
        if num_layers < 1:
            raise ValueError(f"Precondition failed: num_layers must be >= 1, got {num_layers}.")
        if base_std <= 0.0:
            raise ValueError(f"Precondition failed: base_std must be > 0, got {base_std}.")

        if strategy == "scaled_residual":
            scale = 1.0 / math.sqrt(2.0 * num_layers)
            scaled_std = base_std * scale
        elif strategy == "zero_init":
            scale = 0.0
            scaled_std = 0.0
        elif strategy == "fixup":
            scale = num_layers ** (-0.25)
            scaled_std = base_std * scale
        else:
            raise ValueError(f"Precondition failed: unknown strategy {strategy}")

        return {
            "scaled_std": scaled_std,
            "scale_factor": scale,
        }
