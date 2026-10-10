from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoBidirectionalRNN:
    """
    ---
    contract:
      algo_id: ALGO-NN-94
      name: NnAlgoBidirectionalRNN
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.recurrent
        - nn.birnn
        - nn.sequence
        - nn.context_fusion
      inputs:
        type: object
        required:
          - x_seq
          - w_xfwd
          - w_hfwd
          - b_hfwd
          - w_xbwd
          - w_hbwd
          - b_hbwd
        properties:
          x_seq:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input sequence X of shape (T, d_x).
          w_xfwd:
            type: array
            items:
              type: array
              items:
                type: number
            description: Forward pass input projection weights of shape (d_f, d_x).
          w_hfwd:
            type: array
            items:
              type: array
              items:
                type: number
            description: Forward pass recurrent weights of shape (d_f, d_f).
          b_hfwd:
            type: array
            items:
              type: number
            description: Forward pass hidden bias of length d_f.
          w_xbwd:
            type: array
            items:
              type: array
              items:
                type: number
            description: Backward pass input projection weights of shape (d_b, d_x).
          w_hbwd:
            type: array
            items:
              type: array
              items:
                type: number
            description: Backward pass recurrent weights of shape (d_b, d_b).
          b_hbwd:
            type: array
            items:
              type: number
            description: Backward pass hidden bias of length d_b.
          w_y:
            type: array
            items:
              type: array
              items:
                type: number
            description: Optional emission projection weights of shape (d_y, d_f + d_b).
          b_y:
            type: array
            items:
              type: number
            description: Optional emission bias vector of length d_y.
      outputs:
        type: object
        required:
          - h_combined
        properties:
          h_combined:
            type: array
            items:
              type: array
              items:
                type: number
            description: Concatenated bidirectional representations of shape (T, d_f + d_b).
          y_preds:
            type: array
            items:
              type: array
              items:
                type: number
            description: Optional sequence emissions of shape (T, d_y).
      parameters: {}
      input_assumptions:
        - len(x_seq) >= 1 and len(x_seq[0]) == d_x
        - forward matrices dimensions conform to (d_f, d_x) and (d_f, d_f)
        - backward matrices dimensions conform to (d_b, d_x) and (d_b, d_b)
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
          T: sequence length
          d_x: input dimension
          d_f: forward hidden dimension
          d_b: backward hidden dimension
          d_y: output dimension
        time_worst: "O(T * (d_f^2 + d_b^2 + (d_f + d_b) * (d_x + d_y)))"
        time_typical: "O(T * (d_f^2 + d_b^2 + (d_f + d_b) * (d_x + d_y)))"
        space: "O(T * (d_f + d_b))"
      preconditions:
        - len(input.x_seq) > 0
        - len(input.w_xfwd) == len(input.w_hfwd) == len(input.b_hfwd)
        - len(input.w_xbwd) == len(input.w_hbwd) == len(input.b_hbwd)
      postconditions:
        - len(output.h_combined) == len(input.x_seq)
      certificate: "h_t = [\\overrightarrow{h}_t \\parallel \\overleftarrow{h}_t]"
      compatible_adapters:
        - ADAPTER-BIRNN
        - ADAPTER-SEQUENCE-TAGGER
      related_algos:
        - ALGO-NN-90
        - ALGO-NN-92
        - ALGO-NN-93
        - ALGO-NN-95
      references:
        - "https://doi.org/10.1109/78.650093"
        - "https://arxiv.org/abs/1303.5778"
    ---
    """

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
        b_y: Optional[List[float]] = None,
    ) -> Tuple[List[List[float]], Optional[List[List[float]]]]:
        if not x_seq or len(x_seq) == 0:
            raise ValueError("Precondition failed: sequence x_seq must be non-empty")

        t_steps = len(x_seq)
        d_x = len(x_seq[0])
        d_f = len(w_hfwd)
        d_b = len(w_hbwd)

        if len(w_xfwd) != d_f or len(b_hfwd) != d_f or len(w_hfwd[0]) != d_f:
            raise ValueError("Precondition failed: forward parameters dimension mismatch")
        if len(w_xbwd) != d_b or len(b_hbwd) != d_b or len(w_hbwd[0]) != d_b:
            raise ValueError("Precondition failed: backward parameters dimension mismatch")
        if len(w_xfwd[0]) != d_x or len(w_xbwd[0]) != d_x:
            raise ValueError("Precondition failed: input projection weights must match d_x")

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

        h_combined = [h_fwd_seq[t] + h_bwd_seq[t] for t in range(t_steps)]

        y_preds = None
        if w_y is not None:
            d_y = len(w_y)
            if len(w_y[0]) != d_f + d_b:
                raise ValueError("Precondition failed: emission matrix w_y must have d_f + d_b columns")
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
