"""
================================================================================
ALGORITHM BLUEPRINT: ORPHAN GARBAGE COLLECTION (ALGO-VEC-UPD-144)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Identifies and purges index vectors whose upstream source documents have been
   deleted, enforcing safety guardrails to stop execution if orphan ratios are abnormal.
================================================================================
"""

from typing import Any, Dict, List, Optional, Set


class VectorUpdateAlgoOrphanGc:
    """
    --- contract:
      id: ALGO-VEC-UPD-144
      name: VectorUpdateAlgoOrphanGc
      category: update
      complexity: O(V + S)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        index_vectors: list[dict[str, Any]]
        authoritative_source_ids: list[str]
        safety_max_orphan_ratio: float
      output_schema:
        orphan_vector_ids: list[str]
        orphan_ratio: float
        safety_guardrail_triggered: bool
        action_permitted: bool
    ---
    """

    @classmethod
    def identify_orphans(
        cls,
        index_vectors: List[Dict[str, Any]],
        authoritative_source_ids: List[str],
        safety_max_orphan_ratio: float = 0.15,
    ) -> Dict[str, Any]:
        valid_sources: Set[str] = set(authoritative_source_ids)
        orphans = []

        for vec in index_vectors:
            sid = vec.get("source_id", "")
            vid = vec.get("id", "")
            if sid not in valid_sources:
                orphans.append(vid)

        total = len(index_vectors)
        ratio = (len(orphans) / total) if total > 0 else 0.0
        guardrail = ratio > safety_max_orphan_ratio

        return {
            "orphan_vector_ids": sorted(orphans),
            "orphan_ratio": round(ratio, 4),
            "safety_guardrail_triggered": guardrail,
            "action_permitted": not guardrail,
        }
