"""Additive (Bahdanau) and Multiplicative (Luong) Recurrent Attention Mechanisms.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: attention_bahdanau_luong
  category: neural_network_architecture
  subcategory: recurrent_networks
  id: ALGO-NN-96
  equation: |
    e_{t, i}^{(\\text{Bahdanau})} = v_a^T \\tanh(W_a s_{t-1} + U_a h_i + b_a)
    e_{t, i}^{(\\text{Luong})} = s_t^T W_a h_i
    \\alpha_{t, i} = \\frac{\\exp(e_{t, i})}{\\sum_{j=1}^{T_x} \\exp(e_{t, j})}
    c_t = \\sum_{i=1}^{T_x} \\alpha_{t, i} h_i
    \\tilde{s}_t = \\tanh(W_c [c_t \\, \\| \\, s_t])
  domain:
    source_length: T_x
    encoder_hidden_dim: d_h
    decoder_hidden_dim: d_s
    alignment_dim: d_a
  properties:
    dynamic_context_synthesis: true
    soft_alignment_distribution: true
    additive_and_multiplicative_variants: true
    differentiable_memory_retrieval: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class AttentionBahdanauLuong:
    """Additive and Multiplicative Attention mechanisms for sequence models."""

    @staticmethod
    def softmax(scores: List[float]) -> List[float]:
        """Numerically stable softmax over 1D score vector."""
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
        b_a: Optional[List[float]] = None
    ) -> Tuple[List[float], List[float]]:
        """Compute Bahdanau additive attention context vector and alignment weights.

        Score formula:
          e_i = v_a^T tanh(W_a * decoder_state + U_a * encoder_states[i] + b_a)

        Args:
            decoder_state: Query vector s_{t-1} of length d_s.
            encoder_states: Key/Value sequence [T_x, d_h].
            w_a: Decoder projection matrix [d_a, d_s].
            u_a: Encoder projection matrix [d_a, d_h].
            v_a: Alignment vector of length d_a.
            b_a: Optional alignment bias of length d_a.

        Returns:
            Tuple of (context_vector of length d_h, alignment_weights of length T_x).
        """
        t_x = len(encoder_states)
        assert t_x > 0, "Encoder states cannot be empty."
        d_s = len(decoder_state)
        d_h = len(encoder_states[0])
        d_a = len(v_a)

        # Precompute projected decoder state W_a * s
        w_s = [0.0 for _ in range(d_a)]
        for a in range(d_a):
            val = b_a[a] if b_a is not None else 0.0
            for k in range(d_s):
                val += w_a[a][k] * decoder_state[k]
            w_s[a] = val

        raw_scores = []
        for i in range(t_x):
            h_i = encoder_states[i]
            # Projected encoder state U_a * h_i
            u_h = [0.0 for _ in range(d_a)]
            for a in range(d_a):
                val = 0.0
                for j in range(d_h):
                    val += u_a[a][j] * h_i[j]
                u_h[a] = val

            # Non-linear alignment: v_a^T * tanh(W_s + U_h)
            score = 0.0
            for a in range(d_a):
                score += v_a[a] * math.tanh(w_s[a] + u_h[a])
            raw_scores.append(score)

        weights = AttentionBahdanauLuong.softmax(raw_scores)

        # Compute context vector c_t = sum_i alpha_i * h_i
        context = [0.0 for _ in range(d_h)]
        for j in range(d_h):
            for i in range(t_x):
                context[j] += weights[i] * encoder_states[i][j]

        return context, weights

    @staticmethod
    def luong_multiplicative_attention(
        decoder_state: List[float],
        encoder_states: List[List[float]],
        w_a: Optional[List[List[float]]] = None
    ) -> Tuple[List[float], List[float]]:
        """Compute Luong multiplicative (general or dot-product) attention.

        Score formula:
          e_i = decoder_state^T * W_a * encoder_states[i]  (if W_a provided)
          e_i = decoder_state^T * encoder_states[i]        (dot-product if W_a is None)

        Args:
            decoder_state: Query vector s_t of length d_s.
            encoder_states: Key/Value sequence [T_x, d_h].
            w_a: Optional general alignment matrix [d_s, d_h].

        Returns:
            Tuple of (context_vector [d_h], alignment_weights [T_x]).
        """
        t_x = len(encoder_states)
        d_s = len(decoder_state)
        d_h = len(encoder_states[0])

        raw_scores = []
        for i in range(t_x):
            h_i = encoder_states[i]
            if w_a is not None:
                # s^T * W_a * h_i
                score = 0.0
                for r in range(d_s):
                    proj_h = 0.0
                    for c in range(d_h):
                        proj_h += w_a[r][c] * h_i[c]
                    score += decoder_state[r] * proj_h
            else:
                # Pure dot-product: s^T * h_i
                assert d_s == d_h, "Dot-product attention requires d_s == d_h."
                score = sum(decoder_state[k] * h_i[k] for k in range(d_s))
            raw_scores.append(score)

        weights = AttentionBahdanauLuong.softmax(raw_scores)

        context = [0.0 for _ in range(d_h)]
        for j in range(d_h):
            for i in range(t_x):
                context[j] += weights[i] * encoder_states[i][j]

        return context, weights
