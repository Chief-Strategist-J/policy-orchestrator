from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoMetricLearningLosses:
    """
    ---
    contract:
      algo_id: ALGO-NN-18
      name: NnAlgoMetricLearningLosses
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.loss
      - nn.metric_learning
      - nn.triplet_loss
      - nn.arcface
      - nn.cosface
      inputs:
        type: object
        properties:
          mode:
            type: string
            enum:
            - triplet
            - arcface
            - cosface
            default: triplet
            description: Metric learning loss formulation.
          anchors:
            type: array
            items:
              type: array
              items:
                type: number
            description: Anchor feature embeddings A of shape (B, D) (for triplet mode).
          positives:
            type: array
            items:
              type: array
              items:
                type: number
            description: Positive feature embeddings P of shape (B, D) (for triplet mode).
          negatives:
            type: array
            items:
              type: array
              items:
                type: number
            description: Negative feature embeddings N of shape (B, D) (for triplet mode).
          margin:
            type: number
            default: 0.5
            description: Distance or angular margin m >= 0.
          embeddings:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized feature embeddings X of shape (B, D) (for ArcFace/CosFace).
          weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized class weight matrix W of shape (C, D) (for ArcFace/CosFace).
          targets:
            type: array
            items:
              type: integer
            description: Ground truth class labels y of length B (for ArcFace/CosFace).
          scale:
            type: number
            default: 30.0
            description: Inverse temperature scale factor s > 0 for angular losses.
        required:
        - mode
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Reduced scalar metric learning loss.
          active_triplets:
            type: integer
            description: Number of active triplets violating the margin constraint (for
              triplet mode).
          similarities:
            type: array
            items:
              type: array
              items:
                type: number
            description: Margin-adjusted cosine logits matrix of shape (B, C) (for ArcFace/CosFace).
        required:
        - loss
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
        mode: Literal["triplet", "arcface", "cosface"] = "triplet",
        anchors: Optional[Sequence[Sequence[float]]] = None,
        positives: Optional[Sequence[Sequence[float]]] = None,
        negatives: Optional[Sequence[Sequence[float]]] = None,
        margin: float = 0.5,
        embeddings: Optional[Sequence[Sequence[float]]] = None,
        weights: Optional[Sequence[Sequence[float]]] = None,
        targets: Optional[Sequence[int]] = None,
        scale: float = 30.0,
    ) -> Dict[str, Any]:
        if margin < 0.0:
            raise ValueError(f"Precondition failed: margin must be >= 0, got {margin}.")
        if scale <= 0.0:
            raise ValueError(f"Precondition failed: scale s must be > 0, got {scale}.")

        if mode == "triplet":
            if anchors is None or positives is None or negatives is None:
                raise ValueError("Precondition failed: triplet mode requires anchors, positives, and negatives.")
            b = len(anchors)
            if b == 0 or len(positives) != b or len(negatives) != b:
                raise ValueError("Precondition failed: all triplet batches must have identical non-zero length.")
            d = len(anchors[0])

            total_loss = 0.0
            active_count = 0
            for a, p, n in zip(anchors, positives, negatives):
                if len(a) != d or len(p) != d or len(n) != d:
                    raise ValueError("Precondition failed: embedding dimensions D must be identical.")
                d_ap = sum((ai - pi) ** 2 for ai, pi in zip(a, p))
                d_an = sum((ai - ni) ** 2 for ai, ni in zip(a, n))
                val = d_ap - d_an + margin
                if val > 0.0:
                    total_loss += val
                    active_count += 1

            return {
                "loss": total_loss / float(b),
                "active_triplets": active_count,
            }

        elif mode in ("arcface", "cosface"):
            if embeddings is None or weights is None or targets is None:
                raise ValueError("Precondition failed: angular mode requires embeddings, weights, and targets.")
            b = len(embeddings)
            if b == 0 or len(targets) != b:
                raise ValueError("Precondition failed: embeddings batch size must match targets length.")
            c = len(weights)
            d = len(weights[0])

            logits: List[List[float]] = []
            total_loss = 0.0

            for i in range(b):
                x = embeddings[i]
                y = targets[i]
                if not (0 <= y < c):
                    raise ValueError(f"Precondition failed: target {y} out of bounds [0, {c-1}].")

                x_norm = math.sqrt(sum(xi ** 2 for xi in x)) + 1e-12
                x_u = [xi / x_norm for xi in x]

                row_cos: List[float] = []
                for j in range(c):
                    w = weights[j]
                    w_norm = math.sqrt(sum(wj ** 2 for wj in w)) + 1e-12
                    cos_theta = sum(x_u[k] * (w[k] / w_norm) for k in range(d))
                    cos_theta = max(-1.0, min(1.0, cos_theta))
                    row_cos.append(cos_theta)

                row_logits: List[float] = []
                for j in range(c):
                    cos_th = row_cos[j]
                    if j == y:
                        if mode == "arcface":
                            theta = math.acos(cos_th)
                            target_logit = scale * math.cos(theta + margin)
                        else:
                            target_logit = scale * (cos_th - margin)
                        row_logits.append(target_logit)
                    else:
                        row_logits.append(scale * cos_th)

                logits.append(row_logits)

                max_z = max(row_logits)
                lse = max_z + math.log(sum(math.exp(z - max_z) for z in row_logits))
                total_loss += (lse - row_logits[y])

            return {
                "loss": total_loss / float(b),
                "similarities": logits,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized mode {mode}")
