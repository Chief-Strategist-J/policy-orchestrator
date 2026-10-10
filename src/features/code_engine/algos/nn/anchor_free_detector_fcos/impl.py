"""Fully Convolutional One-Stage (FCOS) Anchor-Free Object Detection.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: anchor_free_detector_fcos
  category: neural_network_architecture
  subcategory: object_detection
  id: ALGO-NN-89
  equation: |
    l = x - x_0^{(i)}, \\quad t = y - y_0^{(i)}, \\quad r = x_1^{(i)} - x, \\quad b = y_1^{(i)} - y
    \\text{centerness}^* = \\sqrt{\\frac{\\min(l^*, r^*)}{\\max(l^*, r^*)} \\times \\frac{\\min(t^*, b^*)}{\\max(t^*, b^*)}}
    \\text{FinalScore} = \\sqrt{p_{\\text{cls}} \\cdot \\text{centerness}}
  domain:
    spatial_locations: "Per-pixel continuous points (x, y) \\in \\mathbb{R}^2"
    regression_targets: "Distances to 4 box borders: l, t, r, b \\ge 0"
    centerness_range: "[0, 1]"
  properties:
    anchor_free: true
    proposal_free: true
    centerness_downweighting: true
    multi_level_fpn_scale_partitioning: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class AnchorFreeDetectorFCOS:
    """FCOS (Fully Convolutional One-Stage) Anchor-Free Detector and Centerness Engine."""

    @staticmethod
    def compute_centerness(l: float, t: float, r: float, b: float) -> float:
        """Compute ground-truth or predicted centerness score in [0.0, 1.0].

        Args:
            l: Distance to left boundary (> 0).
            t: Distance to top boundary (> 0).
            r: Distance to right boundary (> 0).
            b: Distance to bottom boundary (> 0).

        Returns:
            Centerness scalar in [0.0, 1.0].
        """
        if l <= 0.0 or t <= 0.0 or r <= 0.0 or b <= 0.0:
            return 0.0

        horiz = min(l, r) / max(l, r)
        vert = min(t, b) / max(t, b)
        return math.sqrt(horiz * vert)

    @staticmethod
    def decode_fcos_features(
        cls_logits: List[List[List[float]]],
        reg_preds: List[List[List[float]]],
        centerness_logits: List[List[float]],
        stride: float = 8.0,
        score_threshold: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Decode FCOS feature head outputs into calibrated bounding boxes.

        Args:
            cls_logits: [C, H, W] class classification logits.
            reg_preds: [4, H, W] regression targets [l, t, r, b] in feature/stride scale.
            centerness_logits: [H, W] centerness logits.
            stride: Spatial stride of feature map relative to original image.
            score_threshold: Minimum detection score threshold.

        Returns:
            List of detected candidate dictionaries:
            [{"box": (x1, y1, x2, y2), "score": s, "class_id": c, "centerness": cnt}]
        """
        c_classes = len(cls_logits)
        h = len(cls_logits[0])
        w = len(cls_logits[0][0])
        assert len(reg_preds) == 4

        detections = []

        for i in range(h):
            # Center of pixel in image coordinate space
            py = (float(i) + 0.5) * stride
            for j in range(w):
                px = (float(j) + 0.5) * stride

                # 1. Centerness decoding
                cnt_logit = centerness_logits[i][j]
                cnt_score = 1.0 / (1.0 + math.exp(-cnt_logit)) if cnt_logit >= 0 else math.exp(cnt_logit) / (1.0 + math.exp(cnt_logit))

                # 2. Box regression distance decoding (exponential or relu scaled)
                l = math.exp(reg_preds[0][i][j]) * stride
                t = math.exp(reg_preds[1][i][j]) * stride
                r = math.exp(reg_preds[2][i][j]) * stride
                b = math.exp(reg_preds[3][i][j]) * stride

                x1 = px - l
                y1 = py - t
                x2 = px + r
                y2 = py + b

                # 3. Class probabilities and score combination
                for c in range(c_classes):
                    logit = cls_logits[c][i][j]
                    p_cls = 1.0 / (1.0 + math.exp(-logit)) if logit >= 0 else math.exp(logit) / (1.0 + math.exp(logit))

                    # Final score combines classification confidence with spatial centerness
                    final_score = math.sqrt(p_cls * cnt_score)

                    if final_score >= score_threshold:
                        detections.append({
                            "box": (x1, y1, x2, y2),
                            "score": final_score,
                            "class_id": c,
                            "centerness": cnt_score,
                            "cls_prob": p_cls
                        })

        return detections

    @staticmethod
    def assign_fpn_level(
        l: float,
        t: float,
        r: float,
        b: float,
        level_limits: Tuple[float, float]
    ) -> bool:
        """Determine whether a sample location belongs to an FPN pyramid level based on max regression distance."""
        max_dist = max(l, t, r, b)
        m_min, m_max = level_limits
        return m_min <= max_dist <= m_max
