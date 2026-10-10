from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoBatchSizeLrScaling:
    """
    ---
    contract:
      algo_id: ALGO-NN-46
      name: NnAlgoBatchSizeLrScaling
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.scaling
      - nn.batch_size
      - nn.learning_rate_scaling
      - nn.distributed_training
      inputs:
        type: object
        properties:
          base_batch_size:
            type: integer
            description: Reference baseline batch size B_0 >= 1.
          base_lr:
            type: number
            description: Reference baseline learning rate eta_0 > 0.
          target_batch_size:
            type: integer
            description: Scaled target batch size B >= 1.
          scaling_rule:
            type: string
            enum:
            - linear
            - square_root
            default: linear
            description: Scaling rule (linear for SGD, square_root for Adam).
        required:
        - base_batch_size
        - base_lr
        - target_batch_size
        additionalProperties: false
      outputs:
        type: object
        properties:
          scaled_lr:
            type: number
            description: Scaled target learning rate eta.
          scale_factor:
            type: number
            description: Batch ratio k = B / B_0.
        required:
        - scaled_lr
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
        base_batch_size: int,
        base_lr: float,
        target_batch_size: int,
        scaling_rule: Literal["linear", "square_root"] = "linear",
    ) -> Dict[str, Any]:
        if base_batch_size < 1 or target_batch_size < 1:
            raise ValueError("Precondition failed: batch sizes must be >= 1.")
        if base_lr <= 0.0:
            raise ValueError(f"Precondition failed: base_lr must be > 0, got {base_lr}.")

        k = float(target_batch_size) / float(base_batch_size)

        if scaling_rule == "linear":
            scaled_lr = base_lr * k
        elif scaling_rule == "square_root":
            scaled_lr = base_lr * math.sqrt(k)
        else:
            raise ValueError(f"Precondition failed: unknown scaling rule {scaling_rule}")

        return {
            "scaled_lr": scaled_lr,
            "scale_factor": k,
        }
