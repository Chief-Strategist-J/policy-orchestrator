from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLearningRateWarmup:
    """
    ---
    contract:
      algo_id: ALGO-NN-43
      name: NnAlgoLearningRateWarmup
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.schedule
        - nn.warmup
        - nn.learning_rate
        - nn.early_training_stability
      inputs:
        type: object
        properties:
          current_step:
            type: integer
            description: Current training step t >= 0.
          warmup_steps:
            type: integer
            description: Total warmup duration W >= 1.
          base_lr:
            type: number
            description: Peak target learning rate eta_max > 0.
          warmup_init_lr:
            type: number
            default: 0.0
            description: Starting learning rate at step 0 eta_min >= 0.
          strategy:
            type: string
            enum: [linear, cosine, quadratic]
            default: linear
            description: Mathematical warmup ramp curve.
        required:
          - current_step
          - warmup_steps
          - base_lr
        additionalProperties: false
      outputs:
        type: object
        properties:
          learning_rate:
            type: number
            description: Computed learning rate eta_t for the current step.
          progress_fraction:
            type: number
            description: Normalized progress ratio in [0, 1].
          is_warmup:
            type: boolean
            description: Whether the current step is within the warmup phase.
        required:
          - learning_rate
          - progress_fraction
          - is_warmup
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        current_step: int,
        warmup_steps: int,
        base_lr: float,
        warmup_init_lr: float = 0.0,
        strategy: Literal["linear", "cosine", "quadratic"] = "linear",
    ) -> Dict[str, Any]:
        if current_step < 0:
            raise ValueError(f"Precondition failed: current_step must be >= 0, got {current_step}.")
        if warmup_steps < 1:
            raise ValueError(f"Precondition failed: warmup_steps must be >= 1, got {warmup_steps}.")
        if base_lr <= 0.0:
            raise ValueError(f"Precondition failed: base_lr must be > 0, got {base_lr}.")
        if warmup_init_lr < 0.0:
            raise ValueError(f"Precondition failed: warmup_init_lr must be >= 0, got {warmup_init_lr}.")

        if current_step >= warmup_steps:
            return {
                "learning_rate": base_lr,
                "progress_fraction": 1.0,
                "is_warmup": False,
            }

        progress = float(current_step) / float(warmup_steps)

        if strategy == "linear":
            lr = warmup_init_lr + (base_lr - warmup_init_lr) * progress
        elif strategy == "cosine":
            factor = 0.5 * (1.0 - math.cos(math.pi * progress))
            lr = warmup_init_lr + (base_lr - warmup_init_lr) * factor
        elif strategy == "quadratic":
            lr = warmup_init_lr + (base_lr - warmup_init_lr) * (progress ** 2)
        else:
            raise ValueError(f"Precondition failed: unrecognized strategy {strategy}")

        return {
            "learning_rate": lr,
            "progress_fraction": progress,
            "is_warmup": True,
        }
