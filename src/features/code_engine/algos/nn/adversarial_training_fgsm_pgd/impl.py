from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoAdversarialTrainingFgsmPgd:
    """
    ---
    contract:
      algo_id: ALGO-NN-63
      name: NnAlgoAdversarialTrainingFgsmPgd
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.adversarial_training
        - nn.fgsm
        - nn.pgd
        - nn.robustness
      inputs:
        type: object
        properties:
          clean_input:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D clean input activation/feature tensor X of shape (B, D).
          gradient_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D input loss gradient tensor nabla_x L(x, y) of shape (B, D).
          epsilon:
            type: number
            default: 0.03
            description: Maximum allowable L_inf perturbation radius eps > 0.
          step_size:
            type: number
            default: 0.01
            description: Step size alpha for iterative gradient ascent steps.
          num_steps:
            type: integer
            default: 1
            description: Number of ascent steps K (K=1 corresponds to FGSM; K>1 corresponds to PGD).
          clip_min:
            type: number
            default: 0.0
            description: Lower valid bound for input clamping.
          clip_max:
            type: number
            default: 1.0
            description: Upper valid bound for input clamping.
        required:
          - clean_input
          - gradient_matrix
      outputs:
        type: object
        properties:
          adversarial_input:
            type: array
            items:
              type: array
              items:
                type: number
            description: Perturbed adversarial tensor X_adv of shape (B, D).
          perturbation:
            type: array
            items:
              type: array
              items:
                type: number
            description: Net perturbation delta = X_adv - X of shape (B, D).
          l_inf_norm:
            type: number
            description: Maximum observed L_inf perturbation magnitude ||delta||_inf.
        required:
          - adversarial_input
          - perturbation
          - l_inf_norm
      parameters: {}
      input_assumptions:
        - clean_input and gradient_matrix must be non-empty 2D arrays of identical shape (B, D) with B >= 1 and D >= 1.
        - epsilon and step_size must be strictly positive.
        - num_steps must be an integer >= 1.
        - clip_min < clip_max.
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
          D: feature dimension
          K: number of steps
        time_worst: O(K * B * D)
        time_typical: O(K * B * D)
        space: O(B * D)
      preconditions:
        - len(clean_input) > 0 and len(clean_input[0]) > 0
        - len(gradient_matrix) == len(clean_input) and len(gradient_matrix[0]) == len(clean_input[0])
        - all(len(row) == len(clean_input[0]) for row in clean_input)
        - all(len(row) == len(clean_input[0]) for row in gradient_matrix)
        - epsilon > 0.0
        - step_size > 0.0
        - num_steps >= 1
        - clip_min < clip_max
      postconditions:
        - len(output.adversarial_input) == len(clean_input)
        - len(output.adversarial_input[0]) == len(clean_input[0])
        - len(output.perturbation) == len(clean_input)
        - len(output.perturbation[0]) == len(clean_input[0])
        - output.l_inf_norm <= epsilon + 1e-7
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-61
        - ALGO-NN-64
      references:
        - goodfellow2014explaining
        - madry2018towards
    ---
    """

    @staticmethod
    def generate_adversarial(
        clean_input: Sequence[Sequence[float]],
        gradient_matrix: Sequence[Sequence[float]],
        epsilon: float = 0.03,
        step_size: float = 0.01,
        num_steps: int = 1,
        clip_min: float = 0.0,
        clip_max: float = 1.0,
    ) -> Dict[str, Any]:
        if not clean_input or not clean_input[0]:
            raise ValueError("Precondition failed: clean_input must be non-empty 2D array.")
        B = len(clean_input)
        D = len(clean_input[0])

        if len(gradient_matrix) != B or len(gradient_matrix[0]) != D:
            raise ValueError("Precondition failed: gradient_matrix shape must match clean_input.")

        for row in clean_input:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in clean_input.")
        for row in gradient_matrix:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in gradient_matrix.")

        if epsilon <= 0.0:
            raise ValueError("Precondition failed: epsilon must be strictly positive.")
        if step_size <= 0.0:
            raise ValueError("Precondition failed: step_size must be strictly positive.")
        if num_steps < 1:
            raise ValueError("Precondition failed: num_steps must be >= 1.")
        if clip_min >= clip_max:
            raise ValueError("Precondition failed: clip_min must be strictly less than clip_max.")

        # Initialize perturbed candidate
        x_adv = [[float(clean_input[i][j]) for j in range(D)] for i in range(B)]
        effective_alpha = epsilon if num_steps == 1 else step_size

        for _ in range(num_steps):
            for i in range(B):
                for j in range(D):
                    g = gradient_matrix[i][j]
                    sign_g = 1.0 if g > 0 else (-1.0 if g < 0 else 0.0)

                    # Gradient ascent step
                    val = x_adv[i][j] + effective_alpha * sign_g

                    # Project back onto L_inf epsilon-ball around clean_input
                    orig = clean_input[i][j]
                    val = max(orig - epsilon, min(orig + epsilon, val))

                    # Clamping to valid pixel domain
                    val = max(clip_min, min(clip_max, val))
                    x_adv[i][j] = val

        # Calculate final perturbation delta and L_inf norm
        perturbation: List[List[float]] = [[0.0] * D for _ in range(B)]
        max_inf = 0.0
        for i in range(B):
            for j in range(D):
                d = x_adv[i][j] - clean_input[i][j]
                perturbation[i][j] = d
                if abs(d) > max_inf:
                    max_inf = abs(d)

        return {
            "adversarial_input": x_adv,
            "perturbation": perturbation,
            "l_inf_norm": max_inf,
        }
