from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoDropoutInverted:
    """
    ---
    contract:
      algo_id: ALGO-NN-58
      name: NnAlgoDropoutInverted
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.dropout
        - nn.inverted_dropout
        - nn.stochastic
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D activation matrix X of shape (B, D).
          dropout_prob:
            type: number
            default: 0.1
            description: Probability p of zeroing an activation element, with 0.0 <= p < 1.0.
          training:
            type: boolean
            default: true
            description: Mode flag (true for stochastic zeroing and scaling, false for identity passthrough).
          mask:
            type: array
            items:
              type: array
              items:
                type: number
            description: Optional pre-generated binary mask of shape (B, D) with elements in {0, 1}.
          seed:
            type: integer
            default: 42
            description: Deterministic pseudorandom seed if mask is not explicitly provided.
        required:
          - input_tensor
      outputs:
        type: object
        properties:
          output_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output tensor Y of shape (B, D).
          mask:
            type: array
            items:
              type: array
              items:
                type: number
            description: Binary mask M applied during the forward pass of shape (B, D).
          scale_factor:
            type: number
            description: Inverted scaling factor 1 / (1 - p) during training, or 1.0 during inference.
        required:
          - output_tensor
          - mask
          - scale_factor
      parameters: {}
      input_assumptions:
        - input_tensor must be a non-empty 2D array of shape (B, D) with B >= 1 and D >= 1.
        - dropout_prob p must satisfy 0.0 <= p < 1.0.
        - If mask is provided, it must match the shape of input_tensor with values in {0, 1}.
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
          B: batch size
          D: hidden dimension
        time_worst: O(B * D)
        time_typical: O(B * D)
        space: O(B * D)
      preconditions:
        - len(input_tensor) > 0 and len(input_tensor[0]) > 0
        - all(len(row) == len(input_tensor[0]) for row in input_tensor)
        - 0.0 <= dropout_prob < 1.0
      postconditions:
        - len(output.output_tensor) == len(input_tensor)
        - len(output.output_tensor[0]) == len(input_tensor[0])
        - len(output.mask) == len(input_tensor)
        - len(output.mask[0]) == len(input_tensor[0])
        - output.scale_factor > 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-59
        - ALGO-NN-60
      references:
        - "https://jmlr.org/papers/v15/srivastava14a.html"
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[float]],
        dropout_prob: float = 0.1,
        training: bool = True,
        mask: Optional[Sequence[Sequence[float]]] = None,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not input_tensor or not input_tensor[0]:
            raise ValueError("Precondition failed: input_tensor must be non-empty 2D array.")
        B = len(input_tensor)
        D = len(input_tensor[0])

        for row in input_tensor:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in input_tensor.")

        if not (0.0 <= dropout_prob < 1.0):
            raise ValueError("Precondition failed: dropout_prob must satisfy 0.0 <= p < 1.0.")

        out_tensor: List[List[float]] = [[0.0] * D for _ in range(B)]
        applied_mask: List[List[float]] = [[1.0] * D for _ in range(B)]

        if not training or dropout_prob == 0.0:
            for i in range(B):
                for j in range(D):
                    out_tensor[i][j] = float(input_tensor[i][j])
            return {
                "output_tensor": out_tensor,
                "mask": applied_mask,
                "scale_factor": 1.0,
            }

        keep_prob = 1.0 - dropout_prob
        scale = 1.0 / keep_prob

        if mask is not None:
            if len(mask) != B or any(len(r) != D for r in mask):
                raise ValueError("Precondition failed: provided mask dimensions do not match input_tensor.")
            applied_mask = [[float(mask[i][j]) for j in range(D)] for i in range(B)]
        else:
            rng = random.Random(seed)
            for i in range(B):
                for j in range(D):
                    applied_mask[i][j] = 1.0 if rng.random() < keep_prob else 0.0

        for i in range(B):
            for j in range(D):
                out_tensor[i][j] = input_tensor[i][j] * applied_mask[i][j] * scale

        return {
            "output_tensor": out_tensor,
            "mask": applied_mask,
            "scale_factor": scale,
        }
