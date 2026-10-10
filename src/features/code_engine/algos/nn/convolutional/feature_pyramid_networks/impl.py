from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoFeaturePyramidNetworks:
    """
    ---
    contract:
      algo_id: ALGO-NN-80
      name: NnAlgoFeaturePyramidNetworks
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.pyramid
        - nn.multi_scale
        - nn.object_detection
      inputs:
        type: object
        required:
          - bottom_up_features
        properties:
          bottom_up_features:
            type: object
            description: Dictionary of bottom-up feature maps C_l where each map is [C_l, H_l, W_l].
          d_pyramid:
            type: integer
            default: 256
            minimum: 1
            description: Unified channel depth d across all pyramid levels.
          lateral_weights:
            type: object
            description: Optional custom 1x1 projection weights per stage.
          smooth_weights:
            type: object
            description: Optional custom 3x3 anti-aliasing convolution weights per stage.
      outputs:
        type: object
        required:
          - pyramid_features
        properties:
          pyramid_features:
            type: object
            description: Dictionary of multi-scale feature pyramid representations P_l of shape [d, H_l, W_l].
      parameters: {}
      input_assumptions:
        - bottom_up_features contains at least 2 hierarchical levels
        - each stage map has valid 3D tensor dimensions [C, H, W]
        - spatial resolutions decrease monotonically across consecutive stages
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Bounded by floating point roundoff in nearest-neighbor upsampling and linear convolution"
      uses_model: false
      complexity:
        variables:
          L: number of pyramid stages
          d: unified channel dimension
          H_l: height of feature map at stage l
          W_l: width of feature map at stage l
        time_worst: "O(sum_{l=2}^L (d * C_l + 9 * d^2) * H_l * W_l)"
        time_typical: "O(sum_{l=2}^L (d * C_l + 9 * d^2) * H_l * W_l)"
        space: "O(d * sum_{l=2}^L H_l * W_l)"
      preconditions:
        - len(input.bottom_up_features) >= 2
        - all(len(map_tensor) > 0 and len(map_tensor[0]) > 0 and len(map_tensor[0][0]) > 0 for map_tensor in input.bottom_up_features.values())
        - input.d_pyramid >= 1
      postconditions:
        - len(output.pyramid_features) == len(input.bottom_up_features)
        - all(len(p_map) == input.d_pyramid for p_map in output.pyramid_features.values())
      certificate: "multi_scale_pyramid_representation: P_l = Conv3x3(Conv1x1(C_l) + Upsample2x(M_{l+1}))"
      compatible_adapters:
        - ADAPTER-FEATURE-PYRAMID
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-70
        - ALGO-NN-84
        - ALGO-NN-85
      references:
        - "https://doi.org/10.1109/CVPR.2017.106"
        - "https://arxiv.org/abs/1612.03144"
    ---
    """

    @staticmethod
    def conv1x1(
        x: List[List[List[float]]],
        weight: List[List[float]],
        bias: Optional[List[float]] = None,
    ) -> List[List[List[float]]]:
        if not x or len(x) == 0 or len(x[0]) == 0 or len(x[0][0]) == 0:
            raise ValueError("Precondition failed: x must be non-empty [C, H, W]")
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])
        if not weight or len(weight) == 0 or len(weight[0]) != c_in:
            raise ValueError("Precondition failed: weight shape must be [C_out, C_in]")
        c_out = len(weight)
        if bias is not None and len(bias) != c_out:
            raise ValueError("Precondition failed: bias length must equal C_out")

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
        if not x or len(x) == 0 or len(x[0]) == 0 or len(x[0][0]) == 0:
            raise ValueError("Precondition failed: x must be non-empty [C, H, W]")
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
        b: List[List[List[float]]],
    ) -> List[List[List[float]]]:
        if len(a) != len(b):
            raise ValueError("Precondition failed: channel count must match")
        c = len(a)
        if c == 0:
            raise ValueError("Precondition failed: tensors must be non-empty")
        h = len(a[0])
        w = len(a[0][0])
        if len(b[0]) != h or len(b[0][0]) != w:
            raise ValueError("Precondition failed: spatial dimensions must match")

        out = [[[a[ch][i][j] + b[ch][i][j] for j in range(w)] for i in range(h)] for ch in range(c)]
        return out

    @staticmethod
    def conv3x3_smooth(
        x: List[List[List[float]]],
        weight: Optional[List[List[List[List[float]]]]] = None,
        bias: Optional[List[float]] = None,
    ) -> List[List[List[float]]]:
        if not x or len(x) == 0 or len(x[0]) == 0 or len(x[0][0]) == 0:
            raise ValueError("Precondition failed: x must be non-empty [C, H, W]")
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])

        if weight is None:
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
        if len(weight[0]) != c_in or len(weight[0][0]) != 3 or len(weight[0][0][0]) != 3:
            raise ValueError("Precondition failed: weight shape must be [C_out, C_in, 3, 3]")
        if bias is not None and len(bias) != c_out:
            raise ValueError("Precondition failed: bias length must match C_out")

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
        smooth_weights: Optional[Dict[str, List[List[List[List[float]]]]]] = None,
    ) -> Dict[str, Any]:
        if not bottom_up_features or len(bottom_up_features) < 2:
            raise ValueError("Precondition failed: len(input.bottom_up_features) >= 2")

        level_keys = sorted(list(bottom_up_features.keys()), key=lambda k: int(k[1:]) if k[1:].isdigit() else k)
        max_level_key = level_keys[-1]

        c_top = bottom_up_features[max_level_key]
        c_in_top = len(c_top)
        if lateral_weights is not None and max_level_key in lateral_weights:
            lat_w = lateral_weights[max_level_key]
        else:
            lat_w = [[1.0 / c_in_top for _ in range(c_in_top)] for _ in range(d_pyramid)]

        m_maps: Dict[str, List[List[List[float]]]] = {}
        m_maps[max_level_key] = NnAlgoFeaturePyramidNetworks.conv1x1(c_top, lat_w)

        for idx in range(len(level_keys) - 2, -1, -1):
            curr_key = level_keys[idx]
            higher_key = level_keys[idx + 1]
            c_curr = bottom_up_features[curr_key]
            c_in_curr = len(c_curr)

            if lateral_weights is not None and curr_key in lateral_weights:
                curr_lat_w = lateral_weights[curr_key]
            else:
                curr_lat_w = [[1.0 / c_in_curr for _ in range(c_in_curr)] for _ in range(d_pyramid)]

            lat_curr = NnAlgoFeaturePyramidNetworks.conv1x1(c_curr, curr_lat_w)
            up_higher = NnAlgoFeaturePyramidNetworks.upsample2x_nearest(m_maps[higher_key])

            h_lat, w_lat = len(lat_curr[0]), len(lat_curr[0][0])
            h_up, w_up = len(up_higher[0]), len(up_higher[0][0])
            if h_lat != h_up or w_lat != w_up:
                trimmed_up = [
                    [[up_higher[ch][i % h_up][j % w_up] for j in range(w_lat)] for i in range(h_lat)]
                    for ch in range(len(up_higher))
                ]
                up_higher = trimmed_up

            m_maps[curr_key] = NnAlgoFeaturePyramidNetworks.add_elementwise(lat_curr, up_higher)

        pyramid_outputs: Dict[str, List[List[List[float]]]] = {}
        for key in level_keys:
            p_key = "P" + key[1:]
            sm_w = smooth_weights.get(p_key) if smooth_weights else None
            pyramid_outputs[p_key] = NnAlgoFeaturePyramidNetworks.conv3x3_smooth(m_maps[key], sm_w)

        return {"pyramid_features": pyramid_outputs}
