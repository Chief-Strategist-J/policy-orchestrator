from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoCrossEntropyNll:
    """
    ---
    contract:
      algo_id: ALGO-NN-14
      name: NnAlgoCrossEntropyNll
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.loss
      - nn.cross_entropy
      - nn.nll
      - nn.multiclass
      - nn.classification
      inputs:
        type: object
        properties:
          logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: Unnormalized prediction scores Z of shape (B, C) where B is batch
              size and C is number of classes.
          targets:
            type: array
            items:
              type: integer
            description: Ground truth class indices y of length B, with y_i in [0, C-1]
              or equal to ignore_index.
          weight:
            type: array
            items:
              type: number
            description: Optional class weighting factors w of length C.
          ignore_index:
            type: integer
            default: -100
            description: Target value that is ignored and does not contribute to the loss
              or gradient.
          reduction:
            type: string
            enum:
            - mean
            - sum
            - none
            default: mean
            description: Reduction method over the batch dimension.
        required:
        - logits
        - targets
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Scalar reduced cross-entropy loss (if reduction is mean or sum).
          losses:
            type: array
            items:
              type: number
            description: Per-sample unreduced losses of length B (if reduction is none).
          probabilities:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized softmax probabilities P of shape (B, C).
          gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Analytic gradients dL/dZ of shape (B, C).
          valid_samples:
            type: integer
            description: Number of valid, non-ignored samples evaluated.
        required:
        - probabilities
        - gradients
        - valid_samples
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
        logits: Sequence[Sequence[float]],
        targets: Sequence[int],
        weight: Optional[Sequence[float]] = None,
        ignore_index: int = -100,
        reduction: Literal["mean", "sum", "none"] = "mean",
    ) -> Dict[str, Any]:
        b = len(logits)
        if b == 0:
            raise ValueError("Precondition failed: logits batch cannot be empty.")
        if len(targets) != b:
            raise ValueError(
                f"Precondition failed: targets length ({len(targets)}) must match logits batch size ({b})."
            )

        c = len(logits[0])
        if c == 0:
            raise ValueError("Precondition failed: class dimension C cannot be zero.")
        for row in logits:
            if len(row) != c:
                raise ValueError("Precondition failed: all logits rows must have identical class count C.")

        if weight is not None:
            if len(weight) != c:
                raise ValueError(
                    f"Precondition failed: weight vector length ({len(weight)}) must match class count ({c})."
                )
            for w in weight:
                if w < 0.0:
                    raise ValueError("Precondition failed: class weights must be non-negative.")

        probs: List[List[float]] = []
        log_probs: List[List[float]] = []

        for row in logits:
            max_val = max(row)
            sum_exp = sum(math.exp(z - max_val) for z in row)
            lse = max_val + math.log(sum_exp)
            p_row = [math.exp(z - lse) for z in row]
            lp_row = [z - lse for z in row]
            probs.append(p_row)
            log_probs.append(lp_row)

        sample_losses: List[float] = []
        grads: List[List[float]] = []
        total_weight = 0.0
        valid_count = 0

        for i in range(b):
            target_class = targets[i]
            if target_class == ignore_index:
                sample_losses.append(0.0)
                grads.append([0.0] * c)
                continue

            if not (0 <= target_class < c):
                raise ValueError(
                    f"Precondition failed: target class {target_class} out of bounds [0, {c-1}]."
                )

            w = weight[target_class] if weight is not None else 1.0
            nll = -log_probs[i][target_class]
            loss_i = w * nll
            sample_losses.append(loss_i)
            total_weight += w
            valid_count += 1

            grad_row = []
            for j in range(c):
                indicator = 1.0 if j == target_class else 0.0
                grad_row.append(w * (probs[i][j] - indicator))
            grads.append(grad_row)

        if reduction == "mean":
            norm_factor = total_weight if total_weight > 0.0 else 1.0
            scalar_loss = sum(sample_losses) / norm_factor
            reduced_grads = [[g / norm_factor for g in row] for row in grads]
            return {
                "loss": scalar_loss,
                "probabilities": probs,
                "gradients": reduced_grads,
                "valid_samples": valid_count,
            }
        elif reduction == "sum":
            scalar_loss = sum(sample_losses)
            return {
                "loss": scalar_loss,
                "probabilities": probs,
                "gradients": grads,
                "valid_samples": valid_count,
            }
        elif reduction == "none":
            return {
                "losses": sample_losses,
                "probabilities": probs,
                "gradients": grads,
                "valid_samples": valid_count,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized reduction mode {reduction}")
