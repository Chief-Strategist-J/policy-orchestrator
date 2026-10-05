"""
================================================================================
ALGORITHM BLUEPRINT: FRESH BUFFER (IN-MEMORY WRITE SEGMENT) (ALGO-VEC-UPD-113)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Searchable in-memory write buffer for low-latency vector ingestion. Provides
   instant read visibility via brute-force search over incoming items and automatically
   signals flush when capacity threshold is reached.

2. ARCHITECTURAL ROLE:
   Retriever & Indexer role (Layer 1). Eliminates visibility delay without triggering
   frequent expensive graph/IVF rebuilds.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoFreshBuffer:
    """
    --- contract:
      id: ALGO-VEC-UPD-113
      name: VectorUpdateAlgoFreshBuffer
      category: update
      complexity: O(B * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        buffer_records: list[dict[str, Any]]
        new_records: list[dict[str, Any]]
        max_buffer_size: int
        query_vector: Optional[list[float]]
        top_k: int
      output_schema:
        updated_buffer: list[dict[str, Any]]
        flush_required: bool
        frozen_segment: Optional[list[dict[str, Any]]]
        query_results: list[dict[str, Any]]
    ---
    """

    @staticmethod
    def _dot(a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _norm(a: List[float]) -> float:
        return math.sqrt(sum(x * x for x in a)) or 1e-12

    @classmethod
    def process(
        cls,
        buffer_records: List[Dict[str, Any]],
        new_records: List[Dict[str, Any]],
        max_buffer_size: int = 1000,
        query_vector: Optional[List[float]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        buf = list(buffer_records)
        buf.extend(new_records)

        flush_required = len(buf) >= max_buffer_size
        frozen_segment = None
        updated_buffer = buf

        if flush_required:
            frozen_segment = list(buf)
            updated_buffer = []

        results: List[Dict[str, Any]] = []
        if query_vector is not None:
            active_items = frozen_segment if frozen_segment is not None else updated_buffer
            q_norm = cls._norm(query_vector)
            scored = []
            for item in active_items:
                v = item.get("vector")
                if v and len(v) == len(query_vector):
                    score = cls._dot(query_vector, v) / (q_norm * cls._norm(v))
                    scored.append((score, item.get("id", ""), item))
            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
            for sc, rid, it in scored[:top_k]:
                results.append({"id": rid, "score": float(sc), "metadata": it.get("metadata", {})})

        return {
            "updated_buffer": updated_buffer,
            "buffer_size": len(updated_buffer),
            "flush_required": flush_required,
            "frozen_segment": frozen_segment,
            "query_results": results,
        }
