from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoOverlapSegmentationLosses:
    """
    ---
    contract:
      algo_id: ALGO-NN-21
      name: NnAlgoOverlapSegmentationLosses
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.loss
      - nn.segmentation
      - nn.dice_loss
      - nn.iou_loss
      - nn.jaccard
      inputs:
        type: object
        properties:
          probabilities:
            type: array
            items:
              type: number
            description: Predicted foreground probabilities p in [0, 1] of length N (flattened
              pixels/voxels).
          targets:
            type: array
            items:
              type: number
            description: Ground truth binary segmentation masks g in {0, 1} of length
              N.
          loss_type:
            type: string
            enum:
            - dice
            - iou
            default: dice
            description: Specific overlap loss formulation.
          smooth:
            type: number
            default: 1.0
            description: Smoothing epsilon constant > 0 added to numerator and denominator
              to prevent division by zero.
        required:
        - probabilities
        - targets
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Scalar overlap segmentation loss in [0, 1].
          dice_coefficient:
            type: number
            description: Soft Dice overlap score in [0, 1].
          iou_score:
            type: number
            description: Soft Jaccard/IoU score in [0, 1].
          gradients:
            type: array
            items:
              type: number
            description: Analytic gradients dL/dp of length N.
        required:
        - loss
        - gradients
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
        probabilities: Sequence[float],
        targets: Sequence[float],
        loss_type: Literal["dice", "iou"] = "dice",
        smooth: float = 1.0,
    ) -> Dict[str, Any]:
        n = len(probabilities)
        if n == 0:
            raise ValueError("Precondition failed: probabilities array cannot be empty.")
        if len(targets) != n:
            raise ValueError(
                f"Precondition failed: targets length ({len(targets)}) must match probabilities ({n})."
            )
        if smooth <= 0.0:
            raise ValueError(f"Precondition failed: smooth epsilon must be > 0, got {smooth}.")

        intersection = 0.0
        sum_p = 0.0
        sum_g = 0.0

        for p, g in zip(probabilities, targets):
            if not (0.0 <= p <= 1.0):
                raise ValueError(f"Precondition failed: predicted probability {p} must be in [0, 1].")
            if not (0.0 <= g <= 1.0):
                raise ValueError(f"Precondition failed: ground truth target {g} must be in [0, 1].")
            intersection += p * g
            sum_p += p
            sum_g += g

        dice_num = 2.0 * intersection + smooth
        dice_den = sum_p + sum_g + smooth
        dice_coeff = dice_num / dice_den
        dice_loss = 1.0 - dice_coeff

        iou_num = intersection + smooth
        iou_den = sum_p + sum_g - intersection + smooth
        iou_score = iou_num / iou_den
        iou_loss = 1.0 - iou_score

        grads: List[float] = []
        if loss_type == "dice":
            loss_val = dice_loss
            for p, g in zip(probabilities, targets):
                g_grad = -(2.0 * g * dice_den - dice_num) / (dice_den ** 2)
                grads.append(g_grad)
        elif loss_type == "iou":
            loss_val = iou_loss
            for p, g in zip(probabilities, targets):
                g_grad = -(g * iou_den - (1.0 - g) * iou_num) / (iou_den ** 2)
                grads.append(g_grad)
        else:
            raise ValueError(f"Precondition failed: unrecognized loss_type {loss_type}")

        return {
            "loss": loss_val,
            "dice_coefficient": dice_coeff,
            "iou_score": iou_score,
            "gradients": grads,
        }
