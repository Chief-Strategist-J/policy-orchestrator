"""Recurrent Neural Networks (RNN) and Full Backpropagation Through Time (BPTT).

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: rnn_bptt
  category: neural_network_architecture
  subcategory: recurrent_networks
  id: ALGO-NN-90
  equation: |
    h_t = \\tanh(W_h h_{t-1} + W_x x_t + b_h)
    \\hat{y}_t = W_y h_t + b_y
    \\delta_t = \\left( \\frac{\\partial \\mathcal{L}_t}{\\partial h_t} + W_h^T \\delta_{t+1} \\right) \\odot (1 - h_t^2)
    \\frac{\\partial \\mathcal{L}}{\\partial W_h} = \\sum_{t=1}^T \\delta_t h_{t-1}^T
  domain:
    sequence_length: T
    hidden_dimension: d_h
    input_dimension: d_x
    output_dimension: d_y
  properties:
    exact_temporal_unrolling: true
    shared_weight_gradient_accumulation: true
    vanishing_exploding_gradient_susceptibility: true
    sequential_recurrence: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class VanillaRNNBPTT:
    """Vanilla Recurrent Neural Network forward unrolling and exact BPTT analytical gradient engine."""

    @staticmethod
    def forward_unroll(
        x_seq: List[List[float]],
        w_x: List[List[float]],
        w_h: List[List[float]],
        b_h: List[float],
        w_y: List[List[float]],
        b_y: List[float],
        h_0: Optional[List[float]] = None
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """Execute full sequence forward unrolling.

        Args:
            x_seq: Input sequence of shape [T, d_x].
            w_x: Input-to-hidden weight matrix [d_h, d_x].
            w_h: Hidden-to-hidden recurrence matrix [d_h, d_h].
            b_h: Hidden bias vector [d_h].
            w_y: Hidden-to-output projection matrix [d_y, d_h].
            b_y: Output bias vector [d_y].
            h_0: Optional initial hidden state [d_h].

        Returns:
            Tuple of (h_states [T+1, d_h], y_preds [T, d_y]).
        """
        t_steps = len(x_seq)
        assert t_steps > 0, "Sequence must be non-empty."
        d_x = len(x_seq[0])
        d_h = len(w_h)
        d_y = len(w_y)

        # Initialize hidden state history [T+1, d_h]
        h_states = [h_0 if h_0 is not None else [0.0 for _ in range(d_h)]]
        y_preds = []

        for t in range(t_steps):
            x_t = x_seq[t]
            h_prev = h_states[-1]

            # Compute pre-activation a_t = W_h h_{t-1} + W_x x_t + b_h
            h_next = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_h[i]
                for j in range(d_h):
                    val += w_h[i][j] * h_prev[j]
                for k in range(d_x):
                    val += w_x[i][k] * x_t[k]
                h_next[i] = math.tanh(val)

            h_states.append(h_next)

            # Compute output y_t = W_y h_t + b_y
            y_t = [0.0 for _ in range(d_y)]
            for o in range(d_y):
                val = b_y[o]
                for i in range(d_h):
                    val += w_y[o][i] * h_next[i]
                y_t[o] = val
            y_preds.append(y_t)

        return h_states, y_preds

    @staticmethod
    def backward_bptt(
        x_seq: List[List[float]],
        y_targets: List[List[float]],
        h_states: List[List[float]],
        y_preds: List[List[float]],
        w_x: List[List[float]],
        w_h: List[List[float]],
        w_y: List[List[float]]
    ) -> Dict[str, Any]:
        """Compute exact gradients via Backpropagation Through Time (BPTT) under MSE loss.

        Loss = 0.5 * sum_t ||y_pred_t - y_target_t||^2

        Args:
            x_seq: Input sequence [T, d_x].
            y_targets: Target sequence [T, d_y].
            h_states: Hidden state trajectory [T+1, d_h].
            y_preds: Predicted sequence [T, d_y].
            w_x, w_h, w_y: Model weight matrices.

        Returns:
            Dict containing parameter gradients: {"dW_x", "dW_h", "db_h", "dW_y", "db_y"}.
        """
        t_steps = len(x_seq)
        d_x = len(x_seq[0])
        d_h = len(w_h)
        d_y = len(w_y)

        # Initialize gradient accumulators
        dw_x = [[0.0 for _ in range(d_x)] for _ in range(d_h)]
        dw_h = [[0.0 for _ in range(d_h)] for _ in range(d_h)]
        db_h = [0.0 for _ in range(d_h)]
        dw_y = [[0.0 for _ in range(d_h)] for _ in range(d_y)]
        db_y = [0.0 for _ in range(d_y)]

        # Future gradient carried over time dL / dh_{t+1}
        dh_next = [0.0 for _ in range(d_h)]

        for t in range(t_steps - 1, -1, -1):
            h_t = h_states[t + 1]
            h_prev = h_states[t]
            x_t = x_seq[t]
            y_t = y_preds[t]
            target_t = y_targets[t]

            # Output loss gradient: dL / dy_t = (y_t - target_t)
            dy_t = [y_t[o] - target_t[o] for o in range(d_y)]

            # Output weights gradients
            for o in range(d_y):
                db_y[o] += dy_t[o]
                for i in range(d_h):
                    dw_y[o][i] += dy_t[o] * h_t[i]

            # Hidden gradient contribution: dL / dh_t = W_y^T dy_t + dh_next
            dh_t = list(dh_next)
            for i in range(d_h):
                for o in range(d_y):
                    dh_t[i] += w_y[o][i] * dy_t[o]

            # Pre-activation gradient: delta_t = dh_t * (1 - h_t^2)
            delta_t = [dh_t[i] * (1.0 - h_t[i] * h_t[i]) for i in range(d_h)]

            # Accumulate recurrence and input weights gradients
            for i in range(d_h):
                db_h[i] += delta_t[i]
                for j in range(d_h):
                    dw_h[i][j] += delta_t[i] * h_prev[j]
                for k in range(d_x):
                    dw_x[i][k] += delta_t[i] * x_t[k]

            # Pass gradient back to previous step: dh_prev = W_h^T delta_t
            dh_next = [0.0 for _ in range(d_h)]
            for j in range(d_h):
                for i in range(d_h):
                    dh_next[j] += w_h[i][j] * delta_t[i]

        return {
            "dW_x": dw_x,
            "dW_h": dw_h,
            "db_h": db_h,
            "dW_y": dw_y,
            "db_y": db_y
        }
