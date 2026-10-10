"""Sequence-to-Sequence (Seq2Seq) Encoder-Decoder Architecture and Autoregressive Decoding.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: seq2seq_encoder_decoder
  category: neural_network_architecture
  subcategory: sequence_models
  id: ALGO-NN-95
  equation: |
    h_t^{(\\text{enc})} = \\tanh(W_h^{(\\text{enc})} h_{t-1}^{(\\text{enc})} + W_x^{(\\text{enc})} x_t + b_h^{(\\text{enc})})
    v = h_{T_x}^{(\\text{enc})}
    s_u = \\tanh(W_s^{(\\text{dec})} s_{u-1} + W_y^{(\\text{dec})} y_{u-1} + b_s^{(\\text{dec})}) \\quad \\text{with } s_0 = v
    P(y_u = k \\mid y_{<u}, \\mathbf{x}) = \\frac{\\exp(W_v[k] s_u + b_v[k])}{\\sum_j \\exp(W_v[j] s_u + b_v[j])}
  domain:
    input_length: T_x
    output_length: T_y
    vocabulary_size: V
    hidden_dimension: d_h
  properties:
    variable_length_mapping: true
    autoregressive_causal_decoding: true
    bottleneck_context_transfer: true
    bos_eos_token_control: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class Seq2SeqEncoderDecoder:
    """Seq2Seq Recurrent Encoder-Decoder with greedy and teacher-forcing rollout routines."""

    @staticmethod
    def softmax(logits: List[float]) -> List[float]:
        """Numerically stable softmax."""
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
        b_h: List[float]
    ) -> Tuple[List[float], List[List[float]]]:
        """Encode input sequence into final context vector and step representations.

        Args:
            x_indices: List of integer token IDs of length T_x.
            embedding_matrix: Table [V, d_emb].
            w_x: Input projection [d_h, d_emb].
            w_h: Recurrent weights [d_h, d_h].
            b_h: Bias vector [d_h].

        Returns:
            Tuple of (context_vector [d_h], encoder_states [T_x, d_h]).
        """
        t_x = len(x_indices)
        assert t_x > 0, "Input sequence cannot be empty."
        d_h = len(w_h)
        d_emb = len(embedding_matrix[0])

        h_states = []
        curr_h = [0.0 for _ in range(d_h)]

        for token_id in x_indices:
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
        max_len: int = 30
    ) -> List[int]:
        """Autoregressively decode tokens using greedy maximum-likelihood selection.

        Args:
            context_vector: Initial state s_0 of length d_h from encoder.
            embedding_matrix: Table [V, d_emb].
            w_s: Decoder hidden-to-hidden weights [d_h, d_h].
            w_y: Decoder embedding-to-hidden weights [d_h, d_emb].
            b_s: Decoder hidden bias [d_h].
            w_vocab: Emission matrix [V, d_h].
            b_vocab: Emission bias [V].
            bos_id: Beginning-of-sequence token ID.
            eos_id: End-of-sequence token ID.
            max_len: Maximum generated sequence length.

        Returns:
            List of generated token IDs (excluding BOS, terminating at EOS).
        """
        d_h = len(context_vector)
        d_emb = len(embedding_matrix[0])
        v_size = len(w_vocab)

        curr_s = list(context_vector)
        curr_token = bos_id
        generated_tokens = []

        for _ in range(max_len):
            # 1. Embed current token
            y_emb = embedding_matrix[curr_token]

            # 2. Advance decoder recurrent state: s_u = tanh(W_s s_{u-1} + W_y y_{u-1} + b_s)
            next_s = [0.0 for _ in range(d_h)]
            for i in range(d_h):
                val = b_s[i]
                for j in range(d_h):
                    val += w_s[i][j] * curr_s[j]
                for k in range(d_emb):
                    val += w_y[i][k] * y_emb[k]
                next_s[i] = math.tanh(val)
            curr_s = next_s

            # 3. Vocabulary emission logits: z = W_vocab * s_u + b_vocab
            logits = [0.0 for _ in range(v_size)]
            for v in range(v_size):
                val = b_vocab[v]
                for i in range(d_h):
                    val += w_vocab[v][i] * curr_s[i]
                logits[v] = val

            # 4. Argmax greedy token selection
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
