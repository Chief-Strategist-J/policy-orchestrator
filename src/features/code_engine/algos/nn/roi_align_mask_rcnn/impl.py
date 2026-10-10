"""RoIAlign and Mask R-CNN Instance Segmentation Extraction.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: roi_align_mask_rcnn
  category: neural_network_architecture
  subcategory: object_detection
  id: ALGO-NN-88
  equation: |
    y(i, j) = \\frac{1}{N_{\\text{samples}}} \\sum_{s=1}^{N_{\\text{samples}}} \\text{BilinearSample}(F, p_y^{(s)}, p_x^{(s)})
    \\mathcal{L}_{\\text{mask}} = - \\frac{1}{m^2} \\sum_{1 \\le u, v \\le m} \\left[ y_{u,v} \\log \\hat{y}_{u,v} + (1 - y_{u,v}) \\log (1 - \\hat{y}_{u,v}) \\right]
  domain:
    spatial_sampling: "Continuous floating-point coordinates (py, px) \\in \\mathbb{R}^2"
    pooled_size: "k x k bins (e.g. 7x7 or 14x14)"
    samples_per_bin: "Typically 2x2 = 4 bilinear points"
  properties:
    exact_spatial_alignment: true
    no_coordinate_quantization: true
    bilinear_continuous_interpolation: true
    decoupled_binary_mask_branch: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class RoIAlignMaskRCNN:
    """RoIAlign (Region of Interest Align) and Mask R-CNN head feature pooling engine."""

    @staticmethod
    def bilinear_sample_2d(
        feat_map: List[List[float]],
        py: float,
        px: float
    ) -> float:
        """Sample 2D feature map at fractional coordinates (py, px) without coordinate quantization.

        Args:
            feat_map: 2D matrix [H, W].
            py: Floating-point y-coordinate.
            px: Floating-point x-coordinate.

        Returns:
            Bilinearly interpolated value.
        """
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
        sampling_ratio: int = 2
    ) -> List[List[List[float]]]:
        """Perform exact RoIAlign without spatial quantization.

        Args:
            features: 3D tensor [C, H, W].
            roi: Region of interest (x1, y1, x2, y2) in image coordinates.
            spatial_scale: Feature map scale relative to image (e.g. 1/16).
            pooled_height: Output grid height k_h.
            pooled_width: Output grid width k_w.
            sampling_ratio: Number of sampling points along each bin axis (default 2 -> 4 points).

        Returns:
            Pooled feature tensor of shape [C, pooled_height, pooled_width].
        """
        c = len(features)
        x1_img, y1_img, x2_img, y2_img = roi

        # Map RoI to feature map continuous coordinates
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
                            accum += RoIAlignMaskRCNN.bilinear_sample_2d(f_channel, py, px)

                    pooled[ch][ph][pw] = accum / num_samples

        return pooled

    @staticmethod
    def mask_bce_loss(
        pred_mask_logits: List[List[float]],
        gt_binary_mask: List[List[float]],
        eps: float = 1e-7
    ) -> float:
        """Compute per-pixel Binary Cross-Entropy loss for predicted mask logits.

        Args:
            pred_mask_logits: Matrix of shape [M, M] raw logits.
            gt_binary_mask: Matrix of shape [M, M] with entries in {0, 1}.
            eps: Numerical stability constant.

        Returns:
            Average binary cross entropy across all M x M pixels.
        """
        m = len(pred_mask_logits)
        total_loss = 0.0

        for i in range(m):
            for j in range(m):
                logit = pred_mask_logits[i][j]
                # Stable sigmoid
                if logit >= 0:
                    prob = 1.0 / (1.0 + math.exp(-logit))
                else:
                    prob = math.exp(logit) / (1.0 + math.exp(logit))

                prob = max(eps, min(1.0 - eps, prob))
                target = gt_binary_mask[i][j]
                bce = - (target * math.log(prob) + (1.0 - target) * math.log(1.0 - prob))
                total_loss += bce

        return total_loss / (m * m)
