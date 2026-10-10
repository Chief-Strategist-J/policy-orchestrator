from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoFocalLoss:
    """
    ---
    contract:
      algo_id: ALGO-NN-17
      name: NnAlgoFocalLoss
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.loss
      - nn.focal_loss
      - nn.imbalanced_learning
      - nn.object_detection
      inputs:
        type: object
        properties:
          logits:
            type: array
            items:
              type: number
            description: Unnormalized binary log-odds predictions z of length N.
          targets:
            type: array
            items:
              type: integer
            description: Ground truth binary targets y in {0, 1} of length N.
          alpha:
            type: number
            default: 0.25
            description: Weighting factor alpha in (0, 1) for class 1 (class 0 gets 1
              - alpha).
          gamma:
            type: number
            default: 2.0
            description: Focusing parameter gamma >= 0 that modulates the easy example
              penalty.
          reduction:
            type: string
            enum:
            - mean
            - sum
            - none
            default: mean
            description: Reduction mode across samples.
        required:
        - logits
        - targets
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Reduced scalar focal loss (if reduction is mean or sum).
          losses:
            type: array
            items:
              type: number
            description: Per-element focal loss values of length N (if reduction is none).
          probabilities:
            type: array
            items:
              type: number
            description: Sigmoid probabilities p = sigma(z) of length N.
          gradients:
            type: array
            items:
              type: number
            description: Analytic gradients dL/dz of length N.
          sample_count:
            type: integer
            description: Number of samples N evaluated.
        required:
        - probabilities
        - gradients
        - sample_count
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
        logits: Sequence[float],
        targets: Sequence[int],
        alpha: float = 0.25,
        gamma: float = 2.0,
        reduction: Literal["mean", "sum", "none"] = "mean",
    ) -> Dict[str, Any]:
        n = len(logits)
        if n == 0:
            raise ValueError("Precondition failed: logits cannot be empty.")
        if len(targets) != n:
            raise ValueError(
                f"Precondition failed: targets length ({len(targets)}) must match logits length ({n})."
            )
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"Precondition failed: alpha must be in (0, 1), got {alpha}.")
        if gamma < 0.0:
            raise ValueError(f"Precondition failed: gamma must be non-negative, got {gamma}.")

        probs: List[float] = []
        element_losses: List[float] = []
        element_grads: List[float] = []

        for z, y in zip(logits, targets):
            if y not in (0, 1):
                raise ValueError(f"Precondition failed: binary target y must be 0 or 1, got {y}.")

            if z >= 0.0:
                ez_neg = math.exp(-z)
                p = 1.0 / (1.0 + ez_neg)
                log_p = -math.log1p(ez_neg)
                log_1_minus_p = -z - math.log1p(ez_neg)
            else:
                ez = math.exp(z)
                p = ez / (1.0 + ez)
                log_p = z - math.log1p(ez)
                log_1_minus_p = -math.log1p(ez)

            probs.append(p)

            if y == 1:
                p_t = p
                log_p_t = log_p
                alpha_t = alpha
                sign = 1.0
            else:
                p_t = 1.0 - p
                log_p_t = log_1_minus_p
                alpha_t = 1.0 - alpha
                sign = -1.0

            modulating_factor = (1.0 - p_t) ** gamma
            loss_i = -alpha_t * modulating_factor * log_p_t
            element_losses.append(loss_i)

            if gamma == 0.0:
                grad_i = alpha_t * (p_t - 1.0) * sign
            else:
                term = gamma * p_t * log_p_t + p_t - 1.0
                grad_i = alpha_t * modulating_factor * term * sign
            element_grads.append(grad_i)

        if reduction == "mean":
            scalar_loss = sum(element_losses) / float(n)
            reduced_grads = [g / float(n) for g in element_grads]
            return {
                "loss": scalar_loss,
                "probabilities": probs,
                "gradients": reduced_grads,
                "sample_count": n,
            }
        elif reduction == "sum":
            scalar_loss = sum(element_losses)
            return {
                "loss": scalar_loss,
                "probabilities": probs,
                "gradients": element_grads,
                "sample_count": n,
            }
        elif reduction == "none":
            return {
                "losses": element_losses,
                "probabilities": probs,
                "gradients": element_grads,
                "sample_count": n,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized reduction mode {reduction}")
