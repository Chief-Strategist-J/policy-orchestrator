from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoConsistencyPseudoLabeling:
    """
    ---
    contract:
      algo_id: ALGO-NN-64
      name: NnAlgoConsistencyPseudoLabeling
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.semi_supervised
        - nn.pseudo_labeling
        - nn.consistency_regularization
        - nn.fixmatch
      inputs:
        type: object
        properties:
          weak_predictions:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D probability distribution matrix Q of shape (B, K) on weakly augmented inputs (rows sum to 1.0).
          strong_logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D unnormalized logit matrix Z of shape (B, K) on strongly augmented inputs.
          threshold:
            type: number
            default: 0.95
            description: Confidence cutoff threshold tau in (0.0, 1.0) required to retain a pseudo-label.
        required:
          - weak_predictions
          - strong_logits
      outputs:
        type: object
        properties:
          pseudo_labels:
            type: array
            items:
              type: integer
            description: Assigned hard class indices of length B (-1 if below threshold).
          mask:
            type: array
            items:
              type: number
            description: Binary selection indicator vector of length B (1.0 if confident, 0.0 otherwise).
          loss_per_sample:
            type: array
            items:
              type: number
            description: Masked cross-entropy loss values for each unlabeled sample.
          unsupervised_loss:
            type: number
            description: Average masked consistency loss across the batch.
          mask_rate:
            type: number
            description: Proportion of samples in the batch exceeding the confidence threshold.
        required:
          - pseudo_labels
          - mask
          - loss_per_sample
          - unsupervised_loss
          - mask_rate
      parameters: {}
      input_assumptions:
        - weak_predictions and strong_logits must be non-empty 2D arrays of matching shape (B, K) with B >= 1 and K >= 1.
        - Rows of weak_predictions must be valid non-negative probability distributions.
        - threshold tau must be in (0.0, 1.0).
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
          B: unlabeled batch size
          K: class count
        time_worst: O(B * K)
        time_typical: O(B * K)
        space: O(B)
      preconditions:
        - len(weak_predictions) > 0 and len(weak_predictions[0]) > 0
        - len(strong_logits) == len(weak_predictions) and len(strong_logits[0]) == len(weak_predictions[0])
        - all(len(row) == len(weak_predictions[0]) for row in weak_predictions)
        - all(len(row) == len(weak_predictions[0]) for row in strong_logits)
        - 0.0 < threshold < 1.0
      postconditions:
        - len(output.pseudo_labels) == len(weak_predictions)
        - len(output.mask) == len(weak_predictions)
        - len(output.loss_per_sample) == len(weak_predictions)
        - 0.0 <= output.mask_rate <= 1.0
        - output.unsupervised_loss >= 0.0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-61
        - ALGO-NN-62
      references:
        - sohn2020fixmatch
        - tarvainen2017mean
    ---
    """

    @staticmethod
    def compute_loss(
        weak_predictions: Sequence[Sequence[float]],
        strong_logits: Sequence[Sequence[float]],
        threshold: float = 0.95,
    ) -> Dict[str, Any]:
        if not weak_predictions or not weak_predictions[0]:
            raise ValueError("Precondition failed: weak_predictions must be non-empty 2D array.")
        B = len(weak_predictions)
        K = len(weak_predictions[0])

        if len(strong_logits) != B or len(strong_logits[0]) != K:
            raise ValueError("Precondition failed: strong_logits shape must match weak_predictions.")

        for row in weak_predictions:
            if len(row) != K:
                raise ValueError("Precondition failed: inconsistent class count in weak_predictions.")
        for row in strong_logits:
            if len(row) != K:
                raise ValueError("Precondition failed: inconsistent class count in strong_logits.")

        if not (0.0 < threshold < 1.0):
            raise ValueError("Precondition failed: threshold must be in (0.0, 1.0).")

        pseudo_labels: List[int] = [-1] * B
        mask: List[float] = [0.0] * B
        loss_per_sample: List[float] = [0.0] * B

        for i in range(B):
            # 1. Find max probability class from weak prediction
            max_prob = -1.0
            best_k = -1
            for k in range(K):
                p = weak_predictions[i][k]
                if p > max_prob:
                    max_prob = p
                    best_k = k

            if max_prob >= threshold:
                mask[i] = 1.0
                pseudo_labels[i] = best_k

                # 2. Compute cross-entropy on strong logits: -log(softmax(strong_logits)[best_k])
                row_logits = strong_logits[i]
                max_logit = max(row_logits)
                exp_sum = sum(math.exp(z - max_logit) for z in row_logits)
                log_sum_exp = max_logit + math.log(exp_sum)
                log_prob_target = row_logits[best_k] - log_sum_exp
                ce_loss = -log_prob_target
                loss_per_sample[i] = max(0.0, ce_loss)
            else:
                mask[i] = 0.0
                pseudo_labels[i] = -1
                loss_per_sample[i] = 0.0

        mask_count = sum(mask)
        mask_rate = mask_count / float(B)
        unsupervised_loss = (sum(loss_per_sample) / float(B)) if B > 0 else 0.0

        return {
            "pseudo_labels": pseudo_labels,
            "mask": mask,
            "loss_per_sample": loss_per_sample,
            "unsupervised_loss": unsupervised_loss,
            "mask_rate": mask_rate,
        }
