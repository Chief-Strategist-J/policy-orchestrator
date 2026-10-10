from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoRoIAlignMaskRCNN:
    """
    ---
    contract:
      algo_id: ALGO-NN-88
      name: NnAlgoRoIAlignMaskRCNN
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.object_detection
        - nn.instance_segmentation
        - nn.roi_align
        - nn.bilinear_sampling
      inputs:
        type: object
        required:
          - features
          - roi
        properties:
          features:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Input 3D feature map tensor of shape (C, H, W).
          roi:
            type: array
            items:
              type: number
            description: Region of interest coordinates (x1, y1, x2, y2) in input image scale.
          spatial_scale:
            type: number
            default: 0.0625
            description: Feature stride scaling factor (e.g. 1/16).
          pooled_height:
            type: integer
            default: 7
            description: Output pooled bin height.
          pooled_width:
            type: integer
            default: 7
            description: Output pooled bin width.
          sampling_ratio:
            type: integer
            default: 2
            description: Number of regular sub-pixel sampling points per bin axis.
      outputs:
        type: object
        required:
          - pooled_features
        properties:
          pooled_features:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Exact non-quantized aligned feature tensor of shape (C, pooled_height, pooled_width).
      parameters: {}
      input_assumptions:
        - features has shape [C, H, W]
        - roi has 4 continuous coordinates [x1, y1, x2, y2]
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact bilinear continuous interpolation without spatial rounding"
      uses_model: false
      complexity:
        variables:
          C: channels
          k_h: pooled height
          k_w: pooled width
          N_s: sampling points per bin (typically 4)
        time_worst: "O(C * k_h * k_w * N_s)"
        time_typical: "O(C * k_h * k_w * N_s)"
        space: "O(C * k_h * k_w)"
      preconditions:
        - len(input.features) > 0 and len(input.features[0]) > 0
        - len(input.roi) == 4
        - input.pooled_height >= 1 and input.pooled_width >= 1
      postconditions:
        - len(output.pooled_features) == len(input.features)
        - len(output.pooled_features[0]) == input.pooled_height
        - len(output.pooled_features[0][0]) == input.pooled_width
      certificate: "Exact continuous bilinear pooling: y(i, j) = 1/N_s * sum_s BilinearSample(F, p_y^{(s)}, p_x^{(s)})"
      compatible_adapters:
        - ADAPTER-ROIALIGN
        - ADAPTER-MASK-RCNN
      related_algos:
        - ALGO-NN-82
        - ALGO-NN-84
        - ALGO-NN-86
      references:
        - "https://doi.org/10.1109/ICCV.2017.322"
        - "https://arxiv.org/abs/1703.06870"
    ---
    """

    @staticmethod
    def bilinear_sample_2d(
        feat_map: List[List[float]],
        py: float,
        px: float,
    ) -> float:
        h = len(feat_map)
        w = len(feat_map[0])

        if py < -1.0 or py > h or px < -1.0 or px > w:
            return 0.0

        y_low = int(math.floor(py))
        y_high = y_low + 1
        x_low = int(math.floor(px))
        x_high = x_low + 1

        ly = py - y_low
        lx = px - x_low
        hy = 1.0 - ly
        hx = 1.0 - lx

        v1 = feat_map[y_low][x_low] if (0 <= y_low < h and 0 <= x_low < w) else 0.0
        v2 = feat_map[y_low][x_high] if (0 <= y_low < h and 0 <= x_high < w) else 0.0
        v3 = feat_map[y_high][x_low] if (0 <= y_high < h and 0 <= x_low < w) else 0.0
        v4 = feat_map[y_high][x_high] if (0 <= y_high < h and 0 <= x_high < w) else 0.0

        return hy * hx * v1 + hy * lx * v2 + ly * hx * v3 + ly * lx * v4

    @staticmethod
    def roi_align(
        features: List[List[List[float]]],
        roi: Tuple[float, float, float, float],
        spatial_scale: float = 1.0 / 16.0,
        pooled_height: int = 7,
        pooled_width: int = 7,
        sampling_ratio: int = 2,
    ) -> Dict[str, Any]:
        if not features or len(features) == 0:
            raise ValueError("Precondition failed: features must be non-empty 3D tensor")
        if len(roi) != 4:
            raise ValueError("Precondition failed: roi must be 4 coordinates (x1, y1, x2, y2)")

        c = len(features)
        x1_img, y1_img, x2_img, y2_img = roi

        roi_start_w = x1_img * spatial_scale
        roi_start_h = y1_img * spatial_scale
        roi_end_w = x2_img * spatial_scale
        roi_end_h = y2_img * spatial_scale

        roi_width = max(roi_end_w - roi_start_w, 1.0)
        roi_height = max(roi_end_h - roi_start_h, 1.0)

        bin_size_h = roi_height / float(pooled_height)
        bin_size_w = roi_width / float(pooled_width)

        pooled = [[[0.0 for _ in range(pooled_width)] for _ in range(pooled_height)] for _ in range(c)]

        sample_h_count = sampling_ratio if sampling_ratio > 0 else max(1, int(math.ceil(roi_height / pooled_height)))
        sample_w_count = sampling_ratio if sampling_ratio > 0 else max(1, int(math.ceil(roi_width / pooled_width)))
        num_samples = float(sample_h_count * sample_w_count)

        for ch in range(c):
            f_channel = features[ch]
            for ph in range(pooled_height):
                for pw in range(pooled_width):
                    bin_y = roi_start_h + ph * bin_size_h
                    bin_x = roi_start_w + pw * bin_size_w

                    accum = 0.0
                    for sh in range(sample_h_count):
                        py = bin_y + (sh + 0.5) * (bin_size_h / sample_h_count)
                        for sw in range(sample_w_count):
                            px = bin_x + (sw + 0.5) * (bin_size_w / sample_w_count)
                            accum += NnAlgoRoIAlignMaskRCNN.bilinear_sample_2d(f_channel, py, px)

                    pooled[ch][ph][pw] = accum / num_samples

        return {"pooled_features": pooled}

    @staticmethod
    def mask_bce_loss(
        pred_mask_logits: List[List[float]],
        gt_binary_mask: List[List[float]],
        eps: float = 1e-7,
    ) -> float:
        m = len(pred_mask_logits)
        total_loss = 0.0

        for i in range(m):
            for j in range(m):
                logit = pred_mask_logits[i][j]
                if logit >= 0:
                    prob = 1.0 / (1.0 + math.exp(-logit))
                else:
                    prob = math.exp(logit) / (1.0 + math.exp(logit))

                prob = max(eps, min(1.0 - eps, prob))
                target = gt_binary_mask[i][j]
                bce = - (target * math.log(prob) + (1.0 - target) * math.log(1.0 - prob))
                total_loss += bce

        return total_loss / (m * m)
