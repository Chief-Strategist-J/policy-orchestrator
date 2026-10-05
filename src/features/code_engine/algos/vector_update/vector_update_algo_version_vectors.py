"""
================================================================================
ALGORITHM BLUEPRINT: VERSION VECTORS AND CONFLICT DETECTION (ALGO-VEC-UPD-140)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tracks per-replica version vectors to determine causal order between vector
   mutations, detecting concurrent updates and triggering re-embedding reconciliation.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoVersionVectors:
    """
    --- contract:
      id: ALGO-VEC-UPD-140
      name: VectorUpdateAlgoVersionVectors
      category: update
      complexity: O(Replicas)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector_a: dict[str, int]
        vector_b: dict[str, int]
      output_schema:
        causal_relationship: str
        is_conflict: bool
        merged_vector: dict[str, int]
    ---
    """

    @classmethod
    def compare_and_merge(
        cls,
        vector_a: Dict[str, int],
        vector_b: Dict[str, int],
    ) -> Dict[str, Any]:
        all_replicas = set(vector_a.keys()).union(vector_b.keys())

        a_dominates = False
        b_dominates = False

        for r in all_replicas:
            va = vector_a.get(r, 0)
            vb = vector_b.get(r, 0)
            if va > vb:
                a_dominates = True
            elif vb > va:
                b_dominates = True

        rel = "IDENTICAL"
        conflict = False

        if a_dominates and not b_dominates:
            rel = "A_DOMINATES_B"
        elif b_dominates and not a_dominates:
            rel = "B_DOMINATES_A"
        elif a_dominates and b_dominates:
            rel = "CONCURRENT_CONFLICT"
            conflict = True

        merged = {r: max(vector_a.get(r, 0), vector_b.get(r, 0)) for r in all_replicas}

        return {
            "causal_relationship": rel,
            "is_conflict": conflict,
            "merged_vector": merged,
        }
