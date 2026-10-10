from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoWsdOneCycleSchedules:
    """
    ---
    contract:
      algo_id: ALGO-NN-45
      name: NnAlgoWsdOneCycleSchedules
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.schedule
        - nn.wsd
        - nn.one_cycle
        - nn.linear_decay
      inputs:
        type: object
        properties:
          current_step:
            type: integer
            description: Current step t >= 0.
          total_steps:
            type: integer
            description: Total steps T >= 1.
          max_lr:
            type: number
            description: Peak learning rate eta_max > 0.
          schedule_type:
            type: string
            enum: [wsd, one_cycle, linear_decay]
            default: wsd
            description: Schedule formulation.
          warmup_pct:
            type: number
            default: 0.1
            description: Fraction of steps for warmup in [0, 1].
          decay_pct:
            type: number
            default: 0.2
            description: Fraction of steps for cooldown/decay in [0, 1] (for WSD).
        required:
          - current_step
          - total_steps
          - max_lr
        additionalProperties: false
      outputs:
        type: object
        properties:
          learning_rate:
            type: number
            description: Computed learning rate eta_t.
          phase:
            type: string
            description: Current schedule phase (warmup, stable, decay).
        required:
          - learning_rate
          - phase
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        current_step: int,
        total_steps: int,
        max_lr: float,
        schedule_type: Literal["wsd", "one_cycle", "linear_decay"] = "wsd",
        warmup_pct: float = 0.1,
        decay_pct: float = 0.2,
    ) -> Dict[str, Any]:
        if current_step < 0 or total_steps < 1 or max_lr <= 0.0:
            raise ValueError("Precondition failed: invalid step or learning rate values.")

        step = min(current_step, total_steps)

        if schedule_type == "wsd":
            w_steps = int(warmup_pct * total_steps)
            d_steps = int(decay_pct * total_steps)
            s_steps = total_steps - w_steps - d_steps

            if step < w_steps:
                lr = max_lr * (float(step) / float(max(1, w_steps)))
                phase = "warmup"
            elif step < (w_steps + s_steps):
                lr = max_lr
                phase = "stable"
            else:
                progress = float(step - w_steps - s_steps) / float(max(1, d_steps))
                lr = max_lr * 0.5 * (1.0 + math.cos(math.pi * min(1.0, progress)))
                phase = "decay"

        elif schedule_type == "linear_decay":
            progress = float(step) / float(total_steps)
            lr = max_lr * (1.0 - progress)
            phase = "decay"

        elif schedule_type == "one_cycle":
            half_steps = total_steps / 2.0
            if step < half_steps:
                progress = float(step) / half_steps
                lr = max_lr * progress
                phase = "warmup"
            else:
                progress = float(step - half_steps) / half_steps
                lr = max_lr * (1.0 - progress)
                phase = "decay"
        else:
            raise ValueError(f"Precondition failed: unknown schedule {schedule_type}")

        return {
            "learning_rate": max(0.0, lr),
            "phase": phase,
        }
