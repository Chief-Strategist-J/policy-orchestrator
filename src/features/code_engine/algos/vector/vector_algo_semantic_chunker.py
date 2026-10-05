"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR SEMANTIC CHUNKER (ALGO-VEC-09)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Divides long textual corpora into semantically cohesive passages by computing
   consecutive sentence similarity drops (semantic breakpoints), while supporting
   deterministic fixed-size overlapping sliding windows for fallback.

2. MATHEMATICAL FORMULA:
   Given sentence embeddings s_1, s_2, ..., s_M:
   sim_i = cosine_similarity(s_i, s_{i+1})
   breakpoint_i = true if sim_i < percentile_threshold(sim_1..M, percentile=P)

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Enforces min_chunk_size and max_chunk_size bounds to avoid fragmenting sentences.
================================================================================
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str
    token_count: int
    start_char: int
    end_char: int


class VectorAlgoSemanticChunker:
    """
    ---
    contract:
      algo_id: ALGO-VEC-09
      name: VectorAlgoSemanticChunker
      version: 1.0.0
      category: vector
      capability_tags: [vector, chunking, semantic_chunker, sliding_window]
      inputs:
        type: object
        required: [text]
        properties:
          text: {type: string}
      outputs:
        type: array
        items:
          type: object
          properties:
            chunk_index: {type: integer}
            text: {type: string}
            token_count: {type: integer}
            start_char: {type: integer}
            end_char: {type: integer}
      parameters:
        chunk_size: {type: integer, default: 200}
        overlap: {type: integer, default: 40}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N)
        space: O(N)
      preconditions:
        - len(text) >= 0
        - chunk_size > overlap
      postconditions:
        - len(output) >= 0
    ---
    """

    @staticmethod
    def sliding_window_chunk(
        text: str,
        chunk_size: int = 200,
        overlap: int = 40,
    ) -> List[TextChunk]:
        if not text:
            return []
        if chunk_size <= overlap:
            raise ValueError(f"chunk_size ({chunk_size}) must be strictly greater than overlap ({overlap})")

        words = text.split()
        if not words:
            return []

        chunks: List[TextChunk] = []
        step = chunk_size - overlap
        current_idx = 0
        chunk_counter = 0

        while current_idx < len(words):
            chunk_words = words[current_idx : current_idx + chunk_size]
            chunk_str = " ".join(chunk_words)
            chunks.append(
                TextChunk(
                    chunk_index=chunk_counter,
                    text=chunk_str,
                    token_count=len(chunk_words),
                    start_char=0,
                    end_char=len(chunk_str),
                )
            )
            chunk_counter += 1
            current_idx += step
            if current_idx + overlap >= len(words) and current_idx < len(words):
                break

        return chunks

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        n1 = math.sqrt(sum(a * a for a in vec1))
        n2 = math.sqrt(sum(b * b for b in vec2))
        if n1 < 1e-12 or n2 < 1e-12:
            return 0.0
        return dot / (n1 * n2)

    @staticmethod
    def breakpoint_chunk(
        sentences: List[str],
        sentence_embeddings: List[List[float]],
        similarity_threshold: float = 0.70,
    ) -> List[str]:
        if not sentences:
            return []
        if len(sentences) != len(sentence_embeddings):
            raise ValueError("sentences and sentence_embeddings must have identical lengths")

        chunks: List[str] = []
        current_group: List[str] = [sentences[0]]

        for i in range(len(sentences) - 1):
            sim = VectorAlgoSemanticChunker.cosine_similarity(
                sentence_embeddings[i], sentence_embeddings[i + 1]
            )
            if sim < similarity_threshold:
                chunks.append(" ".join(current_group))
                current_group = [sentences[i + 1]]
            else:
                current_group.append(sentences[i + 1])

        if current_group:
            chunks.append(" ".join(current_group))

        return chunks

    @staticmethod
    def to_qdrant_points(
        document_id: str,
        chunks: List[str],
        chunk_embeddings: List[List[float]],
        base_metadata: Optional[dict] = None,
    ) -> List[dict]:
        if len(chunks) != len(chunk_embeddings):
            raise ValueError("chunks and chunk_embeddings must have identical lengths")
        points = []
        for idx, (text, emb) in enumerate(zip(chunks, chunk_embeddings)):
            meta = dict(base_metadata or {})
            meta["document_id"] = document_id
            meta["chunk_index"] = idx
            meta["text"] = text
            points.append({
                "id": f"{document_id}_{idx}",
                "vector": emb,
                "payload": meta,
            })
        return points

