"""Gated Recurrent Unit (GRU) Cell and Sequence Unrolling.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: gru_cell
  category: neural_network_architecture
  subcategory: recurrent_networks
  id: ALGO-NN-93
  equation: |
    z_t = \\sigma(W_z x_t + U_z h_{t-1} + b_z)
    r_t = \\sigma(W_r x_t + U_r h_{t-1} + b_r)
    \\tilde{h}_t = \\tanh(W_h x_t + U_h (r_t \\odot h_{t-1}) + b_h)
    h_t = (1 - z_t) \\odot h_{t-1} + z_t \\odot \\tilde{h}_t
  domain:
    hidden_dimension: d_h
    input_dimension: d_x
    gates: "z_t, r_t \\in (0, 1)^{d_h}"
  properties:
    two_gate_parameter_efficiency: true
    linear_state_interpolation: true
    elimination_of_separate_cell_state: true
    adaptive_temporal_reset: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class GRUCell:
    """Gated Recurrent Unit (GRU) transition step and sequence recurrence engine."""

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
    def step(
        x_t: List[float],
        h_prev: List[float],
        w_z: List[List[float]],
        u_z: List[List[float]],
        b_z: List[float],
        w_r: List[List[float]],
        u_r: List[List[float]],
        b_r: List[float],
        w_h: List[List[float]],
        u_h: List[List[float]],
        b_h: List[float]
    ) -> Tuple[List[float], Dict[str, List[float]]]:
        """Execute a single GRU time step.

        Args:
            x_t: Input vector of length d_x.
            h_prev: Previous hidden state of length d_h.
            w_z, u_z, b_z: Update gate parameters.
            w_r, u_r, b_r: Reset gate parameters.
            w_h, u_h, b_h: Candidate hidden state parameters.

        Returns:
            Tuple of (h_next [d_h], gate_activations).
        """
        d_h = len(h_prev)
        d_x = len(x_t)

        # 1. Update gate z_t = sigmoid(W_z x_t + U_z h_{t-1} + b_z)
        z_t = [0.0 for _ in range(d_h)]
        for i in range(d_h):
            val = b_z[i]
            for k in range(d_x):
                val += w_z[i][k] * x_t[k]
            for j in range(d_h):
                val += u_z[i][j] * h_prev[j]
            z_t[i] = GRUCell.sigmoid(val)

        # 2. Reset gate r_t = sigmoid(W_r x_t + U_r h_{t-1} + b_r)
        r_t = [0.0 for _ in range(d_h)]
        for i in range(d_h):
            val = b_r[i]
            for k in range(d_x):
                val += w_r[i][k] * x_t[k]
            for j in range(d_h):
                val += u_r[i][j] * h_prev[j]
            r_t[i] = GRUCell.sigmoid(val)

        # 3. Candidate hidden state h_tilde = tanh(W_h x_t + U_h (r_t * h_{t-1}) + b_h)
        h_tilde = [0.0 for _ in range(d_h)]
        for i in range(d_h):
            val = b_h[i]
            for k in range(d_x):
                val += w_h[i][k] * x_t[k]
            for j in range(d_h):
                val += u_h[i][j] * (r_t[j] * h_prev[j])
            h_tilde[i] = math.tanh(val)

        # 4. State update: h_t = (1 - z_t) * h_{t-1} + z_t * h_tilde
        h_next = [(1.0 - z_t[i]) * h_prev[i] + z_t[i] * h_tilde[i] for i in range(d_h)]

        gates = {
            "z": z_t,
            "r": r_t,
            "h_tilde": h_tilde
        }
        return h_next, gates

    @staticmethod
    def forward_sequence(
        x_seq: List[List[float]],
        w_z: List[List[float]],
        u_z: List[List[float]],
        b_z: List[float],
        w_r: List[List[float]],
        u_r: List[List[float]],
        b_r: List[float],
        w_h: List[List[float]],
        u_h: List[List[float]],
        b_h: List[float],
        h_0: Optional[List[float]] = None
    ) -> List[List[float]]:
        """Unroll GRU across full sequence.

        Args:
            x_seq: Input sequence [T, d_x].
            h_0: Optional initial hidden state of length d_h.

        Returns:
            List of hidden states [T, d_h].
        """
        t_steps = len(x_seq)
        assert t_steps > 0
        d_h = len(w_z)

        curr_h = list(h_0) if h_0 is not None else [0.0 for _ in range(d_h)]
        h_history = []

        for t in range(t_steps):
            curr_h, _ = GRUCell.step(
                x_seq[t], curr_h,
                w_z, u_z, b_z,
                w_r, u_r, b_r,
                w_h, u_h, b_h
            )
            h_history.append(curr_h)

        return h_history
