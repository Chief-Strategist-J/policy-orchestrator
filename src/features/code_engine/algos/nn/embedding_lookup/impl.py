from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoEmbeddingLookup:
    """
    ---
    contract:
      algo_id: ALGO-NN-09
      name: NnAlgoEmbeddingLookup
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.embedding
        - nn.lookup
        - nn.sparse_indexing
        - nn.bag_of_words
        - nn.padding_mask
      inputs:
        type: object
        properties:
          indices:
            type: array
            items:
              type: array
              items:
                type: integer
            description: 2D integer token/category IDs of shape (B, S) where B is batch and S is sequence length.
          embedding_table:
            type: array
            items:
              type: array
              items:
                type: number
            description: Embedding weight matrix E of shape (V, D) where V is vocabulary size and D is embedding dimension.
          padding_idx:
            type: integer
            description: Optional index representing padding tokens whose vectors are zeroed or masked.
          scale_grad_by_freq:
            type: boolean
            default: false
            description: Flag indicating if sparse gradient updates should be scaled inversely by index frequency.
          combiner:
            type: string
            enum:
              - none
              - mean
              - sum
              - sqrtn
            default: none
            description: Aggregation mode across sequence dimension S to produce fixed-size (B, D) bag embeddings.
        required:
          - indices
          - embedding_table
        additionalProperties: false
      outputs:
        type: object
        properties:
          embeddings:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Extracted 3D embeddings tensor of shape (B, S, D) when combiner is 'none'.
          pooled_embeddings:
            type: array
            items:
              type: array
              items:
                type: number
            description: Extracted 2D pooled tensor of shape (B, D) if combiner != 'none', else null.
          unique_accessed_indices:
            type: array
            items:
              type: integer
            description: Sorted unique vocabulary indices accessed during this forward pass.
          sparse_gradient_mask:
            type: array
            items:
              type: integer
            description: Binary mask of length V indicating active rows receiving non-zero backward gradients.
          vocabulary_size:
            type: integer
            description: Number of vocabulary rows V.
          embedding_dim:
            type: integer
            description: Dimension of each vector D.
        required:
          - embeddings
          - unique_accessed_indices
          - sparse_gradient_mask
          - vocabulary_size
          - embedding_dim
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - indices is a non-empty 2D array of non-negative integers
        - embedding_table is a non-empty 2D array of shape (V, D) with finite entries
        - all index values satisfy 0 <= idx < V
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: n/a
      uses_model: false
      complexity:
        variables:
          B: batch size
          S: sequence length
          D: embedding dimension
          V: vocabulary size
        time_worst: O(B * S * D)
        time_typical: O(B * S * D)
        space: O(B * S * D + V)
      preconditions:
        - len(input.indices) > 0 and len(input.indices[0]) > 0
        - len(input.embedding_table) > 0 and len(input.embedding_table[0]) > 0
        - all(0 <= idx < len(input.embedding_table) for row in input.indices for idx in row)
        - all rows in indices and embedding_table have uniform lengths
      postconditions:
        - len(output.sparse_gradient_mask) == len(input.embedding_table)
        - len(output.unique_accessed_indices) <= len(input.indices) * len(input.indices[0])
        - output.vocabulary_size == len(input.embedding_table)
        - output.embedding_dim == len(input.embedding_table[0])
      certificate: Exact row gathering from index array without floating point drift.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-03
        - ALGO-NN-10
      references:
        - mikolov2013efficient
        - vaswani2017attention
    ---
    """

    @staticmethod
    def forward(
        indices: Sequence[Sequence[int]],
        embedding_table: Sequence[Sequence[float]],
        padding_idx: Optional[int] = None,
        scale_grad_by_freq: bool = False,
        combiner: Literal["none", "mean", "sum", "sqrtn"] = "none",
    ) -> Dict[str, Any]:
        if not isinstance(indices, Sequence) or len(indices) == 0:
            raise ValueError("Precondition failed: len(input.indices) > 0")

        s = len(indices[0])
        if s == 0:
            raise ValueError("Precondition failed: len(input.indices[0]) > 0")

        b = len(indices)
        for r_idx, row in enumerate(indices):
            if not isinstance(row, Sequence) or len(row) != s:
                raise ValueError(
                    f"Precondition failed: indices row {r_idx} length {len(row)} != expected {s}"
                )

        if not isinstance(embedding_table, Sequence) or len(embedding_table) == 0:
            raise ValueError("Precondition failed: len(input.embedding_table) > 0")

        d = len(embedding_table[0])
        if d == 0:
            raise ValueError("Precondition failed: len(input.embedding_table[0]) > 0")

        v = len(embedding_table)
        for r_idx, row in enumerate(embedding_table):
            if not isinstance(row, Sequence) or len(row) != d:
                raise ValueError(
                    f"Precondition failed: embedding_table row {r_idx} length {len(row)} != expected {d}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: embedding_table[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        for r_idx, row in enumerate(indices):
            for c_idx, idx_val in enumerate(row):
                if not isinstance(idx_val, int) or idx_val < 0 or idx_val >= v:
                    raise ValueError(
                        f"Precondition failed: indices[{r_idx}][{c_idx}]={idx_val} is out of bounds [0, {v-1}]"
                    )

        if padding_idx is not None:
            if not isinstance(padding_idx, int) or padding_idx < 0 or padding_idx >= v:
                raise ValueError(
                    f"Precondition failed: padding_idx={padding_idx} out of bounds [0, {v-1}]"
                )

        embeddings_3d: List[List[List[float]]] = []
        sparse_mask: List[int] = [0] * v
        accessed_set: set[int] = set()

        for b_i in range(b):
            b_row = indices[b_i]
            seq_embeds: List[List[float]] = []
            for s_i in range(s):
                idx = b_row[s_i]
                accessed_set.add(idx)
                sparse_mask[idx] = 1

                if padding_idx is not None and idx == padding_idx:
                    vec = [0.0] * d
                else:
                    vec = [float(val) for val in embedding_table[idx]]
                seq_embeds.append(vec)
            embeddings_3d.append(seq_embeds)

        pooled_embeddings: Optional[List[List[float]]] = None
        if combiner != "none":
            pooled_embeddings = []
            for b_i in range(b):
                pool_vec: List[float] = [0.0] * d
                seq_embeds = embeddings_3d[b_i]
                valid_count = 0
                for s_i in range(s):
                    idx = indices[b_i][s_i]
                    if padding_idx is not None and idx == padding_idx:
                        continue
                    valid_count += 1
                    vec = seq_embeds[s_i]
                    for dim in range(d):
                        pool_vec[dim] += vec[dim]

                if combiner == "mean":
                    divisor = max(float(valid_count), 1.0)
                    for dim in range(d):
                        pool_vec[dim] /= divisor
                elif combiner == "sqrtn":
                    divisor = max(math.sqrt(float(valid_count)), 1.0)
                    for dim in range(d):
                        pool_vec[dim] /= divisor
                pooled_embeddings.append(pool_vec)

        unique_accessed = sorted(list(accessed_set))

        return {
            "embeddings": embeddings_3d,
            "pooled_embeddings": pooled_embeddings,
            "unique_accessed_indices": unique_accessed,
            "sparse_gradient_mask": sparse_mask,
            "vocabulary_size": v,
            "embedding_dim": d,
        }
