"""Non-Maximum Suppression (Hard NMS, Linear Soft-NMS, and Gaussian Soft-NMS).

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: non_maximum_suppression
  category: neural_network_architecture
  subcategory: object_detection
  id: ALGO-NN-86
  equation: |
    s_i^{\\text{hard}} = \\begin{cases} s_i & \\text{if } \\text{IoU}(M, b_i) < N_t \\\\ 0 & \\text{if } \\text{IoU}(M, b_i) \\ge N_t \\end{cases}
    s_i^{\\text{gaussian}} = s_i \\cdot \\exp\\left( -\\frac{\\text{IoU}(M, b_i)^2}{\\sigma} \\right)
    s_i^{\\text{linear}} = s_i \\cdot (1 - \\text{IoU}(M, b_i)) \\quad \\text{for } \\text{IoU}(M, b_i) \\ge N_t
  domain:
    iou_threshold: "N_t \\in (0, 1)"
    gaussian_variance: "\\sigma > 0"
    score_threshold: "\\tau \\ge 0"
  properties:
    duplicate_suppression: true
    crowded_scene_soft_weighting: true
    asymptotic_quadratic_complexity: true
    class_independent_or_batched: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class NonMaximumSuppression:
    """Non-Maximum Suppression (Hard, Linear, and Gaussian Soft-NMS) Algorithms."""

    @staticmethod
    def box_iou(
        box_a: Tuple[float, float, float, float],
        box_b: Tuple[float, float, float, float]
    ) -> float:
        """Compute Intersection-over-Union (IoU) of two boxes [x1, y1, x2, y2]."""
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
        score_threshold: float = 0.05
    ) -> List[int]:
        """Classic Hard Non-Maximum Suppression.

        Args:
            boxes: List of candidate bounding boxes (x1, y1, x2, y2).
            scores: Confidence score per box.
            iou_threshold: Overlap threshold above which suppressed boxes are purged.
            score_threshold: Pre-filtering minimum score.

        Returns:
            List of kept box integer indices.
        """
        assert len(boxes) == len(scores), "Boxes and scores length must match."
        indices = [i for i in range(len(scores)) if scores[i] >= score_threshold]
        # Sort descending by score
        indices.sort(key=lambda i: scores[i], reverse=True)

        kept: List[int] = []
        while len(indices) > 0:
            current = indices[0]
            kept.append(current)

            remaining = []
            for idx in indices[1:]:
                iou = NonMaximumSuppression.box_iou(boxes[current], boxes[idx])
                if iou < iou_threshold:
                    remaining.append(idx)
            indices = remaining

        return kept

    @staticmethod
    def soft_nms(
        boxes: List[Tuple[float, float, float, float]],
        scores: List[float],
        method: str = "gaussian",
        iou_threshold: float = 0.5,
        sigma: float = 0.5,
        score_threshold: float = 0.001
    ) -> List[Tuple[int, float]]:
        """Soft-NMS with Linear or Gaussian continuous score decay.

        Args:
            boxes: List of bounding boxes.
            scores: Initial confidence scores.
            method: 'linear' or 'gaussian'.
            iou_threshold: Linear threshold (used if method == 'linear').
            sigma: Gaussian dispersion parameter.
            score_threshold: Final score cutoff.

        Returns:
            List of tuples (box_index, decayed_score) for retained detections.
        """
        assert method in ("linear", "gaussian"), "Method must be 'linear' or 'gaussian'."
        assert len(boxes) == len(scores)

        # Mutable working copies
        b_list = list(boxes)
        s_list = list(scores)
        orig_indices = list(range(len(boxes)))

        n = len(boxes)
        for i in range(n):
            # Find max score from i to n-1
            max_idx = i
            max_score = s_list[i]
            for pos in range(i + 1, n):
                if s_list[pos] > max_score:
                    max_score = s_list[pos]
                    max_idx = pos

            # Swap max to current position i
            b_list[i], b_list[max_idx] = b_list[max_idx], b_list[i]
            s_list[i], s_list[max_idx] = s_list[max_idx], s_list[i]
            orig_indices[i], orig_indices[max_idx] = orig_indices[max_idx], orig_indices[i]

            current_box = b_list[i]

            # Decay scores of subsequent elements
            for pos in range(i + 1, n):
                iou = NonMaximumSuppression.box_iou(current_box, b_list[pos])
                if method == "linear":
                    if iou >= iou_threshold:
                        weight = 1.0 - iou
                    else:
                        weight = 1.0
                else:  # gaussian
                    weight = math.exp(-(iou * iou) / max(1e-7, sigma))

                s_list[pos] = s_list[pos] * weight

        # Gather results above score threshold
        results = []
        for i in range(n):
            if s_list[i] >= score_threshold:
                results.append((orig_indices[i], s_list[i]))

        return results
