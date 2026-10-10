from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoDeformableConvolution:
    """
    ---
    contract:
      algo_id: ALGO-NN-82
      name: NnAlgoDeformableConvolution
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.convolution
        - nn.deformable
        - nn.adaptive_sampling
        - nn.dense_prediction
      inputs:
        type: object
        required:
          - x
          - offsets
          - weight
        properties:
          x:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Input feature map tensor of shape (C_in, H, W).
          offsets:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: Learned continuous spatial offsets of shape (K, 2, H, W) where K=9 for 3x3 kernel.
          weight:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
            description: Filter kernel weights of shape (C_out, C_in, 3, 3).
          modulations:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Optional DCNv2 modulation masks of shape (K, H, W) with values in [0, 1].
          bias:
            type: array
            items:
              type: number
            description: Optional output bias vector of length C_out.
      outputs:
        type: object
        required:
          - output
        properties:
          output:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Output convolved feature map tensor of shape (C_out, H, W).
      parameters: {}
      input_assumptions:
        - x is a valid non-empty 3D tensor of shape [C_in, H, W]
        - offsets provides K=9 pairs of (dy, dx) per spatial coordinate
        - weight has shape [C_out, C_in, 3, 3]
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Bounded by bilinear interpolation precision at fractional coordinates"
      uses_model: false
      complexity:
        variables:
          K: number of sampling points (9)
          C_in: input channels
          C_out: output channels
          H: height
          W: width
        time_worst: "O(K * C_in * C_out * H * W)"
        time_typical: "O(K * C_in * C_out * H * W)"
        space: "O(C_out * H * W)"
      preconditions:
        - len(input.x) > 0 and len(input.x[0]) > 0 and len(input.x[0][0]) > 0
        - len(input.offsets) == 9
        - len(input.weight[0]) == len(input.x) and len(input.weight[0][0]) == 3 and len(input.weight[0][0][0]) == 3
      postconditions:
        - len(output.output) == len(input.weight)
        - len(output.output[0]) == len(input.x[0])
        - len(output.output[0][0]) == len(input.x[0][0])
      certificate: "y(p_0) = sum_{k=1}^K w_k * m_k(p_0) * x(p_0 + p_k + delta_p_k(p_0)) via bilinear interpolation"
      compatible_adapters:
        - ADAPTER-DEFORMABLE-CONV
        - ADAPTER-OBJECT-DETECTOR
      related_algos:
        - ALGO-NN-67
        - ALGO-NN-70
        - ALGO-NN-88
      references:
        - "https://doi.org/10.1109/ICCV.2017.89"
        - "https://doi.org/10.1109/CVPR.2019.00953"
    ---
    """

    @staticmethod
    def bilinear_interpolate_2d(
        x: List[List[float]],
        py: float,
        px: float,
    ) -> float:
        h = len(x)
        w = len(x[0])

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

        v1 = x[y_low][x_low] if (0 <= y_low < h and 0 <= x_low < w) else 0.0
        v2 = x[y_low][x_high] if (0 <= y_low < h and 0 <= x_high < w) else 0.0
        v3 = x[y_high][x_low] if (0 <= y_high < h and 0 <= x_low < w) else 0.0
        v4 = x[y_high][x_high] if (0 <= y_high < h and 0 <= x_high < w) else 0.0

        w1 = hy * hx
        w2 = hy * lx
        w3 = ly * hx
        w4 = ly * lx

        return w1 * v1 + w2 * v2 + w3 * v3 + w4 * v4

    @staticmethod
    def forward(
        x: List[List[List[float]]],
        offsets: List[List[List[List[float]]]],
        weight: List[List[List[List[float]]]],
        modulations: Optional[List[List[List[List[float]]]]] = None,
        bias: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not x or len(x) == 0 or len(x[0]) == 0 or len(x[0][0]) == 0:
            raise ValueError("Precondition failed: x must be non-empty [C, H, W]")
        c_in = len(x)
        h = len(x[0])
        w = len(x[0][0])
        c_out = len(weight)

        grid = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        k_pts = len(grid)

        if len(offsets) != k_pts:
            raise ValueError(f"Precondition failed: offsets must have {k_pts} sampling points")
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
                    for k, (gy, gx) in enumerate(grid):
                        dy = offsets[k][0][i][j]
                        dx = offsets[k][1][i][j]
                        py = float(i + gy) + dy
                        px = float(j + gx) + dx

                        m_val = modulations[k][i][j] if modulations is not None else 1.0

                        for ci in range(c_in):
                            val = NnAlgoDeformableConvolution.bilinear_interpolate_2d(x[ci], py, px)
                            w_ky = gy + 1
                            w_kx = gx + 1
                            w_val = weight[co][ci][w_ky][w_kx]
                            s += w_val * m_val * val
                    out[co][i][j] = s

        return {"output": out}
