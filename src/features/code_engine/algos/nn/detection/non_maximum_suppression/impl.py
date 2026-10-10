from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoNonMaximumSuppression:
    """
    ---
    contract:
      algo_id: ALGO-NN-86
      name: NnAlgoNonMaximumSuppression
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.object_detection
        - nn.post_processing
        - nn.nms
        - nn.soft_nms
      inputs:
        type: object
        required:
          - boxes
          - scores
        properties:
          boxes:
            type: array
            items:
              type: array
              items:
                type: number
            description: Candidate bounding boxes in (x1, y1, x2, y2) format.
          scores:
            type: array
            items:
              type: number
            description: Confidence scores corresponding to candidate boxes.
          iou_threshold:
            type: number
            default: 0.5
            description: IoU suppression overlap threshold N_t.
          score_threshold:
            type: number
            default: 0.05
            description: Pre-filtering minimum confidence threshold.
          method:
            type: string
            enum: [hard, linear, gaussian]
            default: hard
            description: Suppression strategy (hard binary suppression or soft decay).
          sigma:
            type: number
            default: 0.5
            description: Gaussian decay parameter for Soft-NMS.
      outputs:
        type: object
        required:
          - kept_indices
        properties:
          kept_indices:
            type: array
            items:
              type: integer
            description: List of retained bounding box indices.
          decayed_scores:
            type: array
            items:
              type: number
            description: Optional decayed scores when method is soft.
      parameters: {}
      input_assumptions:
        - len(boxes) == len(scores) >= 1
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact pairwise bounding box geometry"
      uses_model: false
      complexity:
        variables:
          N: number of candidate boxes
        time_worst: "O(N^2)"
        time_typical: "O(N^2)"
        space: O(N)
      preconditions:
        - len(input.boxes) == len(input.scores)
      postconditions:
        - len(output.kept_indices) <= len(input.boxes)
      certificate: "Pruning candidates with IoU(M, b_i) >= N_t or attenuating scores via Gaussian exp(-IoU^2 / sigma)"
      compatible_adapters:
        - ADAPTER-NMS-POSTPROCESSOR
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-84
        - ALGO-NN-85
        - ALGO-NN-88
      references:
        - "https://doi.org/10.1109/ICCV.2017.593"
        - "https://arxiv.org/abs/1704.04503"
    ---
    """

    @staticmethod
    def box_iou(
        box_a: Tuple[float, float, float, float],
        box_b: Tuple[float, float, float, float],
    ) -> float:
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])

        inter_w = max(0.0, x2 - x1)
        inter_h = max(0.0, y2 - y1)
        inter_area = inter_w * inter_h

        area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
        area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])

        union_area = area_a + area_b - inter_area
        return inter_area / union_area if union_area > 0.0 else 0.0

    @staticmethod
    def hard_nms(
        boxes: List[Tuple[float, float, float, float]],
        scores: List[float],
        iou_threshold: float = 0.5,
        score_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        if len(boxes) != len(scores):
            raise ValueError("Precondition failed: len(input.boxes) == len(input.scores)")

        indices = [i for i in range(len(scores)) if scores[i] >= score_threshold]
        indices.sort(key=lambda i: scores[i], reverse=True)

        kept: List[int] = []
        while len(indices) > 0:
            current = indices[0]
            kept.append(current)

            remaining = []
            for idx in indices[1:]:
                iou = NnAlgoNonMaximumSuppression.box_iou(boxes[current], boxes[idx])
                if iou < iou_threshold:
                    remaining.append(idx)
            indices = remaining

        return {"kept_indices": kept}

    @staticmethod
    def soft_nms(
        boxes: List[Tuple[float, float, float, float]],
        scores: List[float],
        method: str = "gaussian",
        iou_threshold: float = 0.5,
        sigma: float = 0.5,
        score_threshold: float = 0.001,
    ) -> Dict[str, Any]:
        if method not in ("linear", "gaussian"):
            raise ValueError("Precondition failed: method must be 'linear' or 'gaussian'")
        if len(boxes) != len(scores):
            raise ValueError("Precondition failed: len(input.boxes) == len(input.scores)")

        b_list = list(boxes)
        s_list = list(scores)
        orig_indices = list(range(len(boxes)))
        n = len(boxes)

        for i in range(n):
            max_idx = i
            max_score = s_list[i]
            for pos in range(i + 1, n):
                if s_list[pos] > max_score:
                    max_score = s_list[pos]
                    max_idx = pos

            b_list[i], b_list[max_idx] = b_list[max_idx], b_list[i]
            s_list[i], s_list[max_idx] = s_list[max_idx], s_list[i]
            orig_indices[i], orig_indices[max_idx] = orig_indices[max_idx], orig_indices[i]

            current_box = b_list[i]
            for pos in range(i + 1, n):
                iou = NnAlgoNonMaximumSuppression.box_iou(current_box, b_list[pos])
                if method == "linear":
                    weight = 1.0 - iou if iou >= iou_threshold else 1.0
                else:
                    weight = math.exp(-(iou * iou) / max(1e-7, sigma))
                s_list[pos] = s_list[pos] * weight

        kept_indices = []
        decayed_scores = []
        for i in range(n):
            if s_list[i] >= score_threshold:
                kept_indices.append(orig_indices[i])
                decayed_scores.append(s_list[i])

        return {
            "kept_indices": kept_indices,
            "decayed_scores": decayed_scores,
        }
