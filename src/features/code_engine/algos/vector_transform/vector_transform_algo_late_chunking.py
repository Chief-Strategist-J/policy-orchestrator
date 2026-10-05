"""
================================================================================
ALGORITHM BLUEPRINT: LATE CHUNKING (ALGO-VEC-TRFM-10)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements Late Chunking where the full document is first processed through a
   long-context transformer encoder so every token attends to the entire document.
   Mean-pooling is then applied to token span boundaries to produce chunk vectors
   endowed with global document context.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Solves the context fragmentation problem inherent
   in standard naive chunk-first embedding workflows.

3. EXECUTION FLOW:
   a. Accept document-level contextual token embeddings (N_tokens x D).
   b. Accept chunk span boundaries [[start_idx, end_idx], ...].
   c. For each span, compute element-wise mean of token embeddings within [start, end).
   d. Re-normalize each chunk vector to unit L2 sphere.
   e. Return chunk vectors along with span metadata and global context indicators.
================================================================================
"""

from typing import Any, Dict, List, Optional, Tuple
import math


class VectorTransformAlgoLateChunking:
    """
    --- contract:
      id: ALGO-VEC-TRFM-10
      name: VectorTransformAlgoLateChunking
      category: transform
      complexity: O(N_tokens * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_embeddings: list[list[float]]
        chunk_spans: list[list[int]]
        normalize_l2: bool
      output_schema:
        total_tokens: int
        total_chunks: int
        chunk_vectors: list[dict[str, any]]
    ---
    """

    @staticmethod
    def chunk_late(
        token_embeddings: List[List[float]],
        chunk_spans: List[List[int]],
        normalize_l2: bool = True,
    ) -> Dict[str, Any]:
        if not token_embeddings or not chunk_spans:
            return {
                "total_tokens": len(token_embeddings),
                "total_chunks": 0,
                "chunk_vectors": [],
            }

        n_tokens = len(token_embeddings)
        dim = len(token_embeddings[0])
        chunks: List[Dict[str, Any]] = []

        for span_idx, span in enumerate(chunk_spans):
            start = max(0, span[0])
            end = min(n_tokens, span[1])

            if start >= end:
                continue

            count = end - start
            acc = [0.0] * dim

            for t in range(start, end):
                for d in range(dim):
                    acc[d] += token_embeddings[t][d]

            vec = [acc[d] / count for d in range(dim)]

            if normalize_l2:
                norm = math.sqrt(sum(v ** 2 for v in vec))
                if norm > 1e-12:
                    vec = [round(v / norm, 6) for v in vec]
                else:
                    vec = [round(v, 6) for v in vec]
            else:
                vec = [round(v, 6) for v in vec]

            chunks.append({
                "chunk_id": span_idx,
                "token_start": start,
                "token_end": end,
                "token_count": count,
                "vector": vec,
            })

        return {
            "total_tokens": n_tokens,
            "total_chunks": len(chunks),
            "chunk_vectors": chunks,
        }
