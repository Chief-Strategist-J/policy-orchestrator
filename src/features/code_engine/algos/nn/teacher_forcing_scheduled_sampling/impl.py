from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoTeacherForcingScheduledSampling:
    """
    ---
    contract:
      algo_id: ALGO-NN-97
      name: NnAlgoTeacherForcingScheduledSampling
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.scheduled_sampling
        - nn.teacher_forcing
        - nn.curriculum
        - nn.sequence
      inputs:
        type: object
        required:
          - iteration
          - schedule_type
        properties:
          iteration:
            type: integer
            description: Current training iteration step index i >= 0.
          schedule_type:
            type: string
            enum:
              - linear
              - exponential
              - inverse_sigmoid
            description: Curriculum decay function profile.
          k:
            type: number
            description: Decay scaling factor parameter.
          eps_min:
            type: number
            description: Minimum teacher forcing probability floor.
      outputs:
        type: object
        required:
          - epsilon
        properties:
          epsilon:
            type: number
            description: Scheduled probability of ground-truth token selection in [eps_min, 1.0].
      parameters:
        k: 1000.0
        eps_min: 0.05
      input_assumptions:
        - iteration >= 0
        - schedule_type is one of linear, exponential, inverse_sigmoid
        - 0.0 <= eps_min <= 1.0
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Standard IEEE-754 floating point precision"
      uses_model: false
      complexity:
        variables:
          V: vocabulary size
        time_worst: "O(V)"
        time_typical: "O(1)"
        space: "O(1)"
      preconditions:
        - input.iteration >= 0
        - input.schedule_type in ["linear", "exponential", "inverse_sigmoid"]
      postconditions:
        - output.epsilon >= 0.0 and output.epsilon <= 1.0
      certificate: "\\epsilon_i = f(i, k) \\in [\\epsilon_{\\min}, 1.0]"
      compatible_adapters:
        - ADAPTER-SEQ2SEQ-TRAINER
        - ADAPTER-CURRICULUM-SAMPLER
      related_algos:
        - ALGO-NN-95
        - ALGO-NN-96
        - ALGO-NN-98
      references:
        - "https://arxiv.org/abs/1506.03099"
        - "https://doi.org/10.1162/neco.1989.1.2.270"
    ---
    """

    @staticmethod
    def get_scheduled_epsilon(
        iteration: int,
        schedule_type: str = "inverse_sigmoid",
        k: float = 1000.0,
        eps_min: float = 0.05,
    ) -> float:
        if iteration < 0:
            raise ValueError(f"Precondition failed: iteration {iteration} must be non-negative")

        if schedule_type == "linear":
            eps = 1.0 - (float(iteration) / max(1.0, k))
        elif schedule_type == "exponential":
            decay_rate = max(0.001, min(0.9999, k))
            eps = decay_rate**iteration
        elif schedule_type == "inverse_sigmoid":
            scaled = float(iteration) / max(1.0, k)
            if scaled > 50.0:
                eps = 0.0
            else:
                eps = k / (k + math.exp(scaled))
        else:
            raise ValueError(f"Precondition failed: unknown schedule type '{schedule_type}'")

        return max(eps_min, min(1.0, eps))

    @staticmethod
    def select_input_token(
        gt_token: int,
        predicted_logits: List[float],
        epsilon: float,
        rng: Optional[random.Random] = None,
    ) -> Tuple[int, bool]:
        if not predicted_logits or len(predicted_logits) == 0:
            raise ValueError("Precondition failed: predicted_logits must be non-empty")
        if epsilon < 0.0 or epsilon > 1.0:
            raise ValueError(f"Precondition failed: epsilon {epsilon} must be in [0.0, 1.0]")

        r = rng.random() if rng is not None else random.random()

        if r < epsilon:
            return gt_token, True
        else:
            best_token = 0
            best_logit = predicted_logits[0]
            for v in range(1, len(predicted_logits)):
                if predicted_logits[v] > best_logit:
                    best_logit = predicted_logits[v]
                    best_token = v
            return best_token, False
