"""
================================================================================
ALGORITHM BLUEPRINT: SEMANTIC CHUNKING (ALGO-VEC-TRFM-12)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Segments document sentences into coherent semantic chunks by computing cosine
   similarities between consecutive sentence embeddings and placing cut boundaries
   where semantic distance drops below a percentile or absolute similarity threshold.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Preserves thematic coherence across variable-length
   natural topic transitions rather than arbitrary fixed token counts.

3. EXECUTION FLOW:
   a. Accept sentence texts and their corresponding vector embeddings.
   b. Compute cosine similarities between consecutive sentence vectors (s_i, s_{i+1}).
   c. Identify breakpoints where similarity < threshold or difference > percentile.
   d. Group sentences between breakpoints into distinct semantic chunks.
   e. Compute merged chunk texts and provenance lineage.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math
import hashlib


class VectorTransformAlgoSemanticChunking:
    """
    --- contract:
      id: ALGO-VEC-TRFM-12
      name: VectorTransformAlgoSemanticChunking
      category: transform
      complexity: O(N_sentences * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        sentences: list[str]
        sentence_embeddings: list[list[float]]
        similarity_threshold: float
        max_sentences_per_chunk: int
      output_schema:
        total_sentences: int
        total_chunks: int
        breakpoints: list[int]
        chunks: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x ** 2 for x in a))
        norm_b = math.sqrt(sum(y ** 2 for y in b))
        denom = norm_a * norm_b
        return dot / denom if denom > 1e-12 else 0.0

    @staticmethod
    def chunk_semantic(
        sentences: List[str],
        sentence_embeddings: List[List[float]],
        similarity_threshold: float = 0.75,
        max_sentences_per_chunk: int = 8,
    ) -> Dict[str, Any]:
        if not sentences or not sentence_embeddings:
            return {
                "total_sentences": len(sentences),
                "total_chunks": 0,
                "breakpoints": [],
                "chunks": [],
            }

        n = min(len(sentences), len(sentence_embeddings))
        breakpoints: List[int] = []

        consecutive_sims = []
        for i in range(n - 1):
            sim = VectorTransformAlgoSemanticChunking._cosine(
                sentence_embeddings[i], sentence_embeddings[i + 1]
            )
            consecutive_sims.append(sim)
            if sim < similarity_threshold:
                breakpoints.append(i + 1)

        chunks: List[Dict[str, Any]] = []
        chunk_sentences: List[str] = []
        start_idx = 0

        for i in range(n):
            chunk_sentences.append(sentences[i])
            hit_break = (i + 1) in breakpoints
            hit_limit = len(chunk_sentences) >= max_sentences_per_chunk
            is_last = i == (n - 1)

            if hit_break or hit_limit or is_last:
                text_block = " ".join(chunk_sentences)
                h = hashlib.sha256(text_block.encode("utf-8")).hexdigest()[:16]
                chunks.append({
                    "chunk_id": len(chunks),
                    "sentence_start": start_idx,
                    "sentence_end": i + 1,
                    "sentence_count": len(chunk_sentences),
                    "content_hash": h,
                    "text": text_block,
                })
                chunk_sentences = []
                start_idx = i + 1

        return {
            "total_sentences": n,
            "total_chunks": len(chunks),
            "breakpoints": breakpoints,
            "chunks": chunks,
        }
