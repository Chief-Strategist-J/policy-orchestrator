"""
================================================================================
ALGORITHM BLUEPRINT: REBUILD SCHEDULING (ALGO-VEC-UPD-146)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Aggregates index decay telemetry (tombstone ratio, recall decay, segment count,
   imbalance) to determine when offline index rebuilding is required.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoRebuildScheduling:
    """
    --- contract:
      id: ALGO-VEC-UPD-146
      name: VectorUpdateAlgoRebuildScheduling
      category: update
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        tombstone_ratio: float
        measured_recall: float
        target_recall: float
        segment_count: int
        unreachable_nodes_count: int
      output_schema:
        rebuild_required: bool
        triggering_reasons: list[str]
        scheduled_window: str
    ---
    """

    @classmethod
    def evaluate(
        cls,
        tombstone_ratio: float,
        measured_recall: float,
        target_recall: float = 0.90,
        segment_count: int = 4,
        unreachable_nodes_count: int = 0,
    ) -> Dict[str, Any]:
        triggers = []
        if tombstone_ratio >= 0.20:
            triggers.append(f"TOMBSTONE_RATIO_EXCEEDED ({tombstone_ratio:.2f} >= 0.20)")
        if measured_recall < (target_recall - 0.05):
            triggers.append(f"RECALL_DECAY ({measured_recall:.2f} < target {target_recall:.2f})")
        if segment_count >= 16:
            triggers.append(f"FRAGMENTED_SEGMENTS ({segment_count} >= 16)")
        if unreachable_nodes_count > 50:
            triggers.append(f"GRAPH_FRAGMENTATION ({unreachable_nodes_count} dead-end nodes)")

        rebuild = len(triggers) > 0

        return {
            "rebuild_required": rebuild,
            "triggering_reasons": triggers,
            "scheduled_window": "OFF_PEAK_0200_UTC" if rebuild else "NONE",
        }
