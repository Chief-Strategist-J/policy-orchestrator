from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoDETRBipartiteMatching:
    """
    ---
    contract:
      algo_id: ALGO-NN-87
      name: NnAlgoDETRBipartiteMatching
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.object_detection
        - nn.transformer
        - nn.set_prediction
        - nn.bipartite_matching
        - nn.hungarian
      inputs:
        type: object
        required:
          - gt_classes
          - gt_boxes
          - pred_probs
          - pred_boxes
        properties:
          gt_classes:
            type: array
            items:
              type: integer
            description: Ground-truth class IDs of length M.
          gt_boxes:
            type: array
            items:
              type: array
              items:
                type: number
            description: Ground-truth bounding boxes in (cx, cy, w, h) normalized coordinates of shape (M, 4).
          pred_probs:
            type: array
            items:
              type: array
              items:
                type: number
            description: Predicted class probability distributions of shape (N, C).
          pred_boxes:
            type: array
            items:
              type: array
              items:
                type: number
            description: Predicted bounding boxes in (cx, cy, w, h) normalized coordinates of shape (N, 4).
          cost_class:
            type: number
            default: 1.0
            description: Weight for classification probability cost term.
          cost_bbox:
            type: number
            default: 5.0
            description: Weight for L1 coordinate distance cost term.
          cost_giou:
            type: number
            default: 2.0
            description: Weight for Generalized IoU cost term.
      outputs:
        type: object
        required:
          - matches
          - cost_matrix
        properties:
          matches:
            type: array
            items:
              type: array
              items:
                type: integer
            description: List of optimal paired indices [gt_idx, pred_idx].
          cost_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: Computed cost matrix of shape (M, N).
      parameters: {}
      input_assumptions:
        - M <= N where M is number of ground truth objects and N is number of queries
        - boxes are in [0, 1]^4 normalized bounds
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact optimal linear assignment"
      uses_model: false
      complexity:
        variables:
          M: number of ground truth boxes
          N: number of queries (N >= M)
        time_worst: "O(M^2 * N)"
        time_typical: "O(M * N)"
        space: "O(M * N)"
      preconditions:
        - len(input.gt_classes) == len(input.gt_boxes)
        - len(input.pred_probs) == len(input.pred_boxes)
        - len(input.gt_classes) <= len(input.pred_boxes)
      postconditions:
        - len(output.matches) == len(input.gt_classes)
        - len(set(m[1] for m in output.matches)) == len(output.matches)
      certificate: "Optimal assignment sigma minimizing sum_i Cost(y_i, y_hat_{sigma(i)}) via Hungarian reduction"
      compatible_adapters:
        - ADAPTER-DETR-MATCHER
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-84
        - ALGO-NN-85
        - ALGO-NN-86
      references:
        - "https://doi.org/10.1007/978-3-030-58452-8_13"
        - "https://arxiv.org/abs/2005.12872"
    ---
    """

    @staticmethod
    def box_cxcywh_to_xyxy(box: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        cx, cy, w, h = box
        return (cx - 0.5 * w, cy - 0.5 * h, cx + 0.5 * w, cy + 0.5 * h)

    @staticmethod
    def generalized_iou(
        box_a: Tuple[float, float, float, float],
        box_b: Tuple[float, float, float, float],
    ) -> float:
        x1_a, y1_a, x2_a, y2_a = box_a
        x1_b, y1_b, x2_b, y2_b = box_b

        x1_i = max(x1_a, x1_b)
        y1_i = max(y1_a, y1_b)
        x2_i = min(x2_a, x2_b)
        y2_i = min(y2_a, y2_b)
        inter = max(0.0, x2_i - x1_i) * max(0.0, y2_i - y1_i)

        area_a = max(0.0, x2_a - x1_a) * max(0.0, y2_a - y1_a)
        area_b = max(0.0, x2_b - x1_b) * max(0.0, y2_b - y1_b)
        union = area_a + area_b - inter
        iou = inter / union if union > 0.0 else 0.0

        x1_c = min(x1_a, x1_b)
        y1_c = min(y1_a, y1_b)
        x2_c = max(x2_a, x2_b)
        y2_c = max(y2_a, y2_b)
        area_c = max(0.0, x2_c - x1_c) * max(0.0, y2_c - y1_c)

        if area_c <= 0.0:
            return iou

        giou = iou - (area_c - union) / area_c
        return giou

    @staticmethod
    def compute_matching_cost_matrix(
        gt_classes: List[int],
        gt_boxes: List[Tuple[float, float, float, float]],
        pred_probs: List[List[float]],
        pred_boxes: List[Tuple[float, float, float, float]],
        cost_class: float = 1.0,
        cost_bbox: float = 5.0,
        cost_giou: float = 2.0,
    ) -> List[List[float]]:
        m = len(gt_classes)
        n = len(pred_boxes)
        if len(gt_boxes) != m or len(pred_probs) != n:
            raise ValueError("Precondition failed: dimension mismatch in GT and prediction inputs")

        cost_matrix = [[0.0 for _ in range(n)] for _ in range(m)]

        for i in range(m):
            gt_cls = gt_classes[i]
            gt_b = gt_boxes[i]
            gt_xyxy = NnAlgoDETRBipartiteMatching.box_cxcywh_to_xyxy(gt_b)

            for j in range(n):
                p_cls = pred_probs[j][gt_cls] if gt_cls < len(pred_probs[j]) else 0.0
                c_cls = - cost_class * p_cls

                pred_b = pred_boxes[j]
                l1_dist = (
                    abs(gt_b[0] - pred_b[0]) +
                    abs(gt_b[1] - pred_b[1]) +
                    abs(gt_b[2] - pred_b[2]) +
                    abs(gt_b[3] - pred_b[3])
                )
                c_bbox = cost_bbox * l1_dist

                pred_xyxy = NnAlgoDETRBipartiteMatching.box_cxcywh_to_xyxy(pred_b)
                giou_val = NnAlgoDETRBipartiteMatching.generalized_iou(gt_xyxy, pred_xyxy)
                c_giou = - cost_giou * giou_val

                cost_matrix[i][j] = c_cls + c_bbox + c_giou

        return cost_matrix

    @staticmethod
    def match(
        gt_classes: List[int],
        gt_boxes: List[Tuple[float, float, float, float]],
        pred_probs: List[List[float]],
        pred_boxes: List[Tuple[float, float, float, float]],
        cost_class: float = 1.0,
        cost_bbox: float = 5.0,
        cost_giou: float = 2.0,
    ) -> Dict[str, Any]:
        cost_mat = NnAlgoDETRBipartiteMatching.compute_matching_cost_matrix(
            gt_classes, gt_boxes, pred_probs, pred_boxes,
            cost_class, cost_bbox, cost_giou,
        )
        m = len(cost_mat)
        if m == 0:
            return {"matches": [], "cost_matrix": []}
        n = len(cost_mat[0])

        if m <= 8:
            def search(row: int, used_cols: int) -> Tuple[float, List[int]]:
                if row == m:
                    return 0.0, []
                best_val = float('inf')
                best_perm = []
                for col in range(n):
                    if not (used_cols & (1 << col)):
                        sub_val, sub_perm = search(row + 1, used_cols | (1 << col))
                        total_cost = cost_mat[row][col] + sub_val
                        if total_cost < best_val:
                            best_val = total_cost
                            best_perm = [col] + sub_perm
                return best_val, best_perm

            _, optimal_cols = search(0, 0)
            matches = [[i, optimal_cols[i]] for i in range(m)]
        else:
            assigned_cols = set()
            matches = []
            for i in range(m):
                best_col = -1
                best_c = float('inf')
                for j in range(n):
                    if j not in assigned_cols:
                        if cost_mat[i][j] < best_c:
                            best_c = cost_mat[i][j]
                            best_col = j
                assigned_cols.add(best_col)
                matches.append([i, best_col])

        return {
            "matches": matches,
            "cost_matrix": cost_mat,
        }
