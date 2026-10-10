from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoBinaryCrossEntropyLogits:
    """
    ---
    contract:
      algo_id: ALGO-NN-15
      name: NnAlgoBinaryCrossEntropyLogits
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.loss
        - nn.bce
        - nn.binary_classification
        - nn.multilabel
      inputs:
        type: object
        properties:
          logits:
            type: array
            items:
              type: number
            description: Unnormalized log-odds predictions z of length N.
          targets:
            type: array
            items:
              type: number
            description: Ground truth binary targets y in [0, 1] of length N.
          pos_weight:
            type: number
            default: 1.0
            description: Weight multiplier for positive targets (must be > 0).
          weight:
            type: array
            items:
              type: number
            description: Optional per-element weighting factors w of length N.
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
            description: Reduced scalar loss value (if reduction is mean or sum).
          losses:
            type: array
            items:
              type: number
            description: Per-element loss values of length N (if reduction is none).
          probabilities:
            type: array
            items:
              type: number
            description: Sigmoid output probabilities sigma(z) of length N.
          gradients:
            type: array
            items:
              type: number
            description: Analytic gradients dL/dz of length N.
          sample_count:
            type: integer
            description: Total sample count N.
        required:
          - probabilities
          - gradients
          - sample_count
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        logits: Sequence[float],
        targets: Sequence[float],
        pos_weight: float = 1.0,
        weight: Optional[Sequence[float]] = None,
        reduction: Literal["mean", "sum", "none"] = "mean",
    ) -> Dict[str, Any]:
        n = len(logits)
        if n == 0:
            raise ValueError("Precondition failed: logits array cannot be empty.")
        if len(targets) != n:
            raise ValueError(
                f"Precondition failed: targets length ({len(targets)}) must match logits length ({n})."
            )
        if pos_weight <= 0.0:
            raise ValueError(f"Precondition failed: pos_weight must be > 0, got {pos_weight}.")

        if weight is not None:
            if len(weight) != n:
                raise ValueError(
                    f"Precondition failed: weight array length ({len(weight)}) must match logits length ({n})."
                )
            for w in weight:
                if w < 0.0:
                    raise ValueError("Precondition failed: per-element weights must be non-negative.")

        element_losses: List[float] = []
        element_grads: List[float] = []
        probabilities: List[float] = []

        for i in range(n):
            z = logits[i]
            y = targets[i]
            if not (0.0 <= y <= 1.0):
                raise ValueError(f"Precondition failed: target value y[{i}]={y} must be in [0, 1].")

            w_elem = weight[i] if weight is not None else 1.0

            # Numerically stable sigmoid: sigma(z)
            if z >= 0.0:
                ez_neg = math.exp(-z)
                sig = 1.0 / (1.0 + ez_neg)
                # Stable loss: (1 - y) * z + max(-z, 0) + log(1 + exp(-|z|)) + (pos_weight - 1) * y * ...
                # Standard formulation: max(z, 0) - z*y + log(1 + exp(-|z|)) with pos_weight:
                # l_i = (1 - y) * z + (1 + (pos_weight - 1)*y) * (log(1 + exp(-z)))
                # Stable log(1 + exp(-z))
                log_term = math.log1p(ez_neg)
                loss_val = (1.0 - y) * z + (1.0 + (pos_weight - 1.0) * y) * log_term
            else:
                ez = math.exp(z)
                sig = ez / (1.0 + ez)
                # For z < 0: log(1 + exp(z)) - z * (pos_weight * y)
                log_term = math.log1p(ez)
                loss_val = (1.0 + (pos_weight - 1.0) * y) * log_term - pos_weight * y * z

            loss_val *= w_elem
            element_losses.append(loss_val)
            probabilities.append(sig)

            # Gradient: dL/dz = w * [ sig * (1 + (pos_weight - 1)*y) - pos_weight * y ]
            # When pos_weight == 1: sig - y
            grad_val = w_elem * (sig * (1.0 + (pos_weight - 1.0) * y) - pos_weight * y)
            element_grads.append(grad_val)

        if reduction == "mean":
            norm = sum(weight) if weight is not None else float(n)
            norm = norm if norm > 0.0 else 1.0
            scalar_loss = sum(element_losses) / norm
            reduced_grads = [g / norm for g in element_grads]
            return {
                "loss": scalar_loss,
                "probabilities": probabilities,
                "gradients": reduced_grads,
                "sample_count": n,
            }
        elif reduction == "sum":
            scalar_loss = sum(element_losses)
            return {
                "loss": scalar_loss,
                "probabilities": probabilities,
                "gradients": element_grads,
                "sample_count": n,
            }
        elif reduction == "none":
            return {
                "losses": element_losses,
                "probabilities": probabilities,
                "gradients": element_grads,
                "sample_count": n,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized reduction mode {reduction}")
