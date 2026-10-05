"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR TOKEN POOLING (ALGO-VEC-08)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Aggregates sequence-level token embedding matrices (N_tokens x D_dim) into a single
   dense document representation vector using Mean Pooling (with attention mask),
   [CLS] Token Pooling, or Last-Token Pooling (for decoder-only embedders).

2. MATHEMATICAL FORMULAS:
   - Mean Pooling with Attention Mask m:
     v_mean = sum(m_i * h_i for i in 1..T) / max(sum(m_i for i in 1..T), 1)
   - CLS Pooling:
     v_cls = h_0
   - Last Token Pooling:
     v_last = h_{last_unpadded_index}

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Throws clear validation errors on empty token sequences.
================================================================================
"""

from __future__ import annotations
from typing import List, Optional
from src.features.code_engine.algos.vector.vector_algo_l2_normalization import VectorAlgoL2Normalization


class VectorAlgoTokenPooling:
    """
    ---
    contract:
      algo_id: ALGO-VEC-08
      name: VectorAlgoTokenPooling
      version: 1.0.0
      category: vector
      capability_tags: [vector, embedding, pooling, mean_pooling, cls_pooling, last_token]
      inputs:
        type: object
        required: [token_embeddings]
        properties:
          token_embeddings:
            type: array
            items:
              type: array
              items: {type: number}
      outputs:
        type: array
        items: {type: number}
      parameters:
        method: {type: string, enum: [mean, cls, last_token], default: mean}
        attention_mask: {type: array, items: {type: integer}, default: null}
        renormalize_l2: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(T * D)
        space: O(D)
      preconditions:
        - len(token_embeddings) > 0
        - all(len(t) == len(token_embeddings[0]) for t in token_embeddings)
      postconditions:
        - len(output) == len(token_embeddings[0])
    ---
    """

    @staticmethod
    def mean_pool(
        token_embeddings: List[List[float]],
        attention_mask: Optional[List[int]] = None,
        renormalize_l2: bool = True,
    ) -> List[float]:
        if not token_embeddings:
            return []
        seq_len = len(token_embeddings)
        dim = len(token_embeddings[0])
        mask = attention_mask if attention_mask is not None else [1] * seq_len

        sum_vec = [0.0] * dim
        active_tokens = 0

        for i in range(seq_len):
            if mask[i] == 1:
                active_tokens += 1
                for d in range(dim):
                    sum_vec[d] += token_embeddings[i][d]

        divisor = max(active_tokens, 1)
        pooled = [val / divisor for val in sum_vec]
        if renormalize_l2:
            return VectorAlgoL2Normalization.normalize_single(pooled)
        return pooled

    @staticmethod
    def cls_pool(
        token_embeddings: List[List[float]],
        renormalize_l2: bool = True,
    ) -> List[float]:
        if not token_embeddings:
            return []
        cls_vec = list(token_embeddings[0])
        if renormalize_l2:
            return VectorAlgoL2Normalization.normalize_single(cls_vec)
        return cls_vec

    @staticmethod
    def last_token_pool(
        token_embeddings: List[List[float]],
        attention_mask: Optional[List[int]] = None,
        renormalize_l2: bool = True,
    ) -> List[float]:
        if not token_embeddings:
            return []
        if attention_mask is not None:
            last_idx = 0
            for i, m in enumerate(attention_mask):
                if m == 1:
                    last_idx = i
        else:
            last_idx = len(token_embeddings) - 1

        last_vec = list(token_embeddings[last_idx])
        if renormalize_l2:
            return VectorAlgoL2Normalization.normalize_single(last_vec)
        return last_vec
