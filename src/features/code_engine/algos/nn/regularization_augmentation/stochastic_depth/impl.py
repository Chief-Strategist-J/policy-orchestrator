from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoStochasticDepth:
    """
    ---
    contract:
      algo_id: ALGO-NN-59
      name: NnAlgoStochasticDepth
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.stochastic_depth
        - nn.droppath
        - nn.vit
        - nn.resnet
      inputs:
        type: object
        properties:
          x_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D shortcut residual tensor X of shape (B, D).
          f_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D sublayer branch tensor F(X) of shape (B, D).
          drop_prob:
            type: number
            default: 0.1
            description: Probability p of dropping the residual branch, with 0.0 <= p < 1.0.
          training:
            type: boolean
            default: true
            description: Mode flag (true for stochastic branch dropping, false for deterministic addition).
          binary_gates:
            type: array
            items:
              type: number
            description: Optional pre-generated per-sample binary survival gates of length B with elements in {0, 1}.
          seed:
            type: integer
            default: 42
            description: Deterministic pseudorandom seed if binary_gates are not explicitly provided.
        required:
          - x_tensor
          - f_tensor
      outputs:
        type: object
        properties:
          output_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output combined tensor Y = X + (gate / (1-p)) * F(X) of shape (B, D).
          gates:
            type: array
            items:
              type: number
            description: Per-sample survival gates vector of length B (elements in {0.0, 1.0}).
          scale_factor:
            type: number
            description: Inverted survival scale factor 1 / (1 - p) during training, or 1.0 during inference.
        required:
          - output_tensor
          - gates
          - scale_factor
      parameters: {}
      input_assumptions:
        - x_tensor and f_tensor must be non-empty 2D arrays of identical shape (B, D) with B >= 1 and D >= 1.
        - drop_prob p must satisfy 0.0 <= p < 1.0.
        - If binary_gates is provided, its length must equal B and entries must be in {0, 1}.
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
        - len(x_tensor) > 0 and len(x_tensor[0]) > 0
        - len(f_tensor) == len(x_tensor) and len(f_tensor[0]) == len(x_tensor[0])
        - all(len(row) == len(x_tensor[0]) for row in x_tensor)
        - all(len(row) == len(x_tensor[0]) for row in f_tensor)
        - 0.0 <= drop_prob < 1.0
      postconditions:
        - len(output.output_tensor) == len(x_tensor)
        - len(output.output_tensor[0]) == len(x_tensor[0])
        - len(output.gates) == len(x_tensor)
        - output.scale_factor > 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-58
        - ALGO-NN-74
        - ALGO-NN-81
      references:
        - "https://doi.org/10.1007/978-3-319-46493-0_39"
        - "https://doi.org/search?q=touvron2021training"
    ---
    """

    @staticmethod
    def forward(
        x_tensor: Sequence[Sequence[float]],
        f_tensor: Sequence[Sequence[float]],
        drop_prob: float = 0.1,
        training: bool = True,
        binary_gates: Optional[Sequence[float]] = None,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not x_tensor or not x_tensor[0]:
            raise ValueError("Precondition failed: x_tensor must be non-empty 2D array.")
        if not f_tensor or not f_tensor[0]:
            raise ValueError("Precondition failed: f_tensor must be non-empty 2D array.")

        B = len(x_tensor)
        D = len(x_tensor[0])

        if len(f_tensor) != B or len(f_tensor[0]) != D:
            raise ValueError("Precondition failed: f_tensor shape must match x_tensor shape exactly.")

        for row in x_tensor:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in x_tensor.")
        for row in f_tensor:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in f_tensor.")

        if not (0.0 <= drop_prob < 1.0):
            raise ValueError("Precondition failed: drop_prob must satisfy 0.0 <= p < 1.0.")

        out_tensor: List[List[float]] = [[0.0] * D for _ in range(B)]
        gates_list: List[float] = [1.0] * B

        if not training or drop_prob == 0.0:
            for i in range(B):
                for j in range(D):
                    out_tensor[i][j] = float(x_tensor[i][j] + f_tensor[i][j])
            return {
                "output_tensor": out_tensor,
                "gates": gates_list,
                "scale_factor": 1.0,
            }

        keep_prob = 1.0 - drop_prob
        scale = 1.0 / keep_prob

        if binary_gates is not None:
            if len(binary_gates) != B:
                raise ValueError("Precondition failed: binary_gates length must equal batch size B.")
            gates_list = [float(g) for g in binary_gates]
        else:
            rng = random.Random(seed)
            gates_list = [1.0 if rng.random() < keep_prob else 0.0 for _ in range(B)]

        for i in range(B):
            gate = gates_list[i]
            effective_scale = gate * scale
            for j in range(D):
                out_tensor[i][j] = x_tensor[i][j] + effective_scale * f_tensor[i][j]

        return {
            "output_tensor": out_tensor,
            "gates": gates_list,
            "scale_factor": scale,
        }
