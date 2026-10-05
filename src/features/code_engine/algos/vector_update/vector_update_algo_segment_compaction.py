"""
================================================================================
ALGORITHM BLUEPRINT: SEGMENT MERGE AND COMPACTION (ALGO-VEC-UPD-115)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Merges selected immutable vector segments, permanently purges tombstoned records,
   re-indexes surviving vectors, and returns clean unified target segments.
================================================================================
"""

import time
import uuid
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoSegmentCompaction:
    """
    --- contract:
      id: ALGO-VEC-UPD-115
      name: VectorUpdateAlgoSegmentCompaction
      category: update
      complexity: O(sum(N_i))
      pure_function: true
      zero_inline_comments: true
      input_schema:
        segments_to_merge: list[dict[str, Any]]
        target_tier: str
      output_schema:
        new_segment: dict[str, Any]
        dropped_tombstones: int
        surviving_vectors: int
        reclaimed_ratio: float
        old_segment_ids: list[str]
    ---
    """

    @classmethod
    def compact(
        cls,
        segments_to_merge: List[Dict[str, Any]],
        target_tier: str = "L1",
    ) -> Dict[str, Any]:
        surviving: Dict[str, Dict[str, Any]] = {}
        all_tombstones: set = set()
        old_ids = []
        initial_vector_count = 0

        for seg in sorted(segments_to_merge, key=lambda s: s.get("created_at", 0)):
            seg_id = seg.get("segment_id", str(uuid.uuid4()))
            old_ids.append(seg_id)
            tombs = set(seg.get("tombstone_ids", []))
            all_tombstones.update(tombs)

            records = seg.get("records", [])
            initial_vector_count += len(records)
            for r in records:
                rid = r.get("id")
                if rid:
                    surviving[rid] = r

        for t in all_tombstones:
            surviving.pop(t, None)

        surviving_records = list(surviving.values())
        dropped_count = initial_vector_count - len(surviving_records)
        reclaimed = (dropped_count / initial_vector_count) if initial_vector_count > 0 else 0.0

        new_segment = {
            "segment_id": f"seg_{target_tier.lower()}_{uuid.uuid4().hex[:8]}",
            "tier": target_tier,
            "created_at": time.time(),
            "records": surviving_records,
            "tombstone_ids": [],
            "record_count": len(surviving_records),
        }

        return {
            "new_segment": new_segment,
            "dropped_tombstones": dropped_count,
            "surviving_vectors": len(surviving_records),
            "reclaimed_ratio": round(reclaimed, 4),
            "old_segment_ids": old_ids,
        }
