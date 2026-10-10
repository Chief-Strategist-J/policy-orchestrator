"""Region Proposal Networks (RPN) and Two-Stage Object Detection.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: rpn_faster_rcnn
  category: neural_network_architecture
  subcategory: object_detection
  id: ALGO-NN-84
  equation: |
    t_x = (x - x_a)/w_a, \\quad t_y = (y - y_a)/h_a
    t_w = \\log(w / w_a), \\quad t_h = \\log(h / h_a)
    p_{\\text{obj}} = \\sigma(\\text{logit}_{\\text{fg}} - \\text{logit}_{\\text{bg}})
    \\mathcal{L}_{\\text{RPN}} = \\frac{1}{N_{\\text{cls}}} \\sum_i \\mathcal{L}_{\\text{cls}}(p_i, p_i^*) + \\lambda \\frac{1}{N_{\\text{reg}}} \\sum_i p_i^* \\text{SmoothL}_1(t_i - t_i^*)
  domain:
    spatial_grid: "H x W feature map cells"
    anchors_per_cell: "K = |scales| x |aspect_ratios|"
    iou_thresholds: "\\text{IoU}_{\\text{pos}} \\ge 0.7, \\text{IoU}_{\\text{neg}} < 0.3"
  properties:
    translation_invariant_anchors: true
    multi_scale_proposals: true
    smooth_l1_regression: true
    two_stage_decoupling: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class RegionProposalNetwork:
    """Region Proposal Network (RPN) generator, anchor decoder, and IoU matcher."""

    @staticmethod
    def generate_base_anchors(
        base_size: float = 16.0,
        ratios: Tuple[float, ...] = (0.5, 1.0, 2.0),
        scales: Tuple[float, ...] = (8.0, 16.0, 32.0)
    ) -> List[Tuple[float, float, float, float]]:
        """Generate canonical base anchor boxes centered at (0, 0) in [xmin, ymin, xmax, ymax] format.

        Args:
            base_size: Reference anchor side length.
            ratios: Aspect ratios (h/w or w/h).
            scales: Multiplicative scale factors relative to base_size.

        Returns:
            List of K anchor boxes (xmin, ymin, xmax, ymax).
        """
        anchors = []
        for scale in scales:
            area = (base_size * scale) ** 2
            for ratio in ratios:
                # w * h = area, h / w = ratio => w = sqrt(area / ratio), h = w * ratio
                w = math.sqrt(area / ratio)
                h = w * ratio
                x_ctr = 0.0
                y_ctr = 0.0
                xmin = x_ctr - 0.5 * (w - 1.0)
                ymin = y_ctr - 0.5 * (h - 1.0)
                xmax = x_ctr + 0.5 * (w - 1.0)
                ymax = y_ctr + 0.5 * (h - 1.0)
                anchors.append((xmin, ymin, xmax, ymax))
        return anchors

    @staticmethod
    def grid_anchors(
        base_anchors: List[Tuple[float, float, float, float]],
        grid_h: int,
        grid_w: int,
        stride: float = 16.0
    ) -> List[List[List[Tuple[float, float, float, float]]]]:
        """Project base anchors across all spatial grid locations [grid_h, grid_w].

        Args:
            base_anchors: List of K canonical anchors.
            grid_h: Feature map height.
            grid_w: Feature map width.
            stride: Spatial stride of the feature map relative to input.

        Returns:
            3D list [grid_h][grid_w][k] of shifted anchor boxes [xmin, ymin, xmax, ymax].
        """
        all_anchors = []
        for i in range(grid_h):
            row_anchors = []
            shift_y = float(i) * stride
            for j in range(grid_w):
                shift_x = float(j) * stride
                cell_anchors = []
                for (x1, y1, x2, y2) in base_anchors:
                    cell_anchors.append((x1 + shift_x, y1 + shift_y, x2 + shift_x, y2 + shift_y))
                row_anchors.append(cell_anchors)
            all_anchors.append(row_anchors)
        return all_anchors

    @staticmethod
    def box_iou(
        box_a: Tuple[float, float, float, float],
        box_b: Tuple[float, float, float, float]
    ) -> float:
        """Compute Intersection-over-Union (IoU) between two bounding boxes in [x1, y1, x2, y2] format.

        Args:
            box_a: (x1, y1, x2, y2)
            box_b: (x1, y1, x2, y2)

        Returns:
            IoU overlap ratio in [0.0, 1.0].
        """
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])

        inter_w = max(0.0, x2 - x1 + 1.0)
        inter_h = max(0.0, y2 - y1 + 1.0)
        inter_area = inter_w * inter_h

        area_a = max(0.0, box_a[2] - box_a[0] + 1.0) * max(0.0, box_a[3] - box_a[1] + 1.0)
        area_b = max(0.0, box_b[2] - box_b[0] + 1.0) * max(0.0, box_b[3] - box_b[1] + 1.0)

        union_area = area_a + area_b - inter_area
        return inter_area / union_area if union_area > 0.0 else 0.0

    @staticmethod
    def decode_proposals(
        anchors: List[Tuple[float, float, float, float]],
        deltas: List[Tuple[float, float, float, float]],
        clip_bounds: Optional[Tuple[float, float]] = None
    ) -> List[Tuple[float, float, float, float]]:
        """Decode predicted parameterized offsets (dx, dy, dw, dh) into bounding boxes [x1, y1, x2, y2].

        Args:
            anchors: List of anchor boxes [x1, y1, x2, y2].
            deltas: Predicted deltas (dx, dy, dw, dh).
            clip_bounds: Optional (img_height, img_width) for boundary clipping.

        Returns:
            List of decoded candidate boxes [x1, y1, x2, y2].
        """
        assert len(anchors) == len(deltas), "Anchors and deltas counts must match."
        decoded = []

        for (ax1, ay1, ax2, ay2), (dx, dy, dw, dh) in zip(anchors, deltas):
            wa = ax2 - ax1 + 1.0
            ha = ay2 - ay1 + 1.0
            ctr_xa = ax1 + 0.5 * wa
            ctr_ya = ay1 + 0.5 * ha

            # Bounding box delta inversion
            pred_ctr_x = dx * wa + ctr_xa
            pred_ctr_y = dy * ha + ctr_ya
            pred_w = wa * math.exp(min(dh, 10.0))  # clamp to avoid exp explosion
            pred_h = ha * math.exp(min(dw, 10.0))

            pred_x1 = pred_ctr_x - 0.5 * pred_w
            pred_y1 = pred_ctr_y - 0.5 * pred_h
            pred_x2 = pred_ctr_x + 0.5 * pred_w
            pred_y2 = pred_ctr_y + 0.5 * pred_h

            if clip_bounds is not None:
                max_h, max_w = clip_bounds
                pred_x1 = max(0.0, min(pred_x1, max_w - 1.0))
                pred_y1 = max(0.0, min(pred_y1, max_h - 1.0))
                pred_x2 = max(0.0, min(pred_x2, max_w - 1.0))
                pred_y2 = max(0.0, min(pred_y2, max_h - 1.0))

            decoded.append((pred_x1, pred_y1, pred_x2, pred_y2))

        return decoded

    @staticmethod
    def smooth_l1_loss(pred: float, target: float, beta: float = 1.0) -> float:
        """Smooth L1 Loss (Huber loss) with transition threshold beta."""
        diff = abs(pred - target)
        if diff < beta:
            return 0.5 * (diff ** 2) / beta
        return diff - 0.5 * beta
