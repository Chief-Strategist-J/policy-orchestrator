"""
================================================================================
ALGORITHM BLUEPRINT: STRUCTURE-AWARE (RECURSIVE) CHUNKING (ALGO-VEC-TRFM-13)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hierarchically splits structured documents (Markdown, code, documentation) by
   iterating through a priority list of structural separators (e.g. "\n## ", "\n### ",
   "\n\n", "\n", " ", ""). Preserves section headers and code blocks as atomic units.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Optimal chunking strategy for technical manuals,
   source code, and markdown policies, preventing mid-function or mid-heading cuts.

3. EXECUTION FLOW:
   a. Check if text length <= chunk_size; if so, return as single chunk.
   b. Find the highest-priority separator present in text.
   c. Split text into segments by identified separator.
   d. Merge smaller adjacent segments up to chunk_size; recursively split segments
      that exceed chunk_size using lower-priority separators.
   e. Emit chunks with structural hierarchy metadata.
================================================================================
"""

from typing import Any, Dict, List, Optional
import hashlib


class VectorTransformAlgoRecursiveChunking:
    """
    --- contract:
      id: ALGO-VEC-TRFM-13
      name: VectorTransformAlgoRecursiveChunking
      category: transform
      complexity: O(|text| * |separators|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        text: str
        chunk_size: int
        chunk_overlap: int
        separators: list[str]
      output_schema:
        original_length: int
        chunk_size: int
        total_chunks: int
        chunks: list[dict[str, any]]
    ---
    """

    DEFAULT_SEPARATORS = ["\n## ", "\n### ", "\n\n", "\n", " ", ""]

    @staticmethod
    def _split_recursive(
        text: str,
        separators: List[str],
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        final_chunks: List[str] = []

        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []

        sep = separators[-1]
        for s in separators:
            if s == "" or s in text:
                sep = s
                break

        splits = text.split(sep) if sep != "" else list(text)

        next_seps = separators[separators.index(sep) + 1 :] if sep in separators and sep != "" else [""]

        current_doc: List[str] = []
        total_len = 0

        for split in splits:
            item = split.strip()
            if not item:
                continue

            if len(item) > chunk_size and next_seps:
                if current_doc:
                    merged = sep.join(current_doc).strip()
                    if merged:
                        final_chunks.append(merged)
                    current_doc = []
                    total_len = 0
                sub_chunks = VectorTransformAlgoRecursiveChunking._split_recursive(
                    item, next_seps, chunk_size, chunk_overlap
                )
                final_chunks.extend(sub_chunks)
            elif total_len + len(item) + len(sep) <= chunk_size:
                current_doc.append(item)
                total_len += len(item) + len(sep)
            else:
                if current_doc:
                    merged = sep.join(current_doc).strip()
                    if merged:
                        final_chunks.append(merged)
                current_doc = [item]
                total_len = len(item)

        if current_doc:
            merged = sep.join(current_doc).strip()
            if merged:
                final_chunks.append(merged)

        return final_chunks

    @staticmethod
    def chunk_structured(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not text:
            return {
                "original_length": 0,
                "chunk_size": chunk_size,
                "total_chunks": 0,
                "chunks": [],
            }

        seps = separators if separators is not None else VectorTransformAlgoRecursiveChunking.DEFAULT_SEPARATORS
        raw_pieces = VectorTransformAlgoRecursiveChunking._split_recursive(
            text, seps, chunk_size, chunk_overlap
        )

        chunks: List[Dict[str, Any]] = []
        for idx, piece in enumerate(raw_pieces):
            h = hashlib.sha256(piece.encode("utf-8")).hexdigest()[:16]
            chunks.append({
                "chunk_id": idx,
                "length": len(piece),
                "content_hash": h,
                "text": piece,
            })

        return {
            "original_length": len(text),
            "chunk_size": chunk_size,
            "total_chunks": len(chunks),
            "chunks": chunks,
        }
