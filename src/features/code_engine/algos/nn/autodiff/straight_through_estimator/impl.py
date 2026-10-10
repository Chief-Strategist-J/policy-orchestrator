from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoStraightThroughEstimator:
    """
    ---
    contract:
      algo_id: ALGO-NN-29
      name: NnAlgoStraightThroughEstimator
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.quantization
      - nn.ste
      - nn.discrete_optimization
      - nn.binarization
      inputs:
        type: object
        properties:
          inputs:
            type: array
            items:
              type: number
            description: Continuous latent tensor x of length N.
          upstream_gradients:
            type: array
            items:
              type: number
            description: Upstream adjoints dL/dq of length N.
          mode:
            type: string
            enum:
            - sign
            - round
            - clamp_ste
            default: sign
            description: Discrete forward quantization operator.
          clip_threshold:
            type: number
            default: 1.0
            description: Gradient clipping range [-threshold, threshold] for HardTanh/STE
              backward pass.
        required:
        - inputs
        - upstream_gradients
        additionalProperties: false
      outputs:
        type: object
        properties:
          quantized_outputs:
            type: array
            items:
              type: number
            description: Discrete forward outputs q = Q(x) of length N.
          surrogate_gradients:
            type: array
            items:
              type: number
            description: Straight-through surrogate gradients dL/dx of length N.
        required:
        - quantized_outputs
        - surrogate_gradients
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
        inputs: Sequence[float],
        upstream_gradients: Sequence[float],
        mode: Literal["sign", "round", "clamp_ste"] = "sign",
        clip_threshold: float = 1.0,
    ) -> Dict[str, Any]:
        n = len(inputs)
        if n == 0:
            raise ValueError("Precondition failed: inputs list cannot be empty.")
        if len(upstream_gradients) != n:
            raise ValueError(f"Precondition failed: upstream gradients length must match inputs ({n}).")

        q_out: List[float] = []
        g_out: List[float] = []

        for x, dy in zip(inputs, upstream_gradients):
            if mode == "sign":
                q = 1.0 if x >= 0.0 else -1.0
            elif mode == "round":
                q = float(round(x))
            elif mode == "clamp_ste":
                q = max(-clip_threshold, min(clip_threshold, x))
            else:
                raise ValueError(f"Precondition failed: unknown mode {mode}")

            if abs(x) <= clip_threshold:
                dx = dy
            else:
                dx = 0.0

            q_out.append(q)
            g_out.append(dx)

        return {
            "quantized_outputs": q_out,
            "surrogate_gradients": g_out,
        }
