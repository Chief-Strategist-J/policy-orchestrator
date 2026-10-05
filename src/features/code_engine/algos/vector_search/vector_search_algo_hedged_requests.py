"""
================================================================================
ALGORITHM BLUEPRINT: HEDGED REQUESTS (ALGO-VEC-SRCH-102)
================================================================================

Hedged requests curtail long tail latency in distributed retrieval by issuing a
speculative duplicate request to a backup replica if the primary replica has not
responded within a p95/p99 latency threshold. The first arriving response is returned
to the caller and the pending request is cancelled, cutting tail latency at small
marginal computational cost. Hedging is strictly restricted to read-only queries.
"""

from typing import Any, Dict, List, Optional


class VectorSearchAlgoHedgedRequests:
    """
    --- contract:
      id: ALGO-VEC-SRCH-102
      name: VectorSearchAlgoHedgedRequests
      category: vector
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        primary_latency_ms: float
        backup_latency_ms: float
        hedge_delay_threshold_ms: float
        is_read_only: bool
      output_schema:
        is_read_only: bool
        hedged_issued: bool
        winning_channel: str
        effective_latency_ms: float
        time_saved_ms: float
    ---
    """

    @staticmethod
    def evaluate_hedged_execution(
        primary_latency_ms: float,
        backup_latency_ms: float,
        hedge_delay_threshold_ms: float = 20.0,
        is_read_only: bool = True,
    ) -> Dict[str, Any]:
        if not is_read_only:
            return {
                "is_read_only": False,
                "hedged_issued": False,
                "winning_channel": "primary",
                "effective_latency_ms": primary_latency_ms,
                "time_saved_ms": 0.0,
            }

        hedged_issued = primary_latency_ms > hedge_delay_threshold_ms

        if not hedged_issued:
            winning_channel = "primary"
            effective_latency = primary_latency_ms
            time_saved = 0.0
        else:
            backup_finish_time = hedge_delay_threshold_ms + backup_latency_ms
            if backup_finish_time < primary_latency_ms:
                winning_channel = "backup"
                effective_latency = backup_finish_time
                time_saved = primary_latency_ms - backup_finish_time
            else:
                winning_channel = "primary"
                effective_latency = primary_latency_ms
                time_saved = 0.0

        return {
            "is_read_only": is_read_only,
            "hedged_issued": hedged_issued,
            "winning_channel": winning_channel,
            "effective_latency_ms": round(effective_latency, 2),
            "time_saved_ms": round(time_saved, 2),
        }
