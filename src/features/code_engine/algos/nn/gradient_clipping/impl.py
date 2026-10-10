from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoGradientClipping:
    """
    ---
    contract:
      algo_id: ALGO-NN-28
      name: NnAlgoGradientClipping
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.optimization
        - nn.gradient_clipping
        - nn.l2_norm
        - nn.stability
      inputs:
        type: object
        properties:
          gradients:
            type: array
            items:
              type: number
            description: Flattened parameter gradient vector g of length P.
          max_norm:
            type: number
            default: 1.0
            description: Maximum allowed L2 gradient norm threshold (must be > 0).
          clip_value:
            type: number
            description: Optional elementwise absolute coordinate clip threshold.
          mode:
            type: string
            enum: [norm, value]
            default: norm
            description: Clipping algorithm (global L2 norm vs elementwise value).
        required:
          - gradients
        additionalProperties: false
      outputs:
        type: object
        properties:
          clipped_gradients:
            type: array
            items:
              type: number
            description: Rescaled or clamped gradient vector of length P.
          total_norm:
            type: number
            description: Original global L2 norm of the gradient vector before clipping.
          was_clipped:
            type: boolean
            description: Whether the gradient magnitude exceeded max_norm or clip_value.
        required:
          - clipped_gradients
          - total_norm
          - was_clipped
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        gradients: Sequence[float],
        max_norm: float = 1.0,
        clip_value: Optional[float] = None,
        mode: Literal["norm", "value"] = "norm",
    ) -> Dict[str, Any]:
        p = len(gradients)
        if p == 0:
            raise ValueError("Precondition failed: gradients list cannot be empty.")
        if max_norm <= 0.0:
            raise ValueError(f"Precondition failed: max_norm must be > 0, got {max_norm}.")

        total_norm = math.sqrt(sum(g ** 2 for g in gradients))

        if mode == "norm":
            if total_norm > max_norm:
                scale = max_norm / (total_norm + 1e-12)
                clipped = [g * scale for g in gradients]
                was_clipped = True
            else:
                clipped = list(gradients)
                was_clipped = False
            return {
                "clipped_gradients": clipped,
                "total_norm": total_norm,
                "was_clipped": was_clipped,
            }

        elif mode == "value":
            c_val = clip_value if clip_value is not None else max_norm
            clipped = [max(-c_val, min(c_val, g)) for g in gradients]
            was_clipped = any(abs(g) > c_val for g in gradients)
            return {
                "clipped_gradients": clipped,
                "total_norm": total_norm,
                "was_clipped": was_clipped,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized mode {mode}")
