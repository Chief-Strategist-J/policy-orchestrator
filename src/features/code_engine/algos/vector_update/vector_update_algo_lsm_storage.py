"""
================================================================================
ALGORITHM BLUEPRINT: SEGMENT-BASED LSM VECTOR STORAGE (ALGO-VEC-UPD-114)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Manages immutable vector segments organized in hierarchical LSM tiers. Dispatches
   multi-segment queries, evaluates deletion bitmaps, and computes segment fragmentation.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoLsmStorage:
    """
    --- contract:
      id: ALGO-VEC-UPD-114
      name: VectorUpdateAlgoLsmStorage
      category: update
      complexity: O(S * N_seg * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        segments: list[dict[str, Any]]
        query_vector: Optional[list[float]]
        top_k: int
      output_schema:
        total_segments: int
        total_live_vectors: int
        total_tombstones: int
        fragmentation_ratio: float
        recommend_compaction: bool
        merged_results: list[dict[str, Any]]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        segments: List[Dict[str, Any]],
        query_vector: Optional[List[float]] = None,
        top_k: int = 10,
        fragmentation_threshold: float = 0.25,
    ) -> Dict[str, Any]:
        total_live = 0
        total_tomb = 0
        all_candidates: List[Dict[str, Any]] = []

        q_norm = 1.0
        if query_vector:
            q_norm = math.sqrt(sum(x * x for x in query_vector)) or 1e-12

        for seg in segments:
            tombstones = set(seg.get("tombstone_ids", []))
            records = seg.get("records", [])
            for r in records:
                rid = r.get("id", "")
                if rid in tombstones:
                    total_tomb += 1
                    continue
                total_live += 1
                if query_vector and "vector" in r:
                    v = r["vector"]
                    if len(v) == len(query_vector):
                        dot = sum(x * y for x, y in zip(query_vector, v))
                        v_norm = math.sqrt(sum(x * x for x in v)) or 1e-12
                        sim = dot / (q_norm * v_norm)
                        all_candidates.append({"id": rid, "score": float(sim), "segment_id": seg.get("segment_id"), "metadata": r.get("metadata", {})})

        total_v = total_live + total_tomb
        frag_ratio = (total_tomb / total_v) if total_v > 0 else 0.0
        recommend_compaction = frag_ratio >= fragmentation_threshold or len(segments) >= 8

        all_candidates.sort(key=lambda x: (x["score"], x["id"]), reverse=True)

        return {
            "total_segments": len(segments),
            "total_live_vectors": total_live,
            "total_tombstones": total_tomb,
            "fragmentation_ratio": round(frag_ratio, 4),
            "recommend_compaction": recommend_compaction,
            "merged_results": all_candidates[:top_k],
        }
