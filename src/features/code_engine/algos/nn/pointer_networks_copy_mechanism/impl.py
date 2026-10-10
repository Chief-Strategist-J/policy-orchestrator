from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoPointerNetworksCopyMechanism:
    """
    ---
    contract:
      algo_id: ALGO-NN-99
      name: NnAlgoPointerNetworksCopyMechanism
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.pointer_networks
        - nn.copy_mechanism
        - nn.sequence
        - nn.attention
      inputs:
        type: object
        required:
          - vocab_probs
          - attention_weights
          - source_token_ids
          - context_vector
          - decoder_state
          - decoder_input_emb
          - w_c
          - w_s
          - w_x
          - b_gen
          - extended_vocab_size
        properties:
          vocab_probs:
            type: array
            items:
              type: number
            description: Fixed vocabulary generation probabilities of length V_fixed.
          attention_weights:
            type: array
            items:
              type: number
            description: Source sequence attention alignment weights of length T_x.
          source_token_ids:
            type: array
            items:
              type: integer
            description: Token indices in the source input text of length T_x.
          context_vector:
            type: array
            items:
              type: number
            description: Attention context representation vector of length d_c.
          decoder_state:
            type: array
            items:
              type: number
            description: Decoder recurrent hidden state vector of length d_s.
          decoder_input_emb:
            type: array
            items:
              type: number
            description: Embedded decoder input vector of length d_e.
          w_c:
            type: array
            items:
              type: number
            description: Linear switch weights for context vector of length d_c.
          w_s:
            type: array
            items:
              type: number
            description: Linear switch weights for decoder state of length d_s.
          w_x:
            type: array
            items:
              type: number
            description: Linear switch weights for decoder input of length d_e.
          b_gen:
            type: number
            description: Switch bias scalar.
          extended_vocab_size:
            type: integer
            description: Union vocabulary size V_ext >= V_fixed.
      outputs:
        type: object
        required:
          - final_dist
          - p_gen
        properties:
          final_dist:
            type: array
            items:
              type: number
            description: Hybrid emission distribution over extended vocabulary of length V_ext.
          p_gen:
            type: number
            description: Generation probability scalar in [0, 1].
      parameters: {}
      input_assumptions:
        - len(attention_weights) == len(source_token_ids) == T_x
        - extended_vocab_size >= len(vocab_probs)
        - parameter dimensions match respective vectors
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
          T_x: source text length
          V_ext: extended vocabulary size
          d: hidden dimensions
        time_worst: "O(T_x + V_ext + d)"
        time_typical: "O(T_x + V_ext + d)"
        space: "O(V_ext)"
      preconditions:
        - len(input.attention_weights) == len(input.source_token_ids)
        - input.extended_vocab_size >= len(input.vocab_probs)
        - len(input.w_c) == len(input.context_vector)
        - len(input.w_s) == len(input.decoder_state)
        - len(input.w_x) == len(input.decoder_input_emb)
      postconditions:
        - len(output.final_dist) == input.extended_vocab_size
        - output.p_gen >= 0.0 and output.p_gen <= 1.0
      certificate: "P(w) = p_{gen} P_{vocab}(w) + (1 - p_{gen}) \\sum_{i: x_i = w} \\alpha_{t, i}"
      compatible_adapters:
        - ADAPTER-POINTER-GENERATOR
        - ADAPTER-SUMMARIZER
      related_algos:
        - ALGO-NN-95
        - ALGO-NN-96
        - ALGO-NN-98
      references:
        - "https://arxiv.org/abs/1506.03134"
        - "https://arxiv.org/abs/1704.04368"
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
    def softmax(scores: List[float]) -> List[float]:
        max_s = max(scores)
        exps = [math.exp(s - max_s) for s in scores]
        sum_e = sum(exps)
        return [e / sum_e for e in exps]

    @staticmethod
    def compute_copy_distribution(
        vocab_probs: List[float],
        attention_weights: List[float],
        source_token_ids: List[int],
        context_vector: List[float],
        decoder_state: List[float],
        decoder_input_emb: List[float],
        w_c: List[float],
        w_s: List[float],
        w_x: List[float],
        b_gen: float,
        extended_vocab_size: int,
    ) -> Tuple[List[float], float]:
        v_fixed = len(vocab_probs)
        t_x = len(source_token_ids)

        if len(attention_weights) != t_x:
            raise ValueError(f"Precondition failed: attention length {len(attention_weights)} != source length {t_x}")
        if extended_vocab_size < v_fixed:
            raise ValueError(f"Precondition failed: extended vocab {extended_vocab_size} < fixed vocab {v_fixed}")
        if len(w_c) != len(context_vector) or len(w_s) != len(decoder_state) or len(w_x) != len(decoder_input_emb):
            raise ValueError("Precondition failed: weight vector dimensions mismatch input representations")

        raw_gen = b_gen
        for i in range(len(context_vector)):
            raw_gen += w_c[i] * context_vector[i]
        for i in range(len(decoder_state)):
            raw_gen += w_s[i] * decoder_state[i]
        for i in range(len(decoder_input_emb)):
            raw_gen += w_x[i] * decoder_input_emb[i]

        p_gen = NnAlgoPointerNetworksCopyMechanism.sigmoid(raw_gen)

        final_dist = [0.0 for _ in range(extended_vocab_size)]

        for v in range(v_fixed):
            final_dist[v] += p_gen * vocab_probs[v]

        one_minus_pgen = 1.0 - p_gen
        for i in range(t_x):
            tok_id = source_token_ids[i]
            if 0 <= tok_id < extended_vocab_size:
                final_dist[tok_id] += one_minus_pgen * attention_weights[i]

        return final_dist, p_gen

    @staticmethod
    def pointer_network_step(
        decoder_state: List[float],
        encoder_states: List[List[float]],
        w_s: List[List[float]],
        w_h: List[List[float]],
        v_a: List[float],
    ) -> List[float]:
        if not encoder_states or len(encoder_states) == 0:
            raise ValueError("Precondition failed: encoder_states must be non-empty")
        if not decoder_state or len(decoder_state) == 0:
            raise ValueError("Precondition failed: decoder_state must be non-empty")

        t_x = len(encoder_states)
        d_a = len(v_a)
        d_s = len(decoder_state)
        d_h = len(encoder_states[0])

        if len(w_s) != d_a or len(w_h) != d_a:
            raise ValueError(f"Precondition failed: projection rows must match d_a ({d_a})")
        if len(w_s[0]) != d_s or len(w_h[0]) != d_h:
            raise ValueError("Precondition failed: projection columns must match d_s and d_h")

        w_s_proj = [0.0 for _ in range(d_a)]
        for a in range(d_a):
            for k in range(d_s):
                w_s_proj[a] += w_s[a][k] * decoder_state[k]

        scores: List[float] = []
        for i in range(t_x):
            h_i = encoder_states[i]
            w_h_proj = [0.0 for _ in range(d_a)]
            for a in range(d_a):
                for j in range(d_h):
                    w_h_proj[a] += w_h[a][j] * h_i[j]

            val = 0.0
            for a in range(d_a):
                val += v_a[a] * math.tanh(w_s_proj[a] + w_h_proj[a])
            scores.append(val)

        return NnAlgoPointerNetworksCopyMechanism.softmax(scores)
