"""
================================================================================
ALGORITHM BLUEPRINT: BACKPRESSURE AND PRIORITIZED INGESTION (ALGO-VEC-UPD-132)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Prioritizes mutation queues (DELETES > LIVE_UPDATES > BACKFILL) and enforces
   load-shedding / backpressure when buffer limits are exceeded.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoBackpressurePriority:
    """
    --- contract:
      id: ALGO-VEC-UPD-132
      name: VectorUpdateAlgoBackpressurePriority
      category: update
      complexity: O(Q log Q)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        queue_items: list[dict[str, Any]]
        max_queue_capacity: int
        drain_limit: int
      output_schema:
        drained_items: list[dict[str, Any]]
        remaining_queue_size: int
        backpressure_active: bool
        dropped_items_count: int
    ---
    """

    PRIORITY_MAP = {
        "DELETE": 1,
        "LIVE_UPDATE": 2,
        "BACKFILL": 3,
    }

    @classmethod
    def process_queue(
        cls,
        queue_items: List[Dict[str, Any]],
        max_queue_capacity: int = 1000,
        drain_limit: int = 50,
    ) -> Dict[str, Any]:
        sorted_items = sorted(
            queue_items,
            key=lambda x: (
                cls.PRIORITY_MAP.get(x.get("type", "BACKFILL").upper(), 4),
                x.get("enqueue_time", 0),
            )
        )

        dropped_count = 0
        if len(sorted_items) > max_queue_capacity:
            excess = len(sorted_items) - max_queue_capacity
            sorted_items = sorted_items[:-excess]
            dropped_count = excess

        drained = sorted_items[:drain_limit]
        remaining = sorted_items[drain_limit:]
        backpressure = len(remaining) > (max_queue_capacity * 0.8)

        return {
            "drained_items": drained,
            "remaining_queue_size": len(remaining),
            "backpressure_active": backpressure,
            "dropped_items_count": dropped_count,
        }
