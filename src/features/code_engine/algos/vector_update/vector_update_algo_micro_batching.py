"""
================================================================================
ALGORITHM BLUEPRINT: STREAMING MICRO-BATCHING (ALGO-VEC-UPD-131)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Buffers streaming ingestion records into dynamic micro-batches based on item
   count and latency timeout boundaries for cost-effective batched embedding.
================================================================================
"""

import time
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoMicroBatching:
    """
    --- contract:
      id: ALGO-VEC-UPD-131
      name: VectorUpdateAlgoMicroBatching
      category: update
      complexity: O(B)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        incoming_items: list[dict[str, Any]]
        max_batch_size: int
        batch_timeout_ms: float
        oldest_buffered_timestamp: Optional[float]
      output_schema:
        batches_to_dispatch: list[list[dict[str, Any]]]
        remaining_buffer: list[dict[str, Any]]
        flush_triggered_by: str
    ---
    """

    @classmethod
    def evaluate(
        cls,
        incoming_items: List[Dict[str, Any]],
        max_batch_size: int = 32,
        batch_timeout_ms: float = 100.0,
        oldest_buffered_timestamp: Optional[float] = None,
        current_time_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        now = current_time_ms if current_time_ms is not None else time.time() * 1000.0
        batches = []
        buf = list(incoming_items)

        trigger = "NONE"
        while len(buf) >= max_batch_size:
            batches.append(buf[:max_batch_size])
            buf = buf[max_batch_size:]
            trigger = "MAX_BATCH_SIZE"

        if buf and oldest_buffered_timestamp is not None:
            if (now - oldest_buffered_timestamp) >= batch_timeout_ms:
                batches.append(buf)
                buf = []
                trigger = "TIMEOUT_EXPIRED"

        return {
            "batches_to_dispatch": batches,
            "remaining_buffer": buf,
            "flush_triggered_by": trigger,
        }
