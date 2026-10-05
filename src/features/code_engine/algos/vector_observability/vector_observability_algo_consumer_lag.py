"""
================================================================================
ALGORITHM BLUEPRINT: INGESTION CONSUMER LAG & STREAM BACKLOG MONITOR (ALGO-VEC-OBS-187)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Monitors per-partition Kafka/WAL consumer lag between newest producer offset
   and consumer committed offset, isolating stuck partitions and estimating time-to-catch-up.

2. MATHEMATICAL FORMULATION:
   PartitionLag = HighWatermarkOffset - CommittedOffset
   TimeToCatchUp = PartitionLag / max(ConsumptionRate, eps)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoConsumerLag:
    """
    --- contract:
      id: ALGO-VEC-OBS-187
      name: VectorObservabilityAlgoConsumerLag
      category: observability
      complexity: O(P)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        partitions: list[dict[str, Any]]
        consumption_rate_per_sec: float
        max_acceptable_lag_records: int
      output_schema:
        total_consumer_lag_records: int
        max_partition_lag: int
        stuck_partition_ids: list[str]
        estimated_catchup_time_seconds: float
        is_backlog_critical: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        partitions: List[Dict[str, Any]],
        consumption_rate_per_sec: float = 500.0,
        max_acceptable_lag_records: int = 5000,
    ) -> Dict[str, Any]:
        if not partitions:
            return {
                "total_consumer_lag_records": 0,
                "max_partition_lag": 0,
                "stuck_partition_ids": [],
                "estimated_catchup_time_seconds": 0.0,
                "is_backlog_critical": False,
            }

        total_lag = 0
        max_lag = 0
        stuck: List[str] = []

        for p in partitions:
            p_id = str(p.get("partition_id", "p0"))
            high_watermark = int(p.get("high_watermark_offset", 0))
            committed = int(p.get("committed_offset", high_watermark))
            p_lag = max(0, high_watermark - committed)
            total_lag += p_lag

            if p_lag > max_lag:
                max_lag = p_lag

            if p_lag > max_acceptable_lag_records or bool(p.get("is_stalled", False)):
                stuck.append(p_id)

        rate = max(1.0, consumption_rate_per_sec)
        catchup_secs = total_lag / float(rate)
        is_critical = (total_lag > max_acceptable_lag_records * 2) or (len(stuck) > 0)

        return {
            "total_consumer_lag_records": total_lag,
            "max_partition_lag": max_lag,
            "stuck_partition_ids": stuck,
            "estimated_catchup_time_seconds": round(catchup_secs, 2),
            "is_backlog_critical": is_critical,
        }
