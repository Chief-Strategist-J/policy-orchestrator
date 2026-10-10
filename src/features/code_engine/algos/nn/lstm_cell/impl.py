"""Long Short-Term Memory (LSTM) Cell and Unrolled Sequence Recurrence.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: lstm_cell
  category: neural_network_architecture
  subcategory: recurrent_networks
  id: ALGO-NN-92
  equation: |
    f_t = \\sigma(W_f x_t + U_f h_{t-1} + b_f)
    i_t = \\sigma(W_i x_t + U_i h_{t-1} + b_i)
    \\tilde{c}_t = \\tanh(W_c x_t + U_c h_{t-1} + b_c)
    o_t = \\sigma(W_o x_t + U_o h_{t-1} + b_o)
    c_t = f_t \\odot c_{t-1} + i_t \\odot \\tilde{c}_t
    h_t = o_t \\odot \\tanh(c_t)
  domain:
    hidden_dimension: d_h
    input_dimension: d_x
    gates: "f_t, i_t, o_t \\in (0, 1)^{d_h}"
  properties:
    additive_constant_error_carousel: true
    gated_information_flow: true
    long_range_gradient_highway: true
    forget_gate_bias_initialization: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class LSTMCell:
    """Long Short-Term Memory (LSTM) recurrent transition cell and sequential unroller."""

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
        c_prev: List[float],
        w_gates: List[List[float]],
        u_gates: List[List[float]],
        b_gates: List[float]
    ) -> Tuple[List[float], List[float], Dict[str, List[float]]]:
        """Execute a single LSTM time step.

        Gate parameter ordering (standard 4*d_h fused layout):
          - [0 : d_h] -> Forget gate (f)
          - [d_h : 2*d_h] -> Input gate (i)
          - [2*d_h : 3*d_h] -> Candidate cell (c_tilde)
          - [3*d_h : 4*d_h] -> Output gate (o)

        Args:
            x_t: Input vector of length d_x.
            h_prev: Previous hidden state of length d_h.
            c_prev: Previous cell state of length d_h.
            w_gates: Input-to-gate matrix [4*d_h, d_x].
            u_gates: Recurrent hidden-to-gate matrix [4*d_h, d_h].
            b_gates: Gate bias vector of length 4*d_h.

        Returns:
            Tuple of (h_next, c_next, gate_activations).
        """
        d_h = len(h_prev)
        d_x = len(x_t)
        assert len(w_gates) == 4 * d_h and len(u_gates) == 4 * d_h and len(b_gates) == 4 * d_h

        # Compute raw gate pre-activations
        raw = [0.0 for _ in range(4 * d_h)]
        for g in range(4 * d_h):
            val = b_gates[g]
            for k in range(d_x):
                val += w_gates[g][k] * x_t[k]
            for j in range(d_h):
                val += u_gates[g][j] * h_prev[j]
            raw[g] = val

        f_gate = [LSTMCell.sigmoid(raw[g]) for g in range(0, d_h)]
        i_gate = [LSTMCell.sigmoid(raw[g]) for g in range(d_h, 2 * d_h)]
        c_tilde = [math.tanh(raw[g]) for g in range(2 * d_h, 3 * d_h)]
        o_gate = [LSTMCell.sigmoid(raw[g]) for g in range(3 * d_h, 4 * d_h)]

        # Cell update: c_t = f_t * c_{t-1} + i_t * c_tilde
        c_next = [f_gate[j] * c_prev[j] + i_gate[j] * c_tilde[j] for j in range(d_h)]

        # Hidden state: h_t = o_t * tanh(c_t)
        tanh_c = [math.tanh(c_next[j]) for j in range(d_h)]
        h_next = [o_gate[j] * tanh_c[j] for j in range(d_h)]

        gates = {
            "f": f_gate,
            "i": i_gate,
            "c_tilde": c_tilde,
            "o": o_gate,
            "tanh_c": tanh_c
        }
        return h_next, c_next, gates

    @staticmethod
    def forward_sequence(
        x_seq: List[List[float]],
        w_gates: List[List[float]],
        u_gates: List[List[float]],
        b_gates: List[float],
        h_0: Optional[List[float]] = None,
        c_0: Optional[List[float]] = None
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """Unroll LSTM across an entire sequence.

        Args:
            x_seq: Input sequence [T, d_x].
            w_gates, u_gates, b_gates: LSTM parameters.
            h_0, c_0: Optional initial states.

        Returns:
            Tuple of (h_history [T, d_h], c_history [T, d_h]).
        """
        t_steps = len(x_seq)
        assert t_steps > 0
        d_h = len(w_gates) // 4

        curr_h = list(h_0) if h_0 is not None else [0.0 for _ in range(d_h)]
        curr_c = list(c_0) if c_0 is not None else [0.0 for _ in range(d_h)]

        h_out = []
        c_out = []

        for t in range(t_steps):
            curr_h, curr_c, _ = LSTMCell.step(x_seq[t], curr_h, curr_c, w_gates, u_gates, b_gates)
            h_out.append(curr_h)
            c_out.append(curr_c)

        return h_out, c_out
