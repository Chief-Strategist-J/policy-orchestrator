"""
================================================================================
ALGORITHM BLUEPRINT: LAST-TOKEN POOLING (ALGO-VEC-TRFM-05)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Extracts the final contextual token embedding in causal, autoregressive
   decoder-style embedding models (e.g. Mistral/Llama/Qwen embedders). Correctly
   identifies the last active non-padding token using attention mask boundaries.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Preserves causal unidirectional context accumulation
   where the rightmost token has attended to all prior tokens in the sequence.

3. EXECUTION FLOW:
   a. Validate dimensions of token embeddings and sequence attention mask.
   b. Find the index of the last non-padding token (last occurrence of mask == 1).
   c. Extract embedding vector at identified index.
   d. Optionally apply unit L2 normalization.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoLastTokenPooling:
    """
    --- contract:
      id: ALGO-VEC-TRFM-05
      name: VectorTransformAlgoLastTokenPooling
      category: transform
      complexity: O(seq_len + hidden_dim)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_embeddings: list[list[float]]
        attention_mask: list[int]
        normalize_l2: bool
      output_schema:
        dimension: int
        last_token_index: int
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
            return {"dimension": 0, "last_token_index": -1, "pooled_vector": []}

        seq_len = len(token_embeddings)
        dim = len(token_embeddings[0])

        if attention_mask is None:
            last_idx = seq_len - 1
        else:
            active_indices = [i for i, m in enumerate(attention_mask[:seq_len]) if m == 1]
            last_idx = active_indices[-1] if active_indices else seq_len - 1

        vec = list(token_embeddings[last_idx])

        if normalize_l2:
            norm = math.sqrt(sum(v ** 2 for v in vec))
            if norm > 1e-12:
                vec = [round(v / norm, 6) for v in vec]
            else:
                vec = [round(v, 6) for v in vec]
        else:
            vec = [round(v, 6) for v in vec]

        return {
            "dimension": dim,
            "last_token_index": last_idx,
            "pooled_vector": vec,
        }
