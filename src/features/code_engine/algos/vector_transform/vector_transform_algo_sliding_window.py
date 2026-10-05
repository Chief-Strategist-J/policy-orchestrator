"""
================================================================================
ALGORITHM BLUEPRINT: FIXED-SIZE SLIDING-WINDOW CHUNKING (ALGO-VEC-TRFM-11)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Partitions token sequences or words into fixed-size windows with deterministic
   overlap (stride = window_size - overlap). Emits complete provenance lineage tags
   (start_idx, end_idx, chunk_id, content_hash) satisfying Rule V1 and V4.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). The baseline text chunker guaranteeing bounded token
   counts per embedding model input window without information gaps at boundaries.

3. EXECUTION FLOW:
   a. Validate token/word sequence, window size, and overlap parameters.
   b. Calculate step stride = max(1, window_size - overlap).
   c. Slide window over sequence, gathering chunk tokens and boundary indices.
   d. Compute deterministic hash for each chunk.
   e. Return list of chunk payloads with lineage metadata.
================================================================================
"""

from typing import Any, Dict, List, Optional
import hashlib


class VectorTransformAlgoSlidingWindow:
    """
    --- contract:
      id: ALGO-VEC-TRFM-11
      name: VectorTransformAlgoSlidingWindow
      category: transform
      complexity: O(N_tokens)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        tokens: list[str]
        window_size: int
        overlap: int
        document_id: str
      output_schema:
        total_tokens: int
        window_size: int
        overlap: int
        total_chunks: int
        chunks: list[dict[str, any]]
    ---
    """

    @staticmethod
    def chunk(
        tokens: List[str],
        window_size: int = 128,
        overlap: int = 32,
        document_id: str = "doc_default",
    ) -> Dict[str, Any]:
        if not tokens:
            return {
                "total_tokens": 0,
                "window_size": window_size,
                "overlap": overlap,
                "total_chunks": 0,
                "chunks": [],
            }

        n = len(tokens)
        safe_window = max(1, window_size)
        safe_overlap = min(overlap, safe_window - 1) if safe_window > 1 else 0
        stride = max(1, safe_window - safe_overlap)

        chunks: List[Dict[str, Any]] = []
        start = 0

        while start < n:
            end = min(n, start + safe_window)
            chunk_tokens = tokens[start:end]
            chunk_text = " ".join(chunk_tokens)
            chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:16]

            chunks.append({
                "chunk_id": len(chunks),
                "document_id": document_id,
                "token_start": start,
                "token_end": end,
                "token_count": len(chunk_tokens),
                "content_hash": chunk_hash,
                "text": chunk_text,
            })

            if end >= n:
                break
            start += stride

        return {
            "total_tokens": n,
            "window_size": safe_window,
            "overlap": safe_overlap,
            "total_chunks": len(chunks),
            "chunks": chunks,
        }
