"""Feature Pyramid Networks (FPN) for Multi-Scale Dense Visual Representation.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: feature_pyramid_networks
  category: neural_network_architecture
  subcategory: convolutional_networks
  id: ALGO-NN-80
  equation: |
    P_L = \\text{Conv}_{3 \\times 3}\\left( \\text{Conv}_{1 \\times 1}(C_L) \\right) \\quad \\text{for top level } L = \\max
    P_l = \\text{Conv}_{3 \\times 3}\\left( \\text{Conv}_{1 \\times 1}(C_l) + \\text{Upsample}_{2\\times}(M_{l+1}) \\right) \\quad \\text{for } l < L
    M_l = \\text{Conv}_{1 \\times 1}(C_l) + \\text{Upsample}_{2\\times}(M_{l+1})
  domain:
    spatial_dimensions: "H_l x W_l with H_{l+1} = ceil(H_l / 2), W_{l+1} = ceil(W_l / 2)"
    channel_dimensions: "C_l channels mapped to unified d dimensions"
  properties:
    multi_scale_representation: true
    semantic_pyramid: true
    top_down_fusion: true
    uniform_feature_dimension: true
"""

from typing import List, Dict, Tuple, Any, Optional
import math


class FeaturePyramidNetworks:
    """Feature Pyramid Networks (FPN) multi-scale feature extractor and fusion engine."""

    @staticmethod
    def conv1x1(
        x: List[List[List[float]]],
        weight: List[List[float]],
        bias: Optional[List[float]] = None
    ) -> List[List[List[float]]]:
        """Apply 1x1 lateral projection to align channel dimensions.

        Args:
            x: Input feature map of shape [C_in, H, W].
            weight: Projection matrix of shape [C_out, C_in].
            bias: Optional bias vector of shape [C_out].

        Returns:
            Projected feature map of shape [C_out, H, W].
        """
        assert len(x) > 0 and len(x[0]) > 0 and len(x[0][0]) > 0, "Input map x must be non-empty [C, H, W]."
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])
        assert len(weight) > 0 and len(weight[0]) == c_in, "Weight shape must be [C_out, C_in]."
        c_out = len(weight)
        if bias is not None:
            assert len(bias) == c_out, "Bias length must equal C_out."

        out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c_out)]
        for co in range(c_out):
            b_val = bias[co] if bias is not None else 0.0
            w_row = weight[co]
            for i in range(h):
                for j in range(w):
                    val = b_val
                    for ci in range(c_in):
                        val += w_row[ci] * x[ci][i][j]
                    out[co][i][j] = val
        return out

    @staticmethod
    def upsample2x_nearest(x: List[List[List[float]]]) -> List[List[List[float]]]:
        """Nearest neighbor 2x spatial upsampling.

        Args:
            x: Input feature map of shape [C, H, W].

        Returns:
            Upsampled feature map of shape [C, 2*H, 2*W].
        """
        assert len(x) > 0 and len(x[0]) > 0 and len(x[0][0]) > 0, "Input map must be [C, H, W]."
        c = len(x)
        h = len(x[0])
        w = len(x[0][0])
        out_h = 2 * h
        out_w = 2 * w
        out = [[[0.0 for _ in range(out_w)] for _ in range(out_h)] for _ in range(c)]

        for ch in range(c):
            for i in range(out_h):
                src_i = i // 2
                for j in range(out_w):
                    src_j = j // 2
                    out[ch][i][j] = x[ch][src_i][src_j]
        return out

    @staticmethod
    def add_elementwise(
        a: List[List[List[float]]],
        b: List[List[List[float]]]
    ) -> List[List[List[float]]]:
        """Elementwise addition of two identically shaped 3D feature maps [C, H, W].

        Args:
            a: Feature map 1 of shape [C, H, W].
            b: Feature map 2 of shape [C, H, W].

        Returns:
            Sum feature map of shape [C, H, W].
        """
        assert len(a) == len(b), "Channel count must match."
        c = len(a)
        assert c > 0, "Tensors must be non-empty."
        h = len(a[0])
        w = len(a[0][0])
        assert len(b[0]) == h and len(b[0][0]) == w, "Spatial dimensions must match."

        out = [[[a[ch][i][j] + b[ch][i][j] for j in range(w)] for i in range(h)] for ch in range(c)]
        return out

    @staticmethod
    def conv3x3_smooth(
        x: List[List[List[float]]],
        weight: Optional[List[List[List[List[float]]]]] = None,
        bias: Optional[List[float]] = None
    ) -> List[List[List[float]]]:
        """Apply 3x3 convolution with padding=1 to smooth aliasing effects of upsampling.

        Args:
            x: Input feature map [C_in, H, W].
            weight: Optional filter kernel [C_out, C_in, 3, 3]. If None, identity-like depthwise smooth is used.
            bias: Optional bias vector [C_out].

        Returns:
            Smoothed feature map [C_out, H, W].
        """
        assert len(x) > 0 and len(x[0]) > 0 and len(x[0][0]) > 0, "Input map must be [C, H, W]."
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])

        if weight is None:
            # Default average smoothing kernel per channel
            c_out = c_in
            out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c_out)]
            for ch in range(c_in):
                for i in range(h):
                    for j in range(w):
                        total = 0.0
                        count = 0
                        for di in (-1, 0, 1):
                            ni = i + di
                            if 0 <= ni < h:
                                for dj in (-1, 0, 1):
                                    nj = j + dj
                                    if 0 <= nj < w:
                                        total += x[ch][ni][nj]
                                        count += 1
                        out[ch][i][j] = total / count
            return out

        c_out = len(weight)
        assert len(weight[0]) == c_in and len(weight[0][0]) == 3 and len(weight[0][0][0]) == 3, "Kernel must be [C_out, C_in, 3, 3]."
        if bias is not None:
            assert len(bias) == c_out, "Bias length must match C_out."

        out = [[[0.0 for _ in range(w)] for _ in range(h)] for _ in range(c_out)]
        for co in range(c_out):
            b_val = bias[co] if bias is not None else 0.0
            for i in range(h):
                for j in range(w):
                    s = b_val
                    for ci in range(c_in):
                        w_ch = weight[co][ci]
                        for di in range(3):
                            ni = i + di - 1
                            if 0 <= ni < h:
                                for dj in range(3):
                                    nj = j + dj - 1
                                    if 0 <= nj < w:
                                        s += w_ch[di][dj] * x[ci][ni][nj]
                    out[co][i][j] = s
        return out

    @staticmethod
    def forward(
        bottom_up_features: Dict[str, List[List[List[float]]]],
        d_pyramid: int = 2,
        lateral_weights: Optional[Dict[str, List[List[float]]]] = None,
        smooth_weights: Optional[Dict[str, List[List[List[List[float]]]]]] = None
    ) -> Dict[str, List[List[List[float]]]]:
        """Construct multi-scale Feature Pyramid (P_levels) from bottom-up backbone features (C_levels).

        Args:
            bottom_up_features: Dict with keys e.g. {"C2": ..., "C3": ..., "C4": ..., "C5": ...}
                sorted by spatial resolution descending (C2 largest, C5 smallest).
            d_pyramid: Uniform channel depth across all pyramid levels P_l.
            lateral_weights: Optional custom 1x1 weights per level.
            smooth_weights: Optional custom 3x3 smooth weights per level.

        Returns:
            Dict of pyramid feature maps {"P2": ..., "P3": ..., "P4": ..., "P5": ...}.
        """
        assert len(bottom_up_features) >= 2, "FPN requires at least 2 backbone stages."
        level_keys = sorted(list(bottom_up_features.keys()), key=lambda k: int(k[1:]) if k[1:].isdigit() else k)
        max_level_key = level_keys[-1]
        top_idx = int(max_level_key[1:]) if max_level_key[1:].isdigit() else len(level_keys)

        # 1. Initialize top lateral map M_max
        c_top = bottom_up_features[max_level_key]
        c_in_top = len(c_top)
        if lateral_weights is not None and max_level_key in lateral_weights:
            lat_w = lateral_weights[max_level_key]
        else:
            lat_w = [[1.0 / c_in_top for _ in range(c_in_top)] for _ in range(d_pyramid)]

        m_maps: Dict[str, List[List[List[float]]]] = {}
        m_maps[max_level_key] = FeaturePyramidNetworks.conv1x1(c_top, lat_w)

        # 2. Top-down pathway with lateral connections
        for idx in range(len(level_keys) - 2, -1, -1):
            curr_key = level_keys[idx]
            higher_key = level_keys[idx + 1]
            c_curr = bottom_up_features[curr_key]
            c_in_curr = len(c_curr)

            if lateral_weights is not None and curr_key in lateral_weights:
                curr_lat_w = lateral_weights[curr_key]
            else:
                curr_lat_w = [[1.0 / c_in_curr for _ in range(c_in_curr)] for _ in range(d_pyramid)]

            lat_curr = FeaturePyramidNetworks.conv1x1(c_curr, curr_lat_w)
            up_higher = FeaturePyramidNetworks.upsample2x_nearest(m_maps[higher_key])

            # Ensure spatial alignment if slight rounding occurred
            h_lat, w_lat = len(lat_curr[0]), len(lat_curr[0][0])
            h_up, w_up = len(up_higher[0]), len(up_higher[0][0])
            if h_lat != h_up or w_lat != w_up:
                # Crop or pad up_higher to match lat_curr
                trimmed_up = [[[up_higher[ch][i % h_up][j % w_up] for j in range(w_lat)] for i in range(h_lat)] for ch in range(len(up_higher))]
                up_higher = trimmed_up

            m_maps[curr_key] = FeaturePyramidNetworks.add_elementwise(lat_curr, up_higher)

        # 3. 3x3 anti-aliasing smoothing to produce P_levels
        pyramid_outputs: Dict[str, List[List[List[float]]]] = {}
        for key in level_keys:
            p_key = "P" + key[1:]
            sm_w = smooth_weights.get(p_key) if smooth_weights else None
            pyramid_outputs[p_key] = FeaturePyramidNetworks.conv3x3_smooth(m_maps[key], sm_w)

        return pyramid_outputs
