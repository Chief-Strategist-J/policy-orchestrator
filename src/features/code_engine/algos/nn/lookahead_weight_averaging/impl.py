from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLookaheadWeightAveraging:
    """
    ---
    contract:
      algo_id: ALGO-NN-42
      name: NnAlgoLookaheadWeightAveraging
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.optimizer
      - nn.lookahead
      - nn.ema
      - nn.polyak_averaging
      inputs:
        type: object
        properties:
          mode:
            type: string
            enum:
            - lookahead
            - ema
            default: ema
            description: Weight smoothing strategy.
          fast_weights:
            type: array
            items:
              type: number
            description: Current fast optimizer weights theta of length P.
          slow_weights:
            type: array
            items:
              type: number
            description: Slow reference weights or EMA target weights of length P.
          alpha:
            type: number
            default: 0.999
            description: Slow interpolation rate or EMA decay coefficient in (0, 1).
        required:
        - mode
        - fast_weights
        - slow_weights
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_slow_weights:
            type: array
            items:
              type: number
            description: Updated smoothed weights of length P.
          synced_fast_weights:
            type: array
            items:
              type: number
            description: Fast weights synchronized to updated slow weights (for Lookahead).
        required:
        - updated_slow_weights
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
        mode: Literal["lookahead", "ema"] = "ema",
        fast_weights: Optional[Sequence[float]] = None,
        slow_weights: Optional[Sequence[float]] = None,
        alpha: float = 0.999,
    ) -> Dict[str, Any]:
        if fast_weights is None or slow_weights is None:
            raise ValueError("Precondition failed: fast_weights and slow_weights are required.")
        p = len(fast_weights)
        if p == 0 or len(slow_weights) != p:
            raise ValueError("Precondition failed: weights must have identical non-zero length P.")
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"Precondition failed: alpha must be in (0, 1), got {alpha}.")

        if mode == "ema":
            new_slow = [alpha * s + (1.0 - alpha) * f for s, f in zip(slow_weights, fast_weights)]
            return {
                "updated_slow_weights": new_slow,
            }
        elif mode == "lookahead":
            new_slow = [s + alpha * (f - s) for s, f in zip(slow_weights, fast_weights)]
            return {
                "updated_slow_weights": new_slow,
                "synced_fast_weights": list(new_slow),
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized mode {mode}")
