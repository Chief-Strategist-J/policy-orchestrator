"""Receptive Field Analysis and Theoretical/Effective Spatial Coverage in Deep CNNs.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: receptive_field_analysis
  category: neural_network_architecture
  subcategory: convolutional_networks
  id: ALGO-NN-83
  equation: |
    r_l = r_{l-1} + (k'_l - 1) \\cdot j_{l-1}
    j_l = j_{l-1} \\cdot s_l
    \\text{start}_l = \\text{start}_{l-1} + \\left( \\frac{k'_l - 1}{2} - p_l \\right) \\cdot j_{l-1}
    k'_l = d_l (k_l - 1) + 1
  domain:
    layer_parameters: "Kernel size k_l \\ge 1, stride s_l \\ge 1, padding p_l \\ge 0, dilation d_l \\ge 1"
    initial_conditions: "r_0 = 1, j_0 = 1, start_0 = 0.5"
  properties:
    exact_linear_recurrence: true
    coordinate_center_tracking: true
    effective_receptive_field_gaussian_decay: true
"""

from typing import List, Dict, Any, Tuple
import math


class LayerSpec:
    """Specification of a convolutional or pooling layer for receptive field tracking."""
    def __init__(self, name: str, kernel_size: int, stride: int = 1, padding: int = 0, dilation: int = 1):
        assert kernel_size >= 1, "Kernel size must be >= 1"
        assert stride >= 1, "Stride must be >= 1"
        assert padding >= 0, "Padding must be >= 0"
        assert dilation >= 1, "Dilation must be >= 1"
        self.name = name
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation

    @property
    def effective_kernel_size(self) -> int:
        return self.dilation * (self.kernel_size - 1) + 1


class ReceptiveFieldAnalysis:
    """Theoretical Receptive Field (TRF) and Coordinate Mapping Analyzer for CNNs."""

    @staticmethod
    def compute_rf_profile(layers: List[LayerSpec]) -> List[Dict[str, Any]]:
        """Compute layer-by-layer receptive field size, cumulative jump, and start coordinates.

        Args:
            layers: List of LayerSpec objects in sequential execution order.

        Returns:
            List of dictionary status reports after each layer.
        """
        # Initial input state
        r = 1.0  # Receptive field size
        j = 1.0  # Cumulative jump / stride
        start = 0.5  # Coordinate of output pixel 0 center in input space

        history = [{
            "layer": "input",
            "rf_size": r,
            "jump": j,
            "start": start
        }]

        for layer in layers:
            k_eff = float(layer.effective_kernel_size)
            s = float(layer.stride)
            p = float(layer.padding)

            # Recurrence updates
            r_next = r + (k_eff - 1.0) * j
            start_next = start + ((k_eff - 1.0) / 2.0 - p) * j
            j_next = j * s

            r = r_next
            start = start_next
            j = j_next

            history.append({
                "layer": layer.name,
                "rf_size": r,
                "jump": j,
                "start": start,
                "kernel_size": layer.kernel_size,
                "effective_kernel_size": layer.effective_kernel_size,
                "stride": layer.stride,
                "padding": layer.padding,
                "dilation": layer.dilation
            })

        return history

    @staticmethod
    def output_to_input_span(
        out_idx: int,
        rf_size: float,
        jump: float,
        start: float
    ) -> Tuple[float, float, float]:
        """Compute input coordinate bounding box and center for a specific output index.

        Args:
            out_idx: 0-indexed spatial coordinate in output feature map.
            rf_size: Receptive field size of the feature map.
            jump: Cumulative stride.
            start: Start coordinate offset.

        Returns:
            Tuple (center_coord, min_coord, max_coord) in input pixel coordinates.
        """
        center = start + float(out_idx) * jump
        half_rf = (rf_size - 1.0) / 2.0
        min_coord = center - half_rf
        max_coord = center + half_rf
        return center, min_coord, max_coord

    @staticmethod
    def effective_receptive_field_std(layers: List[LayerSpec]) -> float:
        """Compute the theoretical standard deviation sigma of the Gaussian Effective Receptive Field (ERF).

        The ERF distribution asymptotically follows a 2D Gaussian with variance:
          sigma^2 = sum_l ( (k_l^2 - 1) / 12 * j_{l-1}^2 )

        Args:
            layers: List of LayerSpec objects.

        Returns:
            Standard deviation sigma of the ERF.
        """
        var_sum = 0.0
        curr_j = 1.0
        for layer in layers:
            k = float(layer.kernel_size)
            # Variance contribution of uniform kernel of width k
            k_var = (k * k - 1.0) / 12.0
            var_sum += k_var * (curr_j * curr_j)
            curr_j *= float(layer.stride)

        return math.sqrt(max(1e-9, var_sum))
