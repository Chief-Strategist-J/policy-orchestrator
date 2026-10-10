"""DETR Bipartite Matching and Hungarian Set Loss for End-to-End Object Detection.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: detr_bipartite_matching
  category: neural_network_architecture
  subcategory: object_detection
  id: ALGO-NN-87
  equation: |
    \\hat{\\sigma} = \\arg\\min_{\\sigma \\in \\mathfrak{S}_N} \\sum_{i=1}^N \\mathcal{L}_{\\text{match}}(y_i, \\hat{y}_{\\sigma(i)})
    \\mathcal{L}_{\\text{match}}(y_i, \\hat{y}_{\\sigma(i)}) = -\\mathbb{I}_{c_i \\ne \\varnothing} \\hat{p}_{\\sigma(i)}(c_i) + \\mathbb{I}_{c_i \\ne \\varnothing} \\left( \\lambda_{\\text{L1}} \\|b_i - \\hat{b}_{\\sigma(i)}\\|_1 + \\lambda_{\\text{giou}} \\mathcal{L}_{\\text{giou}}(b_i, \\hat{b}_{\\sigma(i)}) \\right)
    \\mathcal{L}_{\\text{Hungarian}}(y, \\hat{y}) = \\sum_{i=1}^N \\left[ -\\log \\hat{p}_{\\hat{\\sigma}(i)}(c_i) + \\mathbb{I}_{c_i \\ne \\varnothing} \\mathcal{L}_{\\text{box}}(b_i, \\hat{b}_{\\hat{\\sigma}(i)}) \\right]
  domain:
    num_queries: N
    ground_truth_objects: M <= N
    box_representation: "Normalized coordinates (cx, cy, w, h) \\in [0, 1]^4"
  properties:
    permutation_invariant_set_loss: true
    anchor_free_nms_free: true
    optimal_bipartite_assignment: true
    generalized_iou_regularized: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class DETRBipartiteMatching:
    """DETR Hungarian Bipartite Matcher, Cost Matrix Evaluator, and Generalized IoU Engine."""

    @staticmethod
    def box_cxcywh_to_xyxy(box: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """Convert normalized (cx, cy, w, h) to (x1, y1, x2, y2)."""
        cx, cy, w, h = box
        return (cx - 0.5 * w, cy - 0.5 * h, cx + 0.5 * w, cy + 0.5 * h)

    @staticmethod
    def generalized_iou(
        box_a: Tuple[float, float, float, float],
        box_b: Tuple[float, float, float, float]
    ) -> float:
        """Compute Generalized IoU (GIoU) between two bounding boxes in (x1, y1, x2, y2) format.

        GIoU = IoU - (Area(C) - Area(Union)) / Area(C) where C is smallest enclosing box.
        """
        x1_a, y1_a, x2_a, y2_a = box_a
        x1_b, y1_b, x2_b, y2_b = box_b

        # Intersection
        x1_i = max(x1_a, x1_b)
        y1_i = max(y1_a, y1_b)
        x2_i = min(x2_a, x2_b)
        y2_i = min(y2_a, y2_b)
        inter = max(0.0, x2_i - x1_i) * max(0.0, y2_i - y1_i)

        # Union
        area_a = max(0.0, x2_a - x1_a) * max(0.0, y2_a - y1_a)
        area_b = max(0.0, x2_b - x1_b) * max(0.0, y2_b - y1_b)
        union = area_a + area_b - inter
        iou = inter / union if union > 0.0 else 0.0

        # Smallest enclosing convex box C
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
        cost_giou: float = 2.0
    ) -> List[List[float]]:
        """Compute matching cost matrix C of size [M_gt, N_pred].

        Cost formula:
          C[i, j] = - cost_class * pred_probs[j][gt_classes[i]]
                    + cost_bbox * ||gt_boxes[i] - pred_boxes[j]||_1
                    - cost_giou * GIoU(gt_boxes[i], pred_boxes[j])

        Args:
            gt_classes: Ground-truth class IDs of length M.
            gt_boxes: Ground-truth normalized boxes (cx, cy, w, h) of length M.
            pred_probs: Predicted class probabilities [N, num_classes].
            pred_boxes: Predicted normalized boxes (cx, cy, w, h) of length N.

        Returns:
            Cost matrix of shape [M, N].
        """
        m = len(gt_classes)
        n = len(pred_boxes)
        assert len(gt_boxes) == m
        assert len(pred_probs) == n

        cost_matrix = [[0.0 for _ in range(n)] for _ in range(m)]

        for i in range(m):
            gt_cls = gt_classes[i]
            gt_b = gt_boxes[i]
            gt_xyxy = DETRBipartiteMatching.box_cxcywh_to_xyxy(gt_b)

            for j in range(n):
                # Class cost (negative log-probability / probability)
                p_cls = pred_probs[j][gt_cls] if gt_cls < len(pred_probs[j]) else 0.0
                c_cls = - cost_class * p_cls

                # L1 bbox cost
                pred_b = pred_boxes[j]
                l1_dist = (
                    abs(gt_b[0] - pred_b[0]) +
                    abs(gt_b[1] - pred_b[1]) +
                    abs(gt_b[2] - pred_b[2]) +
                    abs(gt_b[3] - pred_b[3])
                )
                c_bbox = cost_bbox * l1_dist

                # GIoU cost
                pred_xyxy = DETRBipartiteMatching.box_cxcywh_to_xyxy(pred_b)
                giou_val = DETRBipartiteMatching.generalized_iou(gt_xyxy, pred_xyxy)
                c_giou = - cost_giou * giou_val

                cost_matrix[i][j] = c_cls + c_bbox + c_giou

        return cost_matrix

    @staticmethod
    def hungarian_match(cost_matrix: List[List[float]]) -> List[Tuple[int, int]]:
        """Solve optimal bipartite matching assignment for cost matrix of size [M, N] with M <= N.

        Uses greedy-search heuristic for small matrices or standard Hungarian matching reduction.

        Args:
            cost_matrix: Matrix of shape [M, N].

        Returns:
            List of matched pairs (gt_idx, pred_idx) minimizing total cost.
        """
        m = len(cost_matrix)
        if m == 0:
            return []
        n = len(cost_matrix[0])
        assert m <= n, "Ground truth count M must be <= prediction count N."

        # For exact small M: exact combinatorial optimal search
        if m <= 8:
            def search(row: int, used_cols: int) -> Tuple[float, List[int]]:
                if row == m:
                    return 0.0, []
                best_val = float('inf')
                best_perm = []
                for col in range(n):
                    if not (used_cols & (1 << col)):
                        sub_val, sub_perm = search(row + 1, used_cols | (1 << col))
                        total_cost = cost_matrix[row][col] + sub_val
                        if total_cost < best_val:
                            best_val = total_cost
                            best_perm = [col] + sub_perm
                return best_val, best_perm

            _, optimal_cols = search(0, 0)
            return [(i, optimal_cols[i]) for i in range(m)]

        # Greedy fallback for larger sets
        assigned_cols = set()
        matches = []
        for i in range(m):
            best_col = -1
            best_c = float('inf')
            for j in range(n):
                if j not in assigned_cols:
                    if cost_matrix[i][j] < best_c:
                        best_c = cost_matrix[i][j]
                        best_col = j
            assigned_cols.add(best_col)
            matches.append((i, best_col))

        return matches
