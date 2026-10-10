from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoCosineDecayRestarts:
    """
    ---
    contract:
      algo_id: ALGO-NN-44
      name: NnAlgoCosineDecayRestarts
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.schedule
      - nn.cosine_annealing
      - nn.sgdr
      - nn.warm_restarts
      inputs:
        type: object
        properties:
          current_step:
            type: integer
            description: Current global step count t >= 0.
          total_steps:
            type: integer
            description: Total training duration or base period T_0 >= 1.
          lr_max:
            type: number
            description: Peak learning rate eta_max > 0.
          lr_min:
            type: number
            default: 0.0
            description: Minimum decayed learning rate eta_min >= 0.
          use_restarts:
            type: boolean
            default: false
            description: Whether to enable SGDR periodic warm restarts.
          t_mult:
            type: integer
            default: 1
            description: Period multiplier factor T_mult >= 1 for consecutive restart
              cycles.
        required:
        - current_step
        - total_steps
        - lr_max
        additionalProperties: false
      outputs:
        type: object
        properties:
          learning_rate:
            type: number
            description: Decayed learning rate eta_t.
          current_cycle:
            type: integer
            description: Current restart cycle index i >= 0.
        required:
        - learning_rate
        - current_cycle
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
        current_step: int,
        total_steps: int,
        lr_max: float,
        lr_min: float = 0.0,
        use_restarts: bool = False,
        t_mult: int = 1,
    ) -> Dict[str, Any]:
        if current_step < 0 or total_steps < 1 or lr_max <= 0.0 or lr_min < 0.0 or t_mult < 1:
            raise ValueError("Precondition failed: invalid schedule parameters.")

        if not use_restarts:
            t = min(current_step, total_steps)
            progress = float(t) / float(total_steps)
            lr = lr_min + 0.5 * (lr_max - lr_min) * (1.0 + math.cos(math.pi * progress))
            return {"learning_rate": lr, "current_cycle": 0}

        t_cur = current_step
        t_i = total_steps
        cycle = 0

        while t_cur >= t_i:
            t_cur -= t_i
            t_i *= t_mult
            cycle += 1

        progress = float(t_cur) / float(t_i)
        lr = lr_min + 0.5 * (lr_max - lr_min) * (1.0 + math.cos(math.pi * progress))

        return {
            "learning_rate": lr,
            "current_cycle": cycle,
        }
