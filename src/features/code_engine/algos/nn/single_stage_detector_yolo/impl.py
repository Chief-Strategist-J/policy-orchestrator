"""Single-Stage Object Detector Head (YOLO/SSD/RetinaNet) Grid Decoding and Loss Mechanics.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: single_stage_detector_yolo
  category: neural_network_architecture
  subcategory: object_detection
  id: ALGO-NN-85
  equation: |
    b_x = \\sigma(t_x) + c_x, \\quad b_y = \\sigma(t_y) + c_y
    b_w = p_w \\exp(t_w), \\quad b_h = p_h \\exp(t_h)
    \\text{confidence}_c = \\sigma(t_{\\text{obj}}) \\cdot \\sigma(t_{\\text{cls}, c})
  domain:
    grid_cells: "S x S spatial locations (c_x, c_y)"
    anchors_per_cell: "B prior anchor dimensions (p_w, p_h)"
    class_probabilities: "C semantic categories"
  properties:
    dense_single_pass_prediction: true
    bounded_grid_offset_sigmoid: true
    anchor_modulated_wh: true
    end_to_end_parallelizable: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class SingleStageDetectorYOLO:
    """Single-stage dense detection head decoder, coordinate transformation, and class score evaluator."""

    @staticmethod
    def sigmoid(x: float) -> float:
        """Numerically stable scalar sigmoid function."""
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
        conf_threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """Decode raw dense output tensor into calibrated bounding boxes and class scores.

        Args:
            raw_predictions: Tensor of shape [S_y, S_x, B, 5 + num_classes] where channels are:
                             (tx, ty, tw, th, tobj, tcls_1, ..., tcls_C).
            anchor_priors: List of B anchor (width, height) priors in feature/stride scale.
            stride: Downsampling factor of this grid level.
            num_classes: Number of object categories.
            conf_threshold: Minimum class-confidence score to retain box.

        Returns:
            List of detected box records: [{"box": (x1, y1, x2, y2), "score": s, "class_id": c, "obj_conf": obj}]
        """
        sy = len(raw_predictions)
        sx = len(raw_predictions[0])
        num_anchors = len(anchor_priors)
        assert len(raw_predictions[0][0]) == num_anchors, "Anchor count mismatch."

        detections = []

        for cy in range(sy):
            for cx in range(sx):
                for b in range(num_anchors):
                    vec = raw_predictions[cy][cx][b]
                    tx, ty, tw, th, tobj = vec[0], vec[1], vec[2], vec[3], vec[4]
                    pw, ph = anchor_priors[b]

                    # 1. Coordinate decoding with bounded sigmoid cell offsets
                    bx = (SingleStageDetectorYOLO.sigmoid(tx) + float(cx)) * stride
                    by = (SingleStageDetectorYOLO.sigmoid(ty) + float(cy)) * stride
                    bw = pw * math.exp(min(th, 10.0)) * stride
                    bh = ph * math.exp(min(tw, 10.0)) * stride

                    x1 = bx - 0.5 * bw
                    y1 = by - 0.5 * bh
                    x2 = bx + 0.5 * bw
                    y2 = by + 0.5 * bh

                    obj_conf = SingleStageDetectorYOLO.sigmoid(tobj)

                    # 2. Multi-class score evaluation
                    class_logits = vec[5:5 + num_classes]
                    for cls_id in range(num_classes):
                        cls_prob = SingleStageDetectorYOLO.sigmoid(class_logits[cls_id])
                        final_score = obj_conf * cls_prob

                        if final_score >= conf_threshold:
                            detections.append({
                                "box": (x1, y1, x2, y2),
                                "score": final_score,
                                "class_id": cls_id,
                                "objectness": obj_conf
                            })

        return detections

    @staticmethod
    def compute_ciou(
        box1: Tuple[float, float, float, float],
        box2: Tuple[float, float, float, float]
    ) -> float:
        """Compute Complete IoU (CIoU) taking into account overlap, center distance, and aspect ratio.

        Args:
            box1: (x1, y1, x2, y2)
            box2: (x1, y1, x2, y2)

        Returns:
            CIoU metric in [-1.0, 1.0].
        """
        # Intersections
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        w1, h1 = max(0.0, box1[2] - box1[0]), max(0.0, box1[3] - box1[1])
        w2, h2 = max(0.0, box2[2] - box2[0]), max(0.0, box2[3] - box2[1])
        union_area = w1 * h1 + w2 * h2 - inter_area
        iou = inter_area / union_area if union_area > 0.0 else 0.0

        # Center distance
        cx1, cy1 = box1[0] + 0.5 * w1, box1[1] + 0.5 * h1
        cx2, cy2 = box2[0] + 0.5 * w2, box2[1] + 0.5 * h2
        rho2 = (cx1 - cx2) ** 2 + (cy1 - cy2) ** 2

        # Smallest enclosing box
        enc_x1 = min(box1[0], box2[0])
        enc_y1 = min(box1[1], box2[1])
        enc_x2 = max(box1[2], box2[2])
        enc_y2 = max(box1[3], box2[3])
        c2 = (enc_x2 - enc_x1) ** 2 + (enc_y2 - enc_y1) ** 2

        # Aspect ratio consistency term v and alpha
        if h1 > 0.0 and h2 > 0.0:
            atan_diff = math.atan(w2 / max(1e-6, h2)) - math.atan(w1 / max(1e-6, h1))
            v = (4.0 / (math.pi ** 2)) * (atan_diff ** 2)
        else:
            v = 0.0

        alpha = v / ((1.0 - iou) + v) if (1.0 - iou + v) > 0.0 else 0.0

        ciou = iou - (rho2 / max(1e-7, c2)) - alpha * v
        return ciou
