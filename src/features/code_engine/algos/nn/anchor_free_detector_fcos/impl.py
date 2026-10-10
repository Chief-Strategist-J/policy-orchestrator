from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoAnchorFreeDetectorFCOS:
    """
    ---
    contract:
      algo_id: ALGO-NN-89
      name: NnAlgoAnchorFreeDetectorFCOS
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.object_detection
        - nn.anchor_free
        - nn.centerness
        - nn.fcos
      inputs:
        type: object
        required:
          - cls_logits
          - reg_preds
          - centerness_logits
        properties:
          cls_logits:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Per-pixel classification logits of shape (C, H, W).
          reg_preds:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Per-pixel regression distance targets (l, t, r, b) of shape (4, H, W).
          centerness_logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: Per-pixel centerness logits of shape (H, W).
          stride:
            type: number
            default: 8.0
            description: Feature stride relative to input image.
          score_threshold:
            type: number
            default: 0.05
            description: Minimum composite score cutoff.
      outputs:
        type: object
        required:
          - detections
        properties:
          detections:
            type: array
            items:
              type: object
            description: List of detected candidate boxes with box coordinates, class_id, centerness, and combined score.
      parameters: {}
      input_assumptions:
        - cls_logits has shape [C, H, W]
        - reg_preds has shape [4, H, W]
        - centerness_logits has shape [H, W]
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Bounded by exponential and sigmoid evaluation precision"
      uses_model: false
      complexity:
        variables:
          C: classes
          H: height
          W: width
        time_worst: "O(H * W * C)"
        time_typical: "O(H * W * C)"
        space: "O(H * W * C)"
      preconditions:
        - len(input.cls_logits) > 0 and len(input.cls_logits[0]) > 0 and len(input.cls_logits[0][0]) > 0
        - len(input.reg_preds) == 4
      postconditions:
        - all(d["score"] >= input.score_threshold for d in output.detections)
      certificate: "l = x - x_0, t = y - y_0, r = x_1 - x, b = y_1 - y, centerness = sqrt(min(l,r)/max(l,r) * min(t,b)/max(t,b))"
      compatible_adapters:
        - ADAPTER-FCOS-HEAD
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-80
        - ALGO-NN-85
        - ALGO-NN-86
      references:
        - "https://doi.org/10.1109/ICCV.2019.00972"
        - "https://arxiv.org/abs/1904.01355"
    ---
    """

    @staticmethod
    def compute_centerness(l: float, t: float, r: float, b: float) -> float:
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
        score_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        if not cls_logits or len(cls_logits) == 0 or len(cls_logits[0]) == 0:
            raise ValueError("Precondition failed: cls_logits must be non-empty 3D tensor")
        if len(reg_preds) != 4:
            raise ValueError("Precondition failed: reg_preds must have 4 channels (l, t, r, b)")

        c_classes = len(cls_logits)
        h = len(cls_logits[0])
        w = len(cls_logits[0][0])

        detections = []
        for i in range(h):
            py = (float(i) + 0.5) * stride
            for j in range(w):
                px = (float(j) + 0.5) * stride

                cnt_logit = centerness_logits[i][j]
                cnt_score = 1.0 / (1.0 + math.exp(-cnt_logit)) if cnt_logit >= 0 else math.exp(cnt_logit) / (1.0 + math.exp(cnt_logit))

                l = math.exp(reg_preds[0][i][j]) * stride
                t = math.exp(reg_preds[1][i][j]) * stride
                r = math.exp(reg_preds[2][i][j]) * stride
                b = math.exp(reg_preds[3][i][j]) * stride

                x1 = px - l
                y1 = py - t
                x2 = px + r
                y2 = py + b

                for c in range(c_classes):
                    logit = cls_logits[c][i][j]
                    p_cls = 1.0 / (1.0 + math.exp(-logit)) if logit >= 0 else math.exp(logit) / (1.0 + math.exp(logit))
                    final_score = math.sqrt(p_cls * cnt_score)

                    if final_score >= score_threshold:
                        detections.append({
                            "box": (x1, y1, x2, y2),
                            "score": final_score,
                            "class_id": c,
                            "centerness": cnt_score,
                            "cls_prob": p_cls,
                        })

        return {"detections": detections}

    @staticmethod
    def assign_fpn_level(
        l: float,
        t: float,
        r: float,
        b: float,
        level_limits: Tuple[float, float],
    ) -> bool:
        max_dist = max(l, t, r, b)
        m_min, m_max = level_limits
        return m_min <= max_dist <= m_max
