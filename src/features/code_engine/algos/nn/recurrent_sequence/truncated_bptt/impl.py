from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoTruncatedBPTT:
    """
    ---
    contract:
      algo_id: ALGO-NN-91
      name: NnAlgoTruncatedBPTT
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.recurrent
        - nn.sequence
        - nn.streaming
        - nn.truncated_bptt
      inputs:
        type: object
        required:
          - x_chunk
          - y_chunk_targets
          - h_init
          - w_x
          - w_h
          - b_h
          - w_y
          - b_y
        properties:
          x_chunk:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input sequence chunk of shape (k, d_x).
          y_chunk_targets:
            type: array
            items:
              type: array
              items:
                type: number
            description: Target sequence chunk of shape (k, d_y).
          h_init:
            type: array
            items:
              type: number
            description: Detached initial hidden state vector of length d_h from previous chunk.
          w_x:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input-to-hidden weights of shape (d_h, d_x).
          w_h:
            type: array
            items:
              type: array
              items:
                type: number
            description: Recurrence weights of shape (d_h, d_h).
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
            description: Emission weights of shape (d_y, d_h).
          b_y:
            type: array
            items:
              type: number
            description: Output bias vector of length d_y.
      outputs:
        type: object
        required:
          - gradients
          - h_final
          - chunk_loss
        properties:
          gradients:
            type: object
            description: Gradients dW_x, dW_h, db_h, dW_y, db_y evaluated within truncation window.
          h_final:
            type: array
            items:
              type: number
            description: Final hidden state of length d_h to pass to subsequent chunk.
          chunk_loss:
            type: number
            description: Cumulative loss across this chunk.
      parameters: {}
      input_assumptions:
        - x_chunk has length k >= 1
        - h_init is detached from computational graph
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Bounded by exponential truncation decay O(lambda^{k+1})"
      uses_model: false
      complexity:
        variables:
          k: truncation window length
          d_x: input dimension
          d_h: hidden dimension
        time_worst: "O(k * (d_h^2 + d_h * d_x))"
        time_typical: "O(k * (d_h^2 + d_h * d_x))"
        space: "O(k * d_h)"
      preconditions:
        - len(input.x_chunk) == len(input.y_chunk_targets) > 0
        - len(input.h_init) == len(input.w_h)
      postconditions:
        - len(output.h_final) == len(input.h_init)
        - output.chunk_loss >= 0.0
      certificate: "Truncated backpropagation windowed within [mk, (m+1)k - 1] with detached incoming state"
      compatible_adapters:
        - ADAPTER-TBPTT-TRAINER
        - ADAPTER-STREAMING-SEQUENCE
      related_algos:
        - ALGO-NN-90
        - ALGO-NN-92
        - ALGO-NN-93
      references:
        - "https://doi.org/10.1162/neco.1990.2.4.490"
        - "https://arxiv.org/abs/1308.0850"
    ---
    """

    @staticmethod
    def train_chunk(
        x_chunk: List[List[float]],
        y_chunk_targets: List[List[float]],
        h_init: List[float],
        w_x: List[List[float]],
        w_h: List[List[float]],
        b_h: List[float],
        w_y: List[List[float]],
        b_y: List[float],
    ) -> Dict[str, Any]:
        if not x_chunk or len(x_chunk) != len(y_chunk_targets):
            raise ValueError("Precondition failed: len(input.x_chunk) == len(input.y_chunk_targets) > 0")

        k_steps = len(x_chunk)
        d_x = len(x_chunk[0])
        d_h = len(w_h)
        d_y = len(w_y)

        if len(h_init) != d_h:
            raise ValueError("Precondition failed: len(input.h_init) == d_h")

        h_states = [list(h_init)]
        y_preds = []
        chunk_loss = 0.0

        for t in range(k_steps):
            x_t = x_chunk[t]
            h_prev = h_states[-1]

            h_next = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_h[i]
                for j in range(d_h):
                    val += w_h[i][j] * h_prev[j]
                for p in range(d_x):
                    val += w_x[i][p] * x_t[p]
                h_next[i] = math.tanh(val)
            h_states.append(h_next)

            y_t = [0.0 for _ in range(d_y)]
            for o in range(d_y):
                val = b_y[o]
                for i in range(d_h):
                    val += w_y[o][i] * h_next[i]
                y_t[o] = val
            y_preds.append(y_t)

            target_t = y_chunk_targets[t]
            for o in range(d_y):
                chunk_loss += 0.5 * ((y_t[o] - target_t[o]) ** 2)

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

        return {
            "gradients": {
                "dW_x": dw_x,
                "dW_h": dw_h,
                "db_h": db_h,
                "dW_y": dw_y,
                "db_y": db_y,
            },
            "h_final": h_states[-1],
            "chunk_loss": chunk_loss,
        }
