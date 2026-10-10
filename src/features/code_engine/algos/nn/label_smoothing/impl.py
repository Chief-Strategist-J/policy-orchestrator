from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLabelSmoothing:
    """
    ---
    contract:
      algo_id: ALGO-NN-16
      name: NnAlgoLabelSmoothing
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.loss
        - nn.regularization
        - nn.label_smoothing
        - nn.calibration
      inputs:
        type: object
        properties:
          logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: Unnormalized prediction scores Z of shape (B, C).
          targets:
            type: array
            items:
              type: integer
            description: Ground truth class indices y of length B.
          epsilon:
            type: number
            default: 0.1
            description: Smoothing factor epsilon in [0, 1).
          reduction:
            type: string
            enum:
              - mean
              - sum
              - none
            default: mean
            description: Reduction mode over the batch dimension.
        required:
          - logits
          - targets
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Reduced scalar smoothed cross-entropy loss (if reduction is mean or sum).
          losses:
            type: array
            items:
              type: number
            description: Per-sample unreduced losses of length B (if reduction is none).
          smooth_targets:
            type: array
            items:
              type: array
              items:
                type: number
            description: Smoothed soft target probability distributions of shape (B, C).
          probabilities:
            type: array
            items:
              type: array
              items:
                type: number
            description: Softmax predicted probabilities of shape (B, C).
          gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Analytic gradients dL/dZ of shape (B, C).
        required:
          - smooth_targets
          - probabilities
          - gradients
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        logits: Sequence[Sequence[float]],
        targets: Sequence[int],
        epsilon: float = 0.1,
        reduction: Literal["mean", "sum", "none"] = "mean",
    ) -> Dict[str, Any]:
        b = len(logits)
        if b == 0:
            raise ValueError("Precondition failed: logits batch cannot be empty.")
        if len(targets) != b:
            raise ValueError(
                f"Precondition failed: targets length ({len(targets)}) must match logits batch size ({b})."
            )
        if not (0.0 <= epsilon < 1.0):
            raise ValueError(f"Precondition failed: epsilon must be in [0, 1), got {epsilon}.")

        c = len(logits[0])
        if c <= 1:
            raise ValueError(f"Precondition failed: class dimension C must be > 1, got {c}.")

        uniform_prob = epsilon / float(c)
        one_minus_eps = 1.0 - epsilon

        probs: List[List[float]] = []
        log_probs: List[List[float]] = []
        smooth_targets: List[List[float]] = []
        sample_losses: List[float] = []
        grads: List[List[float]] = []

        for i in range(b):
            row = logits[i]
            y = targets[i]
            if not (0 <= y < c):
                raise ValueError(f"Precondition failed: target {y} out of bounds [0, {c-1}].")

            max_z = max(row)
            sum_exp = sum(math.exp(z - max_z) for z in row)
            lse = max_z + math.log(sum_exp)
            p_row = [math.exp(z - lse) for z in row]
            lp_row = [z - lse for z in row]
            probs.append(p_row)
            log_probs.append(lp_row)

            q_row = [uniform_prob] * c
            q_row[y] += one_minus_eps
            smooth_targets.append(q_row)

            loss_i = -sum(q_row[j] * lp_row[j] for j in range(c))
            sample_losses.append(loss_i)

            grad_row = [p_row[j] - q_row[j] for j in range(c)]
            grads.append(grad_row)

        if reduction == "mean":
            scalar_loss = sum(sample_losses) / float(b)
            reduced_grads = [[g / float(b) for g in r] for r in grads]
            return {
                "loss": scalar_loss,
                "smooth_targets": smooth_targets,
                "probabilities": probs,
                "gradients": reduced_grads,
            }
        elif reduction == "sum":
            scalar_loss = sum(sample_losses)
            return {
                "loss": scalar_loss,
                "smooth_targets": smooth_targets,
                "probabilities": probs,
                "gradients": grads,
            }
        elif reduction == "none":
            return {
                "losses": sample_losses,
                "smooth_targets": smooth_targets,
                "probabilities": probs,
                "gradients": grads,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized reduction mode {reduction}")
