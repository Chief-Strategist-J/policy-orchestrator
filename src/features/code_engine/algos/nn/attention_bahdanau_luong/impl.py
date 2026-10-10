from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoAttentionBahdanauLuong:
    """
    ---
    contract:
      algo_id: ALGO-NN-96
      name: NnAlgoAttentionBahdanauLuong
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.attention
        - nn.bahdanau
        - nn.luong
        - nn.sequence
        - nn.alignment
      inputs:
        type: object
        required:
          - decoder_state
          - encoder_states
          - w_a
        properties:
          decoder_state:
            type: array
            items:
              type: number
            description: Decoder query state vector s_t of length d_s.
          encoder_states:
            type: array
            items:
              type: array
              items:
                type: number
            description: Encoder key/value annotation sequence H of shape (T_x, d_h).
          w_a:
            type: array
            items:
              type: array
              items:
                type: number
            description: Decoder projection matrix of shape (d_a, d_s) for Bahdanau or (d_s, d_h) for Luong.
          u_a:
            type: array
            items:
              type: array
              items:
                type: number
            description: Encoder projection matrix of shape (d_a, d_h) for Bahdanau attention.
          v_a:
            type: array
            items:
              type: number
            description: Alignment score projection vector of length d_a.
          b_a:
            type: array
            items:
              type: number
            description: Optional alignment bias vector of length d_a.
      outputs:
        type: object
        required:
          - context_vector
          - weights
        properties:
          context_vector:
            type: array
            items:
              type: number
            description: Attentive dynamic context vector c_t of length d_h.
          weights:
            type: array
            items:
              type: number
            description: Soft alignment probability distribution of length T_x.
      parameters: {}
      input_assumptions:
        - len(encoder_states) >= 1
        - dimensions of query d_s, keys d_h, and alignment d_a match respective projections
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
          T_x: source sequence length
          d_s: decoder state dimension
          d_h: encoder hidden dimension
          d_a: alignment projection dimension
        time_worst: "O(T_x * (d_a * d_h + d_a * d_s))"
        time_typical: "O(T_x * (d_a * d_h + d_a * d_s))"
        space: "O(T_x + d_h)"
      preconditions:
        - len(input.encoder_states) > 0
        - len(input.decoder_state) > 0
      postconditions:
        - len(output.context_vector) == len(input.encoder_states[0])
        - len(output.weights) == len(input.encoder_states)
      certificate: "c_t = \\sum_{i=1}^{T_x} \\alpha_{t, i} h_i and \\sum_i \\alpha_{t, i} = 1"
      compatible_adapters:
        - ADAPTER-ATTENTION-LAYER
        - ADAPTER-SEQ2SEQ-ATTN
      related_algos:
        - ALGO-NN-94
        - ALGO-NN-95
        - ALGO-NN-99
      references:
        - "https://arxiv.org/abs/1409.0473"
        - "https://arxiv.org/abs/1508.04025"
    ---
    """

    @staticmethod
    def softmax(scores: List[float]) -> List[float]:
        max_s = max(scores)
        exps = [math.exp(s - max_s) for s in scores]
        sum_e = sum(exps)
        return [e / sum_e for e in exps]

    @staticmethod
    def bahdanau_additive_attention(
        decoder_state: List[float],
        encoder_states: List[List[float]],
        w_a: List[List[float]],
        u_a: List[List[float]],
        v_a: List[float],
        b_a: Optional[List[float]] = None,
    ) -> Tuple[List[float], List[float]]:
        if not encoder_states or len(encoder_states) == 0:
            raise ValueError("Precondition failed: encoder_states must be non-empty")
        if not decoder_state or len(decoder_state) == 0:
            raise ValueError("Precondition failed: decoder_state must be non-empty")

        t_x = len(encoder_states)
        d_s = len(decoder_state)
        d_h = len(encoder_states[0])
        d_a = len(v_a)

        if len(w_a) != d_a or len(u_a) != d_a:
            raise ValueError(f"Precondition failed: projection rows must match d_a ({d_a})")
        if len(w_a[0]) != d_s or len(u_a[0]) != d_h:
            raise ValueError("Precondition failed: projection columns must match d_s and d_h")

        w_s = [0.0 for _ in range(d_a)]
        for a in range(d_a):
            val = b_a[a] if b_a is not None else 0.0
            for k in range(d_s):
                val += w_a[a][k] * decoder_state[k]
            w_s[a] = val

        raw_scores: List[float] = []
        for i in range(t_x):
            h_i = encoder_states[i]
            u_h = [0.0 for _ in range(d_a)]
            for a in range(d_a):
                val = 0.0
                for j in range(d_h):
                    val += u_a[a][j] * h_i[j]
                u_h[a] = val

            score = 0.0
            for a in range(d_a):
                score += v_a[a] * math.tanh(w_s[a] + u_h[a])
            raw_scores.append(score)

        weights = NnAlgoAttentionBahdanauLuong.softmax(raw_scores)

        context = [0.0 for _ in range(d_h)]
        for j in range(d_h):
            for i in range(t_x):
                context[j] += weights[i] * encoder_states[i][j]

        return context, weights

    @staticmethod
    def luong_multiplicative_attention(
        decoder_state: List[float],
        encoder_states: List[List[float]],
        w_a: Optional[List[List[float]]] = None,
    ) -> Tuple[List[float], List[float]]:
        if not encoder_states or len(encoder_states) == 0:
            raise ValueError("Precondition failed: encoder_states must be non-empty")
        if not decoder_state or len(decoder_state) == 0:
            raise ValueError("Precondition failed: decoder_state must be non-empty")

        t_x = len(encoder_states)
        d_s = len(decoder_state)
        d_h = len(encoder_states[0])

        raw_scores: List[float] = []
        for i in range(t_x):
            h_i = encoder_states[i]
            if w_a is not None:
                if len(w_a) != d_s or len(w_a[0]) != d_h:
                    raise ValueError("Precondition failed: w_a shape must be (d_s, d_h)")
                score = 0.0
                for r in range(d_s):
                    proj_h = 0.0
                    for c in range(d_h):
                        proj_h += w_a[r][c] * h_i[c]
                    score += decoder_state[r] * proj_h
            else:
                if d_s != d_h:
                    raise ValueError(f"Precondition failed: dot-product attention requires d_s ({d_s}) == d_h ({d_h})")
                score = sum(decoder_state[k] * h_i[k] for k in range(d_s))
            raw_scores.append(score)

        weights = NnAlgoAttentionBahdanauLuong.softmax(raw_scores)

        context = [0.0 for _ in range(d_h)]
        for j in range(d_h):
            for i in range(t_x):
                context[j] += weights[i] * encoder_states[i][j]

        return context, weights
