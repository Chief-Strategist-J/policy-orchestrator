"""
================================================================================
ALGORITHM BLUEPRINT: TOMBSTONE RATIO & COMPACTION TRIGGER (ALGO-VEC-OBS-184)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Monitors the proportion of soft-deleted tombstone vectors across immutable segments
   and triggers compaction or graph edge repair when thresholds are exceeded.

2. MATHEMATICAL FORMULATION:
   TombstoneRatio = TotalTombstones / TotalStoredRecords
   TriggerCompaction = TombstoneRatio >= compaction_threshold_ratio
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoTombstoneRatio:
    """
    --- contract:
      id: ALGO-VEC-OBS-184
      name: VectorObservabilityAlgoTombstoneRatio
      category: observability
      complexity: O(S)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        segments: list[dict[str, Any]]
        compaction_threshold_ratio: float
      output_schema:
        total_records: int
        total_tombstones: int
        global_tombstone_ratio: float
        is_compaction_triggered: bool
        segments_needing_compaction: list[str]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        segments: List[Dict[str, Any]],
        compaction_threshold_ratio: float = 0.20,
    ) -> Dict[str, Any]:
        if not segments:
            return {
                "total_records": 0,
                "total_tombstones": 0,
                "global_tombstone_ratio": 0.0,
                "is_compaction_triggered": False,
                "segments_needing_compaction": [],
            }

        total_recs = 0
        total_tombs = 0
        compaction_needed: List[str] = []

        for seg in segments:
            s_id = seg.get("segment_id", "seg")
            rec_cnt = int(seg.get("record_count", 0))
            tomb_cnt = int(seg.get("tombstone_count", 0))
            total_recs += rec_cnt
            total_tombs += tomb_cnt

            ratio = tomb_cnt / float(rec_cnt) if rec_cnt > 0 else 0.0
            if ratio >= compaction_threshold_ratio:
                compaction_needed.append(s_id)

        global_ratio = total_tombs / float(total_recs) if total_recs > 0 else 0.0
        triggered = (global_ratio >= compaction_threshold_ratio) or (len(compaction_needed) > 0)

        return {
            "total_records": total_recs,
            "total_tombstones": total_tombs,
            "global_tombstone_ratio": round(global_ratio, 4),
            "is_compaction_triggered": triggered,
            "segments_needing_compaction": compaction_needed,
        }
