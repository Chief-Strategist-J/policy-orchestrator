from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoLSTMCell:
    """
    ---
    contract:
      algo_id: ALGO-NN-92
      name: NnAlgoLSTMCell
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.recurrent
        - nn.lstm
        - nn.sequence
        - nn.gated_memory
      inputs:
        type: object
        required:
          - x_t
          - h_prev
          - c_prev
          - w_gates
          - u_gates
          - b_gates
        properties:
          x_t:
            type: array
            items:
              type: number
            description: Input vector x_t of length d_x at time step t.
          h_prev:
            type: array
            items:
              type: number
            description: Previous hidden state h_{t-1} of length d_h.
          c_prev:
            type: array
            items:
              type: number
            description: Previous cell state c_{t-1} of length d_h.
          w_gates:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input-to-gate projection matrix of shape (4 * d_h, d_x).
          u_gates:
            type: array
            items:
              type: array
              items:
                type: number
            description: Hidden-to-gate recurrent transition matrix of shape (4 * d_h, d_h).
          b_gates:
            type: array
            items:
              type: number
            description: Gate bias vector of length 4 * d_h.
      outputs:
        type: object
        required:
          - h_next
          - c_next
          - gates
        properties:
          h_next:
            type: array
            items:
              type: number
            description: Updated hidden state vector h_t of length d_h.
          c_next:
            type: array
            items:
              type: number
            description: Updated cell state vector c_t of length d_h.
          gates:
            type: object
            description: Intermediate gate activation vectors (f, i, c_tilde, o).
      parameters: {}
      input_assumptions:
        - len(h_prev) == len(c_prev) == d_h
        - len(w_gates) == len(u_gates) == len(b_gates) == 4 * d_h
        - len(w_gates[0]) == len(x_t) and len(u_gates[0]) == d_h
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Standard IEEE-754 floating point precision"
      uses_model: false
      complexity:
        variables:
          d_h: hidden state dimension
          d_x: input dimension
        time_worst: "O(d_h * (d_x + d_h))"
        time_typical: "O(d_h * (d_x + d_h))"
        space: "O(d_h)"
      preconditions:
        - len(input.h_prev) == len(input.c_prev)
        - len(input.w_gates) == 4 * len(input.h_prev)
        - len(input.u_gates) == 4 * len(input.h_prev)
        - len(input.b_gates) == 4 * len(input.h_prev)
        - len(input.w_gates[0]) == len(input.x_t)
        - len(input.u_gates[0]) == len(input.h_prev)
      postconditions:
        - len(output.h_next) == len(input.h_prev)
        - len(output.c_next) == len(input.c_prev)
      certificate: "c_t = f_t \\odot c_{t-1} + i_t \\odot \\tilde{c}_t and h_t = o_t \\odot \\tanh(c_t)"
      compatible_adapters:
        - ADAPTER-LSTM-CELL
        - ADAPTER-RECURRENT-LAYER
      related_algos:
        - ALGO-NN-90
        - ALGO-NN-91
        - ALGO-NN-93
        - ALGO-NN-94
      references:
        - "https://doi.org/10.1162/neco.1997.9.8.1735"
        - "https://doi.org/10.1162/089976600300015015"
    ---
    """

    @staticmethod
    def sigmoid(x: float) -> float:
        if x >= 0.0:
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
        b_gates: List[float],
    ) -> Tuple[List[float], List[float], Dict[str, List[float]]]:
        d_h = len(h_prev)
        d_x = len(x_t)

        if len(c_prev) != d_h:
            raise ValueError(f"Precondition failed: c_prev length {len(c_prev)} != h_prev length {d_h}")
        if len(w_gates) != 4 * d_h or len(u_gates) != 4 * d_h or len(b_gates) != 4 * d_h:
            raise ValueError(f"Precondition failed: gates dimension must equal 4 * d_h ({4 * d_h})")
        if d_h > 0 and len(u_gates[0]) != d_h:
            raise ValueError(f"Precondition failed: u_gates inner dimension must equal d_h ({d_h})")
        if d_h > 0 and len(w_gates[0]) != d_x:
            raise ValueError(f"Precondition failed: w_gates inner dimension must equal d_x ({d_x})")

        raw = [0.0 for _ in range(4 * d_h)]
        for g in range(4 * d_h):
            val = b_gates[g]
            for k in range(d_x):
                val += w_gates[g][k] * x_t[k]
            for j in range(d_h):
                val += u_gates[g][j] * h_prev[j]
            raw[g] = val

        f_gate = [NnAlgoLSTMCell.sigmoid(raw[g]) for g in range(0, d_h)]
        i_gate = [NnAlgoLSTMCell.sigmoid(raw[g]) for g in range(d_h, 2 * d_h)]
        c_tilde = [math.tanh(raw[g]) for g in range(2 * d_h, 3 * d_h)]
        o_gate = [NnAlgoLSTMCell.sigmoid(raw[g]) for g in range(3 * d_h, 4 * d_h)]

        c_next = [f_gate[j] * c_prev[j] + i_gate[j] * c_tilde[j] for j in range(d_h)]
        tanh_c = [math.tanh(c_next[j]) for j in range(d_h)]
        h_next = [o_gate[j] * tanh_c[j] for j in range(d_h)]

        gates = {
            "f": f_gate,
            "i": i_gate,
            "c_tilde": c_tilde,
            "o": o_gate,
            "tanh_c": tanh_c,
        }
        return h_next, c_next, gates

    @staticmethod
    def forward_sequence(
        x_seq: List[List[float]],
        w_gates: List[List[float]],
        u_gates: List[List[float]],
        b_gates: List[float],
        h_0: Optional[List[float]] = None,
        c_0: Optional[List[float]] = None,
    ) -> Tuple[List[List[float]], List[List[float]]]:
        if not x_seq or len(x_seq) == 0:
            raise ValueError("Precondition failed: input sequence x_seq must be non-empty")

        t_steps = len(x_seq)
        d_h = len(w_gates) // 4
        d_x = len(x_seq[0])

        if len(w_gates) != 4 * d_h or len(u_gates) != 4 * d_h or len(b_gates) != 4 * d_h:
            raise ValueError("Precondition failed: gate weights dimension mismatch")

        curr_h = list(h_0) if h_0 is not None else [0.0 for _ in range(d_h)]
        curr_c = list(c_0) if c_0 is not None else [0.0 for _ in range(d_h)]

        h_out: List[List[float]] = []
        c_out: List[List[float]] = []

        for t in range(t_steps):
            curr_h, curr_c, _ = NnAlgoLSTMCell.step(x_seq[t], curr_h, curr_c, w_gates, u_gates, b_gates)
            h_out.append(curr_h)
            c_out.append(curr_c)

        return h_out, c_out
