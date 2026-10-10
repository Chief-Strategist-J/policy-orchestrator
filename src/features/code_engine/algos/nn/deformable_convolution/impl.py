"""Deformable Convolution (DCN v1 / DCN v2) with Bilinear Interpolation Sampling.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: deformable_convolution
  category: neural_network_architecture
  subcategory: convolutional_networks
  id: ALGO-NN-82
  equation: |
    y(p_0) = \\sum_{k=1}^K w_k \\cdot m_k(p_0) \\cdot x(p_0 + p_k + \\Delta p_k(p_0))
    x(p) = \\sum_{q} \\max(0, 1 - |q_x - p_x|) \\cdot \\max(0, 1 - |q_y - p_y|) \\cdot x(q)
  domain:
    sampling_grid: "Fractional 2D coordinates (y, x) \\in \\mathbb{R}^2"
    modulation_range: "m_k \\in [0, 1]"
    kernel_size: K (typically 3x3 = 9 sampling points)
  properties:
    adaptive_receptive_field: true
    bilinear_spatial_interpolation: true
    differentiable_offset_sampling: true
    content_dependent_deformation: true
"""

from typing import List, Tuple, Optional
import math


class DeformableConvolution:
    """Deformable Convolutional Operator with Learned Spatial Offsets and Modulations."""

    @staticmethod
    def bilinear_interpolate_2d(
        x: List[List[float]],
        py: float,
        px: float
    ) -> float:
        """Sample a 2D single-channel grid at continuous fractional coordinates (py, px) via bilinear interpolation.

        Args:
            x: 2D input matrix of shape [H, W].
            py: Continuous y-coordinate (row).
            px: Continuous x-coordinate (col).

        Returns:
            Bilinearly interpolated scalar value (0.0 if completely out of bounds).
        """
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
        bias: Optional[List[float]] = None
    ) -> List[List[List[float]]]:
        """Execute Deformable Convolution 2D.

        Standard 3x3 sampling grid relative offsets:
          k=0: (-1,-1), k=1: (-1,0), k=2: (-1,1)
          k=3: ( 0,-1), k=4: ( 0,0), k=5: ( 0,1)
          k=6: ( 1,-1), k=7: ( 1,0), k=8: ( 1,1)

        Args:
            x: Input feature map [C_in, H, W].
            offsets: Learned continuous offsets [2*K, H, W] or [K, 2, H, W] where K=9 for 3x3.
                     Formatted here as [K, 2, H, W] where dim 1 is (dy, dx).
            weight: Convolution filter weights [C_out, C_in, 3, 3].
            modulations: Optional DCNv2 modulation masks [K, H, W] in range [0, 1].
            bias: Optional output bias vector of length C_out.

        Returns:
            Output feature map [C_out, H, W].
        """
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

        assert len(offsets) == k_pts, f"Offsets must provide {k_pts} sampling offsets."
        assert len(weight[0]) == c_in and len(weight[0][0]) == 3 and len(weight[0][0][0]) == 3

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
                            val = DeformableConvolution.bilinear_interpolate_2d(x[ci], py, px)
                            # weight coordinates for (gy, gx)
                            w_ky = gy + 1
                            w_kx = gx + 1
                            w_val = weight[co][ci][w_ky][w_kx]
                            s += w_val * m_val * val
                    out[co][i][j] = s

        return out
