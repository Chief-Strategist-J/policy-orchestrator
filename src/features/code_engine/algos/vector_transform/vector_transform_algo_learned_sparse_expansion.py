"""
================================================================================
ALGORITHM BLUEPRINT: LEARNED SPARSE EXPANSION (SPLADE) (ALGO-VEC-TRFM-32)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Transforms token representations into sparse vocabulary-space vectors using
   SPLADE-style log-saturation and max-pooling (Formal et al.):
   w_j = max_{t ∈ sequence} log(1 + ReLU(W_v · h_t + b_v)_j).
   Produces sparse lexical term weights enabling inverted index search while
   benefiting from deep neural synonym expansion.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Bridges dense semantic reasoning to Lucene/inverted-index
   sparse inverted postings lists with zero loss of lexical exact-match guarantees.

3. EXECUTION FLOW:
   a. Accept token embeddings sequence (N_tokens x D) and vocabulary projection head.
   b. Compute linear logit projection to vocabulary dimension.
   c. Apply ReLU activation followed by log(1 + x) saturation.
   d. Max-pool across all token positions for each vocabulary term.
   e. Threshold values below min_weight to preserve extreme sparsity.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoLearnedSparseExpansion:
    """
    --- contract:
      id: ALGO-VEC-TRFM-32
      name: VectorTransformAlgoLearnedSparseExpansion
      category: transform
      complexity: O(seq_len * D * V_sample)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_embeddings: list[list[float]]
        vocab_tokens: list[str]
        projection_matrix: list[list[float]]
        min_weight_threshold: float
      output_schema:
        sequence_length: int
        non_zero_terms: int
        sparse_weights: dict[str, float]
    ---
    """

    @staticmethod
    def expand_sparse(
        token_embeddings: List[List[float]],
        vocab_tokens: Optional[List[str]] = None,
        projection_matrix: Optional[List[List[float]]] = None,
        min_weight_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        if not token_embeddings:
            return {
                "sequence_length": 0,
                "non_zero_terms": 0,
                "sparse_weights": {},
            }

        seq_len = len(token_embeddings)
        d = len(token_embeddings[0])

        if vocab_tokens is None:
            vocab_tokens = [f"term_{i}" for i in range(16)]
        v_size = len(vocab_tokens)

        if projection_matrix is None:
            projection_matrix = [
                [math.sin((t + 1) * (i + 1) * 0.1) * 0.1 for i in range(d)]
                for t in range(v_size)
            ]

        max_weights: Dict[str, float] = {token: 0.0 for token in vocab_tokens}

        for token_vec in token_embeddings:
            for v_idx, token_name in enumerate(vocab_tokens):
                logit = sum(
                    projection_matrix[v_idx][i] * token_vec[i]
                    for i in range(min(d, len(projection_matrix[v_idx])))
                )
                relu_val = max(0.0, logit)
                weight = math.log1p(relu_val)
                if weight > max_weights[token_name]:
                    max_weights[token_name] = weight

        filtered_weights = {
            t: round(w, 4)
            for t, w in max_weights.items()
            if w >= min_weight_threshold
        }

        return {
            "sequence_length": seq_len,
            "non_zero_terms": len(filtered_weights),
            "sparse_weights": filtered_weights,
        }
