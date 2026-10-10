from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoRegressionLosses:
    """
    ---
    contract:
      algo_id: ALGO-NN-13
      name: NnAlgoRegressionLosses
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.loss
        - nn.regression
        - nn.mse
        - nn.mae
        - nn.huber
        - nn.quantile
      inputs:
        type: object
        properties:
          predictions:
            type: array
            items:
              type: number
            description: Predicted continuous values y_hat of length N.
          targets:
            type: array
            items:
              type: number
            description: Ground truth continuous target values y of length N.
          loss_type:
            type: string
            enum:
              - mse
              - mae
              - huber
              - quantile
            default: mse
            description: Specific regression loss formulation to evaluate.
          delta:
            type: number
            default: 1.0
            description: Transition threshold delta for Huber loss (must be > 0).
          quantile:
            type: number
            default: 0.5
            description: Quantile level tau in (0, 1) for pinball/quantile loss.
          reduction:
            type: string
            enum:
              - mean
              - sum
              - none
            default: mean
            description: Reduction method across the batch elements.
        required:
          - predictions
          - targets
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Scalar reduced regression loss value (if reduction is mean or sum).
          losses:
            type: array
            items:
              type: number
            description: Per-element unreduced loss values (if reduction is none).
          gradients:
            type: array
            items:
              type: number
            description: Analytic gradients dL/d(y_hat) with respect to predictions of length N.
          loss_type:
            type: string
            description: The applied loss formulation.
          sample_count:
            type: integer
            description: Number of samples N evaluated.
        required:
          - gradients
          - loss_type
          - sample_count
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        predictions: Sequence[float],
        targets: Sequence[float],
        loss_type: Literal["mse", "mae", "huber", "quantile"] = "mse",
        delta: float = 1.0,
        quantile: float = 0.5,
        reduction: Literal["mean", "sum", "none"] = "mean",
    ) -> Dict[str, Any]:
        if len(predictions) == 0:
            raise ValueError("Precondition failed: predictions list cannot be empty.")
        if len(predictions) != len(targets):
            raise ValueError(
                f"Precondition failed: predictions length ({len(predictions)}) must match targets length ({len(targets)})."
            )
        if loss_type == "huber" and delta <= 0.0:
            raise ValueError(f"Precondition failed: delta must be > 0 for Huber loss, got {delta}.")
        if loss_type == "quantile" and not (0.0 < quantile < 1.0):
            raise ValueError(f"Precondition failed: quantile must be in (0, 1), got {quantile}.")

        n = len(predictions)
        element_losses: List[float] = []
        element_grads: List[float] = []

        for y_hat, y in zip(predictions, targets):
            diff = y_hat - y
            abs_diff = abs(diff)

            if loss_type == "mse":
                loss_val = 0.5 * (diff ** 2)
                grad_val = diff
            elif loss_type == "mae":
                loss_val = abs_diff
                grad_val = 1.0 if diff > 0.0 else (-1.0 if diff < 0.0 else 0.0)
            elif loss_type == "huber":
                if abs_diff <= delta:
                    loss_val = 0.5 * (diff ** 2)
                    grad_val = diff
                else:
                    loss_val = delta * (abs_diff - 0.5 * delta)
                    grad_val = delta * (1.0 if diff > 0.0 else -1.0)
            elif loss_type == "quantile":
                if diff >= 0.0:
                    loss_val = quantile * diff
                    grad_val = quantile
                else:
                    loss_val = (quantile - 1.0) * diff
                    grad_val = quantile - 1.0
            else:
                raise ValueError(f"Precondition failed: unrecognized loss_type {loss_type}")

            element_losses.append(loss_val)
            element_grads.append(grad_val)

        if reduction == "mean":
            scalar_loss = sum(element_losses) / float(n)
            reduced_grads = [g / float(n) for g in element_grads]
            return {
                "loss": scalar_loss,
                "gradients": reduced_grads,
                "loss_type": loss_type,
                "sample_count": n,
            }
        elif reduction == "sum":
            scalar_loss = sum(element_losses)
            return {
                "loss": scalar_loss,
                "gradients": element_grads,
                "loss_type": loss_type,
                "sample_count": n,
            }
        elif reduction == "none":
            return {
                "losses": element_losses,
                "gradients": element_grads,
                "loss_type": loss_type,
                "sample_count": n,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized reduction mode {reduction}")
