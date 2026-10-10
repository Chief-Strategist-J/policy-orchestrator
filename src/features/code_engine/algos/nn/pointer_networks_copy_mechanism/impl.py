"""Pointer Networks and Pointer-Generator Copy Mechanism.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: pointer_networks_copy_mechanism
  category: neural_network_architecture
  subcategory: sequence_models
  id: ALGO-NN-99
  equation: |
    p_{\\text{gen}} = \\sigma(w_c^T c_t + w_s^T s_t + w_x^T x_t + b_{\\text{gen}})
    P(w) = p_{\\text{gen}} P_{\\text{vocab}}(w) + (1 - p_{\\text{gen}}) \\sum_{i: x_i = w} \\alpha_{t, i}
    \\alpha_{t, i} = \\frac{\\exp(v^T \\tanh(W_s s_t + W_h h_i))}{\\sum_j \\exp(v^T \\tanh(W_s s_t + W_h h_j))}
  domain:
    fixed_vocab_size: V
    source_sequence_length: T_x
    generation_probability: "p_gen \\in [0, 1]"
  properties:
    out_of_vocabulary_copying: true
    hybrid_generative_extractive: true
    variable_length_output_pointing: true
    differentiable_soft_switching: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class PointerNetworksCopyMechanism:
    """Pointer Network and Pointer-Generator Copy Mechanism Engine."""

    @staticmethod
    def sigmoid(x: float) -> float:
        """Stable scalar sigmoid function."""
        if x >= 0:
            z = math.exp(-x)
            return 1.0 / (1.0 + z)
        else:
            z = math.exp(x)
            return z / (1.0 + z)

    @staticmethod
    def softmax(scores: List[float]) -> List[float]:
        """Stable softmax over 1D array."""
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
        extended_vocab_size: int
    ) -> Tuple[List[float], float]:
        """Compute the hybrid pointer-generator token emission distribution.

        Args:
            vocab_probs: Fixed-vocabulary probability distribution of length V_fixed.
            attention_weights: Attention distribution alpha over source tokens of length T_x.
            source_token_ids: Sequence of token IDs in source text of length T_x.
            context_vector: Attention context vector of length d_c.
            decoder_state: Decoder hidden state of length d_s.
            decoder_input_emb: Embedded decoder input of length d_e.
            w_c, w_s, w_x, b_gen: Parameters for p_gen scalar calculation.
            extended_vocab_size: Total vocabulary size V_ext >= V_fixed.

        Returns:
            Tuple of (final_probability_distribution of length extended_vocab_size, p_gen).
        """
        v_fixed = len(vocab_probs)
        t_x = len(source_token_ids)
        assert len(attention_weights) == t_x
        assert extended_vocab_size >= v_fixed

        # 1. Compute p_gen = sigmoid(w_c^T c + w_s^T s + w_x^T x + b_gen)
        raw_gen = b_gen
        for i in range(len(context_vector)):
            raw_gen += w_c[i] * context_vector[i]
        for i in range(len(decoder_state)):
            raw_gen += w_s[i] * decoder_state[i]
        for i in range(len(decoder_input_emb)):
            raw_gen += w_x[i] * decoder_input_emb[i]

        p_gen = PointerNetworksCopyMechanism.sigmoid(raw_gen)

        # 2. Allocate extended probability vector
        final_dist = [0.0 for _ in range(extended_vocab_size)]

        # 3. Add generated vocabulary contributions: p_gen * P_vocab(w)
        for v in range(v_fixed):
            final_dist[v] += p_gen * vocab_probs[v]

        # 4. Add copied attention contributions: (1 - p_gen) * sum_{i: src_i == w} alpha_i
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
        v_a: List[float]
    ) -> List[float]:
        """Pure Pointer Network: output distribution directly points to source sequence positions.

        Args:
            decoder_state: Decoder query s_t of length d_s.
            encoder_states: Source annotations [T_x, d_h].
            w_s: Decoder alignment weights [d_a, d_s].
            w_h: Encoder alignment weights [d_a, d_h].
            v_a: Alignment scoring vector [d_a].

        Returns:
            Probability distribution over source positions of length T_x.
        """
        t_x = len(encoder_states)
        d_a = len(v_a)
        d_s = len(decoder_state)
        d_h = len(encoder_states[0])

        w_s_proj = [0.0 for _ in range(d_a)]
        for a in range(d_a):
            for k in range(d_s):
                w_s_proj[a] += w_s[a][k] * decoder_state[k]

        scores = []
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

        return PointerNetworksCopyMechanism.softmax(scores)
