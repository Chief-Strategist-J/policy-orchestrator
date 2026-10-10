from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoSingleStageDetectorYolo:
    """
    ---
    contract:
      algo_id: ALGO-NN-85
      name: NnAlgoSingleStageDetectorYolo
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.object_detection
        - nn.single_stage
        - nn.dense_grid
        - nn.real_time
      inputs:
        type: object
        required:
          - raw_predictions
          - anchor_priors
        properties:
          raw_predictions:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: 4D Tensor of shape (S_y, S_x, B, 5 + C) containing (tx, ty, tw, th, tobj, tcls_1..C).
          anchor_priors:
            type: array
            items:
              type: array
              items:
                type: number
            description: List of B anchor (width, height) priors.
          stride:
            type: number
            default: 32.0
            description: Feature stride relative to input image.
          num_classes:
            type: integer
            default: 80
            description: Number of object categories C.
          conf_threshold:
            type: number
            default: 0.25
            description: Minimum confidence cutoff.
      outputs:
        type: object
        required:
          - detections
        properties:
          detections:
            type: array
            items:
              type: object
            description: List of decoded detections with box coordinates, class_id, objectness, and combined score.
      parameters: {}
      input_assumptions:
        - raw_predictions has shape [S_y, S_x, B, 5 + num_classes]
        - anchor_priors has length B
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Bounded by sigmoid and exponential floating-point evaluation"
      uses_model: false
      complexity:
        variables:
          S_y: grid height
          S_x: grid width
          B: anchors per cell
          C: number of classes
        time_worst: "O(S_y * S_x * B * C)"
        time_typical: "O(S_y * S_x * B * C)"
        space: "O(S_y * S_x * B * C)"
      preconditions:
        - len(input.raw_predictions) > 0 and len(input.raw_predictions[0]) > 0
        - len(input.anchor_priors) == len(input.raw_predictions[0][0])
      postconditions:
        - all(d["score"] >= input.conf_threshold for d in output.detections)
      certificate: "b_x = (sigma(t_x) + c_x) * s, b_y = (sigma(t_y) + c_y) * s, score = sigma(t_obj) * sigma(t_cls)"
      compatible_adapters:
        - ADAPTER-YOLO-HEAD
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-80
        - ALGO-NN-84
        - ALGO-NN-86
        - ALGO-NN-89
      references:
        - "https://doi.org/10.1109/CVPR.2016.91"
        - "https://arxiv.org/abs/1506.02640"
    ---
    """

    @staticmethod
    def sigmoid(x: float) -> float:
        if x >= 0:
            z = math.exp(-x)
            return 1.0 / (1.0 + z)
        else:
            z = math.exp(x)
            return z / (1.0 + z)

    @staticmethod
    def decode_yolo_grid(
        raw_predictions: List[List[List[List[float]]]],
        anchor_priors: List[Tuple[float, float]],
        stride: float = 32.0,
        num_classes: int = 80,
        conf_threshold: float = 0.25,
    ) -> Dict[str, Any]:
        if not raw_predictions or len(raw_predictions) == 0 or len(raw_predictions[0]) == 0:
            raise ValueError("Precondition failed: raw_predictions must be non-empty 4D tensor")
        sy = len(raw_predictions)
        sx = len(raw_predictions[0])
        num_anchors = len(anchor_priors)
        if len(raw_predictions[0][0]) != num_anchors:
            raise ValueError("Precondition failed: anchor_priors length must match tensor dimension 2")

        detections = []
        for cy in range(sy):
            for cx in range(sx):
                for b in range(num_anchors):
                    vec = raw_predictions[cy][cx][b]
                    tx, ty, tw, th, tobj = vec[0], vec[1], vec[2], vec[3], vec[4]
                    pw, ph = anchor_priors[b]

                    bx = (NnAlgoSingleStageDetectorYolo.sigmoid(tx) + float(cx)) * stride
                    by = (NnAlgoSingleStageDetectorYolo.sigmoid(ty) + float(cy)) * stride
                    bw = pw * math.exp(min(th, 10.0)) * stride
                    bh = ph * math.exp(min(tw, 10.0)) * stride

                    x1 = bx - 0.5 * bw
                    y1 = by - 0.5 * bh
                    x2 = bx + 0.5 * bw
                    y2 = by + 0.5 * bh

                    obj_conf = NnAlgoSingleStageDetectorYolo.sigmoid(tobj)
                    class_logits = vec[5:5 + num_classes]

                    for cls_id in range(min(num_classes, len(class_logits))):
                        cls_prob = NnAlgoSingleStageDetectorYolo.sigmoid(class_logits[cls_id])
                        final_score = obj_conf * cls_prob

                        if final_score >= conf_threshold:
                            detections.append({
                                "box": (x1, y1, x2, y2),
                                "score": final_score,
                                "class_id": cls_id,
                                "objectness": obj_conf,
                            })

        return {"detections": detections}

    @staticmethod
    def compute_ciou(
        box1: Tuple[float, float, float, float],
        box2: Tuple[float, float, float, float],
    ) -> float:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        w1, h1 = max(0.0, box1[2] - box1[0]), max(0.0, box1[3] - box1[1])
        w2, h2 = max(0.0, box2[2] - box2[0]), max(0.0, box2[3] - box2[1])
        union_area = w1 * h1 + w2 * h2 - inter_area
        iou = inter_area / union_area if union_area > 0.0 else 0.0

        cx1, cy1 = box1[0] + 0.5 * w1, box1[1] + 0.5 * h1
        cx2, cy2 = box2[0] + 0.5 * w2, box2[1] + 0.5 * h2
        rho2 = (cx1 - cx2) ** 2 + (cy1 - cy2) ** 2

        enc_x1 = min(box1[0], box2[0])
        enc_y1 = min(box1[1], box2[1])
        enc_x2 = max(box1[2], box2[2])
        enc_y2 = max(box1[3], box2[3])
        c2 = (enc_x2 - enc_x1) ** 2 + (enc_y2 - enc_y1) ** 2

        if h1 > 0.0 and h2 > 0.0:
            atan_diff = math.atan(w2 / max(1e-6, h2)) - math.atan(w1 / max(1e-6, h1))
            v = (4.0 / (math.pi ** 2)) * (atan_diff ** 2)
        else:
            v = 0.0

        alpha = v / ((1.0 - iou) + v) if (1.0 - iou + v) > 0.0 else 0.0
        ciou = iou - (rho2 / max(1e-7, c2)) - alpha * v
        return ciou
