"""
================================================================================
ALGORITHM BLUEPRINT: BACKFILL WITH RESUMABLE CHECKPOINTS (ALGO-VEC-UPD-130)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Manages partition cursor progression and checkpoint states during long-running
   bulk ingestion tasks to guarantee seamless restart after interruptions.
================================================================================
"""

import time
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoBackfillCheckpoints:
    """
    --- contract:
      id: ALGO-VEC-UPD-130
      name: VectorUpdateAlgoBackfillCheckpoints
      category: update
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        job_id: str
        last_cursor: str
        processed_count: int
        total_count: int
        last_item_id: str
      output_schema:
        checkpoint_token: str
        percent_complete: float
        is_completed: bool
        checkpoint_metadata: dict[str, Any]
    ---
    """

    @classmethod
    def update_checkpoint(
        cls,
        job_id: str,
        last_cursor: str,
        processed_count: int,
        total_count: int,
        last_item_id: str,
    ) -> Dict[str, Any]:
        percent = (processed_count / total_count * 100.0) if total_count > 0 else 100.0
        is_done = processed_count >= total_count
        token = f"chk_{job_id}_{last_cursor}_{processed_count}"

        meta = {
            "job_id": job_id,
            "cursor": last_cursor,
            "last_item_id": last_item_id,
            "processed_count": processed_count,
            "total_count": total_count,
            "timestamp": time.time(),
        }

        return {
            "checkpoint_token": token,
            "percent_complete": round(percent, 2),
            "is_completed": is_done,
            "checkpoint_metadata": meta,
        }
