"""Bidirectional Recurrent Neural Networks (BiRNN) Forward-Backward Contextual Fusion.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: bidirectional_rnn
  category: neural_network_architecture
  subcategory: recurrent_networks
  id: ALGO-NN-94
  equation: |
    \\overrightarrow{h}_t = \\tanh(\\overrightarrow{W}_h \\overrightarrow{h}_{t-1} + \\overrightarrow{W}_x x_t + \\overrightarrow{b}_h)
    \\overleftarrow{h}_t = \\tanh(\\overleftarrow{W}_h \\overleftarrow{h}_{t+1} + \\overleftarrow{W}_x x_t + \\overleftarrow{b}_h)
    h_t = [\\overrightarrow{h}_t \\, \\| \\, \\overleftarrow{h}_t]
    y_t = W_y h_t + b_y
  domain:
    sequence_length: T
    forward_hidden_dim: d_f
    backward_hidden_dim: d_b
    output_representation_dim: "d_f + d_b"
  properties:
    non_causal_full_context: true
    dual_temporal_pass: true
    concatenated_bidirectional_representation: true
    offline_sequence_labeling: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class BidirectionalRNN:
    """Bidirectional Recurrent Neural Network (BiRNN) Dual-Direction Unroller."""

    @staticmethod
    def forward_unroll(
        x_seq: List[List[float]],
        w_xfwd: List[List[float]],
        w_hfwd: List[List[float]],
        b_hfwd: List[float],
        w_xbwd: List[List[float]],
        w_hbwd: List[List[float]],
        b_hbwd: List[float],
        w_y: Optional[List[List[float]]] = None,
        b_y: Optional[List[float]] = None
    ) -> Tuple[List[List[float]], Optional[List[List[float]]]]:
        """Execute bidirectional recurrent forward-backward unrolling.

        Args:
            x_seq: Sequence of shape [T, d_x].
            w_xfwd: Forward input weights [d_f, d_x].
            w_hfwd: Forward hidden weights [d_f, d_f].
            b_hfwd: Forward bias vector [d_f].
            w_xbwd: Backward input weights [d_b, d_x].
            w_hbwd: Backward hidden weights [d_b, d_b].
            b_hbwd: Backward bias vector [d_b].
            w_y: Optional emission matrix [d_y, d_f + d_b].
            b_y: Optional emission bias [d_y].

        Returns:
            Tuple of:
              - h_combined: List of concatenated representations [T, d_f + d_b].
              - y_preds: List of output predictions [T, d_y] if w_y provided, else None.
        """
        t_steps = len(x_seq)
        assert t_steps > 0, "Sequence must be non-empty."
        d_x = len(x_seq[0])
        d_f = len(w_hfwd)
        d_b = len(w_hbwd)

        # 1. Forward Pass (t = 0 to T-1)
        h_fwd_seq: List[List[float]] = []
        curr_hfwd = [0.0 for _ in range(d_f)]
        for t in range(t_steps):
            x_t = x_seq[t]
            next_hfwd = [0.0 for _ in range(d_f)]
            for i in range(d_f):
                val = b_hfwd[i]
                for j in range(d_f):
                    val += w_hfwd[i][j] * curr_hfwd[j]
                for k in range(d_x):
                    val += w_xfwd[i][k] * x_t[k]
                next_hfwd[i] = math.tanh(val)
            curr_hfwd = next_hfwd
            h_fwd_seq.append(curr_hfwd)

        # 2. Backward Pass (t = T-1 down to 0)
        h_bwd_seq: List[List[float]] = [[0.0 for _ in range(d_b)] for _ in range(t_steps)]
        curr_hbwd = [0.0 for _ in range(d_b)]
        for t in range(t_steps - 1, -1, -1):
            x_t = x_seq[t]
            next_hbwd = [0.0 for _ in range(d_b)]
            for i in range(d_b):
                val = b_hbwd[i]
                for j in range(d_b):
                    val += w_hbwd[i][j] * curr_hbwd[j]
                for k in range(d_x):
                    val += w_xbwd[i][k] * x_t[k]
                next_hbwd[i] = math.tanh(val)
            curr_hbwd = next_hbwd
            h_bwd_seq[t] = curr_hbwd

        # 3. Concatenate representations [h_fwd || h_bwd]
        h_combined = [h_fwd_seq[t] + h_bwd_seq[t] for t in range(t_steps)]

        # 4. Optional emission prediction
        y_preds = None
        if w_y is not None:
            d_y = len(w_y)
            y_preds = []
            for t in range(t_steps):
                y_t = [0.0 for _ in range(d_y)]
                h_t = h_combined[t]
                for o in range(d_y):
                    val = b_y[o] if b_y is not None else 0.0
                    for c in range(d_f + d_b):
                        val += w_y[o][c] * h_t[c]
                    y_t[o] = val
                y_preds.append(y_t)

        return h_combined, y_preds
