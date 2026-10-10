from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoVanillaRNNBPTT:
    """
    ---
    contract:
      algo_id: ALGO-NN-90
      name: NnAlgoVanillaRNNBPTT
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.recurrent
        - nn.sequence
        - nn.bptt
        - nn.backpropagation
      inputs:
        type: object
        required:
          - x_seq
          - w_x
          - w_h
          - b_h
          - w_y
          - b_y
        properties:
          x_seq:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input sequence X of shape (T, d_x).
          w_x:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input-to-hidden projection weights of shape (d_h, d_x).
          w_h:
            type: array
            items:
              type: array
              items:
                type: number
            description: Recurrent hidden-to-hidden transition matrix of shape (d_h, d_h).
          b_h:
            type: array
            items:
              type: number
            description: Hidden bias vector of length d_h.
          w_y:
            type: array
            items:
              type: array
              items:
                type: number
            description: Hidden-to-output emission matrix of shape (d_y, d_h).
          b_y:
            type: array
            items:
              type: number
            description: Output bias vector of length d_y.
          h_0:
            type: array
            items:
              type: number
            description: Optional initial hidden state vector of length d_h.
      outputs:
        type: object
        required:
          - h_states
          - y_preds
        properties:
          h_states:
            type: array
            items:
              type: array
              items:
                type: number
            description: Full hidden state trajectory of shape (T + 1, d_h).
          y_preds:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output predictions of shape (T, d_y).
      parameters: {}
      input_assumptions:
        - x_seq is non-empty with length T >= 1
        - matrices dimensions conform: w_x (d_h, d_x), w_h (d_h, d_h), w_y (d_y, d_h)
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact analytical gradients via adjoint unrolled backpropagation"
      uses_model: false
      complexity:
        variables:
          T: sequence length
          d_x: input dimension
          d_h: hidden dimension
          d_y: output dimension
        time_worst: "O(T * (d_h^2 + d_h * d_x + d_y * d_h))"
        time_typical: "O(T * (d_h^2 + d_h * d_x + d_y * d_h))"
        space: "O(T * d_h)"
      preconditions:
        - len(input.x_seq) > 0 and len(input.x_seq[0]) > 0
        - len(input.w_h) == len(input.w_h[0]) and len(input.w_x) == len(input.w_h)
        - len(input.w_y[0]) == len(input.w_h)
      postconditions:
        - len(output.h_states) == len(input.x_seq) + 1
        - len(output.y_preds) == len(input.x_seq)
      certificate: "h_t = tanh(W_h h_{t-1} + W_x x_t + b_h) and y_t = W_y h_t + b_y"
      compatible_adapters:
        - ADAPTER-RNN-CELL
        - ADAPTER-SEQUENCE-MODEL
      related_algos:
        - ALGO-NN-91
        - ALGO-NN-92
        - ALGO-NN-93
        - ALGO-NN-94
      references:
        - "https://doi.org/10.1109/5.58337"
        - "https://proceedings.mlr.press/v28/pascanu13.html"
    ---
    """

    @staticmethod
    def forward_unroll(
        x_seq: List[List[float]],
        w_x: List[List[float]],
        w_h: List[List[float]],
        b_h: List[float],
        w_y: List[List[float]],
        b_y: List[float],
        h_0: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not x_seq or len(x_seq) == 0:
            raise ValueError("Precondition failed: sequence must be non-empty")
        t_steps = len(x_seq)
        d_x = len(x_seq[0])
        d_h = len(w_h)
        d_y = len(w_y)

        if len(w_x) != d_h or len(w_x[0]) != d_x:
            raise ValueError("Precondition failed: w_x shape must be (d_h, d_x)")
        if len(w_h[0]) != d_h or len(b_h) != d_h:
            raise ValueError("Precondition failed: w_h must be square (d_h, d_h)")
        if len(w_y[0]) != d_h or len(b_y) != d_y:
            raise ValueError("Precondition failed: w_y shape must be (d_y, d_h)")

        h_states = [h_0 if h_0 is not None else [0.0 for _ in range(d_h)]]
        y_preds = []

        for t in range(t_steps):
            x_t = x_seq[t]
            h_prev = h_states[-1]

            h_next = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_h[i]
                for j in range(d_h):
                    val += w_h[i][j] * h_prev[j]
                for k in range(d_x):
                    val += w_x[i][k] * x_t[k]
                h_next[i] = math.tanh(val)

            h_states.append(h_next)

            y_t = [0.0 for _ in range(d_y)]
            for o in range(d_y):
                val = b_y[o]
                for i in range(d_h):
                    val += w_y[o][i] * h_next[i]
                y_t[o] = val
            y_preds.append(y_t)

        return {
            "h_states": h_states,
            "y_preds": y_preds,
        }

    @staticmethod
    def backward_bptt(
        x_seq: List[List[float]],
        y_targets: List[List[float]],
        h_states: List[List[float]],
        y_preds: List[List[float]],
        w_x: List[List[float]],
        w_h: List[List[float]],
        w_y: List[List[float]],
    ) -> Dict[str, Any]:
        t_steps = len(x_seq)
        d_x = len(x_seq[0])
        d_h = len(w_h)
        d_y = len(w_y)

        dw_x = [[0.0 for _ in range(d_x)] for _ in range(d_h)]
        dw_h = [[0.0 for _ in range(d_h)] for _ in range(d_h)]
        db_h = [0.0 for _ in range(d_h)]
        dw_y = [[0.0 for _ in range(d_h)] for _ in range(d_y)]
        db_y = [0.0 for _ in range(d_y)]

        dh_next = [0.0 for _ in range(d_h)]

        for t in range(t_steps - 1, -1, -1):
            h_t = h_states[t + 1]
            h_prev = h_states[t]
            x_t = x_seq[t]
            y_t = y_preds[t]
            target_t = y_targets[t]

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
                for k in range(d_x):
                    dw_x[i][k] += delta_t[i] * x_t[k]

            dh_next = [0.0 for _ in range(d_h)]
            for j in range(d_h):
                for i in range(d_h):
                    dh_next[j] += w_h[i][j] * delta_t[i]

        return {
            "dW_x": dw_x,
            "dW_h": dw_h,
            "db_h": db_h,
            "dW_y": dw_y,
            "db_y": db_y,
        }
