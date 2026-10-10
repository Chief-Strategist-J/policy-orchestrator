from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoGRUCell:
    """
    ---
    contract:
      algo_id: ALGO-NN-93
      name: NnAlgoGRUCell
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.recurrent
        - nn.gru
        - nn.sequence
        - nn.gated_memory
      inputs:
        type: object
        required:
          - x_t
          - h_prev
          - w_z
          - u_z
          - b_z
          - w_r
          - u_r
          - b_r
          - w_h
          - u_h
          - b_h
        properties:
          x_t:
            type: array
            items:
              type: number
            description: Input vector x_t of length d_x.
          h_prev:
            type: array
            items:
              type: number
            description: Previous hidden state h_{t-1} of length d_h.
          w_z:
            type: array
            items:
              type: array
              items:
                type: number
            description: Update gate input matrix of shape (d_h, d_x).
          u_z:
            type: array
            items:
              type: array
              items:
                type: number
            description: Update gate recurrent matrix of shape (d_h, d_h).
          b_z:
            type: array
            items:
              type: number
            description: Update gate bias vector of length d_h.
          w_r:
            type: array
            items:
              type: array
              items:
                type: number
            description: Reset gate input matrix of shape (d_h, d_x).
          u_r:
            type: array
            items:
              type: array
              items:
                type: number
            description: Reset gate recurrent matrix of shape (d_h, d_h).
          b_r:
            type: array
            items:
              type: number
            description: Reset gate bias vector of length d_h.
          w_h:
            type: array
            items:
              type: array
              items:
                type: number
            description: Candidate state input matrix of shape (d_h, d_x).
          u_h:
            type: array
            items:
              type: array
              items:
                type: number
            description: Candidate state recurrent matrix of shape (d_h, d_h).
          b_h:
            type: array
            items:
              type: number
            description: Candidate state bias vector of length d_h.
      outputs:
        type: object
        required:
          - h_next
          - gates
        properties:
          h_next:
            type: array
            items:
              type: number
            description: Updated hidden state vector h_t of length d_h.
          gates:
            type: object
            description: Intermediate gate activations dictionary (z, r, h_tilde).
      parameters: {}
      input_assumptions:
        - len(h_prev) == d_h and len(x_t) == d_x
        - weight matrices dimensions match (d_h, d_x) and (d_h, d_h)
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
        - len(input.h_prev) == len(input.u_z)
        - len(input.x_t) == len(input.w_z[0])
        - len(input.w_z) == len(input.w_r) == len(input.w_h) == len(input.h_prev)
      postconditions:
        - len(output.h_next) == len(input.h_prev)
      certificate: "h_t = (1 - z_t) \\odot h_{t-1} + z_t \\odot \\tilde{h}_t"
      compatible_adapters:
        - ADAPTER-GRU-CELL
        - ADAPTER-RECURRENT-LAYER
      related_algos:
        - ALGO-NN-90
        - ALGO-NN-91
        - ALGO-NN-92
        - ALGO-NN-94
      references:
        - "https://arxiv.org/abs/1406.1078"
        - "https://arxiv.org/abs/1412.3555"
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
        w_z: List[List[float]],
        u_z: List[List[float]],
        b_z: List[float],
        w_r: List[List[float]],
        u_r: List[List[float]],
        b_r: List[float],
        w_h: List[List[float]],
        u_h: List[List[float]],
        b_h: List[float],
    ) -> Tuple[List[float], Dict[str, List[float]]]:
        d_h = len(h_prev)
        d_x = len(x_t)

        if len(w_z) != d_h or len(w_r) != d_h or len(w_h) != d_h:
            raise ValueError(f"Precondition failed: input weight matrices rows must match d_h ({d_h})")
        if len(u_z) != d_h or len(u_r) != d_h or len(u_h) != d_h:
            raise ValueError(f"Precondition failed: recurrent weight matrices rows must match d_h ({d_h})")
        if len(b_z) != d_h or len(b_r) != d_h or len(b_h) != d_h:
            raise ValueError(f"Precondition failed: bias vectors must match d_h ({d_h})")

        z_t = [0.0 for _ in range(d_h)]
        for i in range(d_h):
            val = b_z[i]
            for k in range(d_x):
                val += w_z[i][k] * x_t[k]
            for j in range(d_h):
                val += u_z[i][j] * h_prev[j]
            z_t[i] = NnAlgoGRUCell.sigmoid(val)

        r_t = [0.0 for _ in range(d_h)]
        for i in range(d_h):
            val = b_r[i]
            for k in range(d_x):
                val += w_r[i][k] * x_t[k]
            for j in range(d_h):
                val += u_r[i][j] * h_prev[j]
            r_t[i] = NnAlgoGRUCell.sigmoid(val)

        h_tilde = [0.0 for _ in range(d_h)]
        for i in range(d_h):
            val = b_h[i]
            for k in range(d_x):
                val += w_h[i][k] * x_t[k]
            for j in range(d_h):
                val += u_h[i][j] * (r_t[j] * h_prev[j])
            h_tilde[i] = math.tanh(val)

        h_next = [(1.0 - z_t[i]) * h_prev[i] + z_t[i] * h_tilde[i] for i in range(d_h)]

        gates = {
            "z": z_t,
            "r": r_t,
            "h_tilde": h_tilde,
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
        h_0: Optional[List[float]] = None,
    ) -> List[List[float]]:
        if not x_seq or len(x_seq) == 0:
            raise ValueError("Precondition failed: sequence x_seq must be non-empty")

        t_steps = len(x_seq)
        d_h = len(w_z)

        curr_h = list(h_0) if h_0 is not None else [0.0 for _ in range(d_h)]
        h_history: List[List[float]] = []

        for t in range(t_steps):
            curr_h, _ = NnAlgoGRUCell.step(
                x_seq[t],
                curr_h,
                w_z,
                u_z,
                b_z,
                w_r,
                u_r,
                b_r,
                w_h,
                u_h,
                b_h,
            )
            h_history.append(curr_h)

        return h_history
