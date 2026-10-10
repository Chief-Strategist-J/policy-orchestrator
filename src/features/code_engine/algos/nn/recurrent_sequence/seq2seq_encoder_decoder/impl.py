from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


class NnAlgoSeq2SeqEncoderDecoder:
    """
    ---
    contract:
      algo_id: ALGO-NN-95
      name: NnAlgoSeq2SeqEncoderDecoder
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.seq2seq
        - nn.encoder_decoder
        - nn.sequence
        - nn.autoregressive
      inputs:
        type: object
        required:
          - x_indices
          - embedding_matrix
          - w_x
          - w_h
          - b_h
        properties:
          x_indices:
            type: array
            items:
              type: integer
            description: Input sequence token indices of length T_x.
          embedding_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: Token embedding lookup table of shape (V, d_emb).
          w_x:
            type: array
            items:
              type: array
              items:
                type: number
            description: Encoder input projection matrix of shape (d_h, d_emb).
          w_h:
            type: array
            items:
              type: array
              items:
                type: number
            description: Encoder hidden recurrent matrix of shape (d_h, d_h).
          b_h:
            type: array
            items:
              type: number
            description: Encoder hidden bias vector of length d_h.
      outputs:
        type: object
        required:
          - context_vector
          - h_states
        properties:
          context_vector:
            type: array
            items:
              type: number
            description: Summary bottleneck representation vector of length d_h.
          h_states:
            type: array
            items:
              type: array
              items:
                type: number
            description: Full encoder hidden sequence trajectory of shape (T_x, d_h).
      parameters: {}
      input_assumptions:
        - len(x_indices) >= 1
        - embedding_matrix dimension matches (V, d_emb)
        - encoder matrices conform to (d_h, d_emb) and (d_h, d_h)
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
          T_y: target sequence length
          d_emb: embedding dimension
          d_h: hidden state dimension
          V: vocabulary size
        time_worst: "O(T_x * (d_h * d_emb + d_h^2) + T_y * (d_h * d_emb + d_h^2 + V * d_h))"
        time_typical: "O(T_x * (d_h * d_emb + d_h^2) + T_y * (d_h * d_emb + d_h^2 + V * d_h))"
        space: "O(T_x * d_h + T_y)"
      preconditions:
        - len(input.x_indices) > 0
        - len(input.embedding_matrix) > 0 and len(input.embedding_matrix[0]) == len(input.w_x[0])
        - len(input.w_x) == len(input.w_h) == len(input.b_h)
      postconditions:
        - len(output.context_vector) == len(input.b_h)
        - len(output.h_states) == len(input.x_indices)
      certificate: "v = h_{T_x}^{(enc)} and s_u = \\tanh(W_s s_{u-1} + W_y y_{u-1} + b_s)"
      compatible_adapters:
        - ADAPTER-SEQ2SEQ
        - ADAPTER-NEURAL-TRANSLATION
      related_algos:
        - ALGO-NN-90
        - ALGO-NN-92
        - ALGO-NN-96
        - ALGO-NN-98
      references:
        - "https://arxiv.org/abs/1409.3215"
        - "https://arxiv.org/abs/1406.1078"
    ---
    """

    @staticmethod
    def softmax(logits: List[float]) -> List[float]:
        max_l = max(logits)
        exps = [math.exp(l - max_l) for l in logits]
        sum_e = sum(exps)
        return [e / sum_e for e in exps]

    @staticmethod
    def encode(
        x_indices: List[int],
        embedding_matrix: List[List[float]],
        w_x: List[List[float]],
        w_h: List[List[float]],
        b_h: List[float],
    ) -> Tuple[List[float], List[List[float]]]:
        if not x_indices or len(x_indices) == 0:
            raise ValueError("Precondition failed: input token sequence x_indices must be non-empty")

        t_x = len(x_indices)
        d_h = len(w_h)
        v_size = len(embedding_matrix)
        d_emb = len(embedding_matrix[0])

        if len(w_x) != d_h or len(b_h) != d_h or len(w_h[0]) != d_h:
            raise ValueError("Precondition failed: encoder weights dimension mismatch")
        if len(w_x[0]) != d_emb:
            raise ValueError("Precondition failed: w_x input dimension must match d_emb")

        h_states: List[List[float]] = []
        curr_h = [0.0 for _ in range(d_h)]

        for token_id in x_indices:
            if token_id < 0 or token_id >= v_size:
                raise ValueError(f"Precondition failed: token id {token_id} out of bounds [0, {v_size})")
            x_emb = embedding_matrix[token_id]
            next_h = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_h[i]
                for j in range(d_h):
                    val += w_h[i][j] * curr_h[j]
                for k in range(d_emb):
                    val += w_x[i][k] * x_emb[k]
                next_h[i] = math.tanh(val)
            curr_h = next_h
            h_states.append(curr_h)

        context_vector = curr_h
        return context_vector, h_states

    @staticmethod
    def decode_greedy(
        context_vector: List[float],
        embedding_matrix: List[List[float]],
        w_s: List[List[float]],
        w_y: List[List[float]],
        b_s: List[float],
        w_vocab: List[List[float]],
        b_vocab: List[float],
        bos_id: int = 1,
        eos_id: int = 2,
        max_len: int = 30,
    ) -> List[int]:
        d_h = len(context_vector)
        d_emb = len(embedding_matrix[0])
        v_size = len(w_vocab)

        if len(w_s) != d_h or len(b_s) != d_h or len(w_y) != d_h:
            raise ValueError("Precondition failed: decoder parameter dimension mismatch")
        if len(w_vocab[0]) != d_h or len(b_vocab) != v_size:
            raise ValueError("Precondition failed: emission matrix dimension mismatch")

        curr_s = list(context_vector)
        curr_token = bos_id
        generated_tokens: List[int] = []

        for _ in range(max_len):
            y_emb = embedding_matrix[curr_token]

            next_s = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_s[i]
                for j in range(d_h):
                    val += w_s[i][j] * curr_s[j]
                for k in range(d_emb):
                    val += w_y[i][k] * y_emb[k]
                next_s[i] = math.tanh(val)
            curr_s = next_s

            logits = [0.0 for _ in range(v_size)]
            for v in range(v_size):
                val = b_vocab[v]
                for i in range(d_h):
                    val += w_vocab[v][i] * curr_s[i]
                logits[v] = val

            best_token = 0
            best_logit = logits[0]
            for v in range(1, v_size):
                if logits[v] > best_logit:
                    best_logit = logits[v]
                    best_token = v

            if best_token == eos_id:
                break

            generated_tokens.append(best_token)
            curr_token = best_token

        return generated_tokens
