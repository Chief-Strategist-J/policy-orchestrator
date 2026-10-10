"""Truncated Backpropagation Through Time (TBPTT) for Streaming Sequences.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: truncated_bptt
  category: neural_network_architecture
  subcategory: recurrent_networks
  id: ALGO-NN-91
  equation: |
    h_t = \\tanh(W_h h_{t-1} + W_x x_t + b_h) \\quad \\text{for } t \\in [m k, (m+1)k - 1]
    h_{m k - 1} = \\text{detach}(h_{m k - 1}^{(m-1)})
    \\mathcal{L}^{(m)} = \\sum_{t = m k}^{(m+1)k - 1} \\mathcal{L}_t(\\hat{y}_t, y_t^*)
    \\nabla_\\theta \\mathcal{L} \\approx \\sum_m \\nabla_\\theta \\mathcal{L}^{(m)}
  domain:
    sequence_chunks: "M chunks of length k_1 forward, k_2 backward"
    memory_per_update: "\\mathcal{O}(k_2 \\cdot d_h)"
  properties:
    streaming_state_persistence: true
    computational_graph_detachment: true
    bounded_memory_overhead: true
    approximate_long_range_gradient: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class TruncatedBPTT:
    """Truncated Backpropagation Through Time (TBPTT) windowed trainer."""

    @staticmethod
    def train_chunk(
        x_chunk: List[List[float]],
        y_chunk_targets: List[List[float]],
        h_init: List[float],
        w_x: List[List[float]],
        w_h: List[List[float]],
        b_h: List[float],
        w_y: List[List[float]],
        b_y: List[float]
    ) -> Tuple[Dict[str, Any], List[float], float]:
        """Execute forward pass and BPTT backward pass restricted to a single window chunk of length k.

        The incoming initial hidden state h_init is treated as detached (constant).

        Args:
            x_chunk: Input window [k, d_x].
            y_chunk_targets: Target window [k, d_y].
            h_init: Detached incoming hidden state of length d_h.
            w_x, w_h, b_h, w_y, b_y: Model parameters.

        Returns:
            Tuple of:
              - grads: Dict containing parameter gradients for this chunk.
              - h_final: Final hidden state of length d_h to pass to next chunk.
              - chunk_loss: Total MSE loss on this chunk.
        """
        k_steps = len(x_chunk)
        d_x = len(x_chunk[0])
        d_h = len(w_h)
        d_y = len(w_y)

        # 1. Forward pass within chunk
        h_states = [list(h_init)]
        y_preds = []
        chunk_loss = 0.0

        for t in range(k_steps):
            x_t = x_chunk[t]
            h_prev = h_states[-1]

            # Recurrence
            h_next = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_h[i]
                for j in range(d_h):
                    val += w_h[i][j] * h_prev[j]
                for p in range(d_x):
                    val += w_x[i][p] * x_t[p]
                h_next[i] = math.tanh(val)
            h_states.append(h_next)

            # Output
            y_t = [0.0 for _ in range(d_y)]
            for o in range(d_y):
                val = b_y[o]
                for i in range(d_h):
                    val += w_y[o][i] * h_next[i]
                y_t[o] = val
            y_preds.append(y_t)

            # Accumulate loss
            target_t = y_chunk_targets[t]
            for o in range(d_y):
                chunk_loss += 0.5 * ((y_t[o] - target_t[o]) ** 2)

        # 2. Backward pass within chunk (truncated at t=0)
        dw_x = [[0.0 for _ in range(d_x)] for _ in range(d_h)]
        dw_h = [[0.0 for _ in range(d_h)] for _ in range(d_h)]
        db_h = [0.0 for _ in range(d_h)]
        dw_y = [[0.0 for _ in range(d_h)] for _ in range(d_y)]
        db_y = [0.0 for _ in range(d_y)]

        dh_next = [0.0 for _ in range(d_h)]

        for t in range(k_steps - 1, -1, -1):
            h_t = h_states[t + 1]
            h_prev = h_states[t]
            x_t = x_chunk[t]
            y_t = y_preds[t]
            target_t = y_chunk_targets[t]

            dy_t = [y_t[o] - target_t[o] for o in range(d_y)]

            for o in range(d_y):
                db_y[o] += dy_t[o]
                for i in range(d_h):
                    dw_y[o][i] += dy_t[o] * h_t[i]

            dh_t = list(dh_next)
            for i in range(d_h):
                for o in range(d_y):
                    dh_t[i] += w_y[o][i] * dy_t[o]

            delta_t = [dh_t[i] * (1.0 - h_t[i] * h_t[i]) for i in range(d_h)]

            for i in range(d_h):
                db_h[i] += delta_t[i]
                for j in range(d_h):
                    dw_h[i][j] += delta_t[i] * h_prev[j]
                for p in range(d_x):
                    dw_x[i][p] += delta_t[i] * x_t[p]

            dh_next = [0.0 for _ in range(d_h)]
            for j in range(d_h):
                for i in range(d_h):
                    dh_next[j] += w_h[i][j] * delta_t[i]

        grads = {
            "dW_x": dw_x,
            "dW_h": dw_h,
            "db_h": db_h,
            "dW_y": dw_y,
            "db_y": db_y
        }
        h_final = h_states[-1]
        return grads, h_final, chunk_loss
