"""
================================================================================
ALGORITHM BLUEPRINT: MEAN POOLING (ALGO-VEC-TRFM-03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Aggregates token-level embeddings into a single dense vector by computing the
   element-wise average across unmasked tokens. Enforces attention mask usage to
   prevent padding tokens from biasing vector representation.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Standard pooling method for sentence-transformer
   models, outputting a fixed-dimensional vector with optional L2 normalization.

3. EXECUTION FLOW:
   a. Validate token embeddings and attention mask dimensions.
   b. Filter tokens where attention_mask == 1.
   c. Sum unmasked vectors along the sequence dimension.
   d. Divide by unmasked token count.
   e. Optionally apply L2 normalization to unit hypersphere.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoMeanPooling:
    """
    --- contract:
      id: ALGO-VEC-TRFM-03
      name: VectorTransformAlgoMeanPooling
      category: transform
      complexity: O(seq_len * hidden_dim)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_embeddings: list[list[float]]
        attention_mask: list[int]
        normalize_l2: bool
      output_schema:
        dimension: int
        unmasked_tokens: int
        pooled_vector: list[float]
    ---
    """

    @staticmethod
    def pool(
        token_embeddings: List[List[float]],
        attention_mask: Optional[List[int]] = None,
        normalize_l2: bool = True,
    ) -> Dict[str, Any]:
        if not token_embeddings:
            return {"dimension": 0, "unmasked_tokens": 0, "pooled_vector": []}

        seq_len = len(token_embeddings)
        dim = len(token_embeddings[0])

        if attention_mask is None:
            attention_mask = [1] * seq_len
        elif len(attention_mask) != seq_len:
            attention_mask = attention_mask[:seq_len] + [1] * max(0, seq_len - len(attention_mask))

        acc = [0.0] * dim
        count = 0

        for i in range(seq_len):
            if attention_mask[i] == 1:
                count += 1
                for d in range(dim):
                    acc[d] += token_embeddings[i][d]

        if count == 0:
            return {"dimension": dim, "unmasked_tokens": 0, "pooled_vector": [0.0] * dim}

        mean_vec = [acc[d] / count for d in range(dim)]

        if normalize_l2:
            norm = math.sqrt(sum(v ** 2 for v in mean_vec))
            if norm > 1e-12:
                mean_vec = [round(v / norm, 6) for v in mean_vec]
            else:
                mean_vec = [round(v, 6) for v in mean_vec]
        else:
            mean_vec = [round(v, 6) for v in mean_vec]

        return {
            "dimension": dim,
            "unmasked_tokens": count,
            "pooled_vector": mean_vec,
        }
