"""
================================================================================
ALGORITHM BLUEPRINT: DUAL-WRITE SHADOW INDEX (ALGO-VEC-UPD-122)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Replicates live mutation events simultaneously to primary and shadow indexes.
   Maintains retry buffers for asynchronous divergence and reconciles ID sets.
================================================================================
"""

from typing import Any, Dict, List, Optional, Set


class VectorUpdateAlgoDualWrite:
    """
    --- contract:
      id: ALGO-VEC-UPD-122
      name: VectorUpdateAlgoDualWrite
      category: update
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        mutation_events: list[dict[str, Any]]
        primary_ids: list[str]
        shadow_ids: list[str]
        simulate_shadow_failure_rate: float
      output_schema:
        primary_written: list[str]
        shadow_written: list[str]
        shadow_retry_buffer: list[dict[str, Any]]
        divergent_ids: list[str]
        is_converged: bool
    ---
    """

    @classmethod
    def dispatch(
        cls,
        mutation_events: List[Dict[str, Any]],
        primary_ids: List[str],
        shadow_ids: List[str],
        simulate_shadow_failure_rate: float = 0.0,
    ) -> Dict[str, Any]:
        prim_set: Set[str] = set(primary_ids)
        shad_set: Set[str] = set(shadow_ids)
        prim_written: List[str] = []
        shad_written: List[str] = []
        retry_buf: List[Dict[str, Any]] = []

        for idx, ev in enumerate(mutation_events):
            rid = ev.get("record_id", "")
            op = ev.get("op_type", "UPSERT")
            if op == "DELETE":
                prim_set.discard(rid)
            else:
                prim_set.add(rid)
            prim_written.append(rid)

            is_fail = (idx % 10) < int(simulate_shadow_failure_rate * 10) if simulate_shadow_failure_rate > 0 else False
            if is_fail:
                retry_buf.append(ev)
            else:
                if op == "DELETE":
                    shad_set.discard(rid)
                else:
                    shad_set.add(rid)
                shad_written.append(rid)

        divergent = list(prim_set.symmetric_difference(shad_set))

        return {
            "primary_written": prim_written,
            "shadow_written": shad_written,
            "shadow_retry_buffer": retry_buf,
            "divergent_ids": sorted(divergent),
            "is_converged": len(divergent) == 0,
        }
