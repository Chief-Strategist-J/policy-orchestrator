from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoRegionProposalNetwork:
    """
    ---
    contract:
      algo_id: ALGO-NN-84
      name: NnAlgoRegionProposalNetwork
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.object_detection
        - nn.two_stage
        - nn.region_proposals
        - nn.anchors
      inputs:
        type: object
        required:
          - anchors
          - deltas
        properties:
          anchors:
            type: array
            items:
              type: array
              items:
                type: number
            description: List of anchor boxes in (x1, y1, x2, y2) format.
          deltas:
            type: array
            items:
              type: array
              items:
                type: number
            description: Parameterized regression displacements (dx, dy, dw, dh).
          clip_bounds:
            type: array
            items:
              type: number
            description: Optional (height, width) canvas dimensions to clip decoded boxes.
      outputs:
        type: object
        required:
          - proposals
        properties:
          proposals:
            type: array
            items:
              type: array
              items:
                type: number
            description: Decoded candidate bounding boxes in (x1, y1, x2, y2) format.
      parameters: {}
      input_assumptions:
        - anchors and deltas have identical lengths N >= 1
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact parameter inversion"
      uses_model: false
      complexity:
        variables:
          N: number of candidate anchors
        time_worst: O(N)
        time_typical: O(N)
        space: O(N)
      preconditions:
        - len(input.anchors) > 0 and len(input.anchors) == len(input.deltas)
      postconditions:
        - len(output.proposals) == len(input.anchors)
      certificate: "x = x_a + dx * w_a, y = y_a + dy * h_a, w = w_a * exp(dw), h = h_a * exp(dh)"
      compatible_adapters:
        - ADAPTER-RPN-HEAD
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-80
        - ALGO-NN-86
        - ALGO-NN-88
      references:
        - "https://doi.org/10.1109/TPAMI.2016.2577031"
        - "https://arxiv.org/abs/1506.01497"
    ---
    """

    @staticmethod
    def generate_base_anchors(
        base_size: float = 16.0,
        ratios: Tuple[float, ...] = (0.5, 1.0, 2.0),
        scales: Tuple[float, ...] = (8.0, 16.0, 32.0),
    ) -> List[Tuple[float, float, float, float]]:
        anchors = []
        for scale in scales:
            area = (base_size * scale) ** 2
            for ratio in ratios:
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
        stride: float = 16.0,
    ) -> List[List[List[Tuple[float, float, float, float]]]]:
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
        box_b: Tuple[float, float, float, float],
    ) -> float:
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
        clip_bounds: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        if not anchors or len(anchors) != len(deltas):
            raise ValueError("Precondition failed: len(input.anchors) == len(input.deltas) > 0")

        decoded = []
        for (ax1, ay1, ax2, ay2), (dx, dy, dw, dh) in zip(anchors, deltas):
            wa = ax2 - ax1 + 1.0
            ha = ay2 - ay1 + 1.0
            ctr_xa = ax1 + 0.5 * wa
            ctr_ya = ay1 + 0.5 * ha

            pred_ctr_x = dx * wa + ctr_xa
            pred_ctr_y = dy * ha + ctr_ya
            pred_w = wa * math.exp(min(dh, 10.0))
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

        return {"proposals": decoded}

    @staticmethod
    def smooth_l1_loss(pred: float, target: float, beta: float = 1.0) -> float:
        diff = abs(pred - target)
        if diff < beta:
            return 0.5 * (diff ** 2) / beta
        return diff - 0.5 * beta
