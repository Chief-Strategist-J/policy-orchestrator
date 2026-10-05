"""
================================================================================
ALGORITHM BLUEPRINT: MVCC SNAPSHOTS AND ISOLATION (ALGO-VEC-UPD-133)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Multi-Version Concurrency Control (MVCC) isolation engine. Pins active snapshot
   versions for long-running multi-step retrieval queries, isolates concurrent writes,
   and reclaims unreferenced historical versions.
================================================================================
"""

import time
from typing import Any, Dict, List, Optional, Set


class VectorUpdateAlgoMvccSnapshots:
    """
    --- contract:
      id: ALGO-VEC-UPD-133
      name: VectorUpdateAlgoMvccSnapshots
      category: update
      complexity: O(V)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        active_versions: list[dict[str, Any]]
        pinned_version_ids: list[str]
        new_commit_version: Optional[dict[str, Any]]
        max_retention_seconds: float
      output_schema:
        visible_version: dict[str, Any]
        retained_versions: list[dict[str, Any]]
        garbage_collected_ids: list[str]
    ---
    """

    @classmethod
    def reconcile(
        cls,
        active_versions: List[Dict[str, Any]],
        pinned_version_ids: List[str],
        new_commit_version: Optional[Dict[str, Any]] = None,
        max_retention_seconds: float = 3600.0,
        current_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        now = current_time if current_time is not None else time.time()
        pinned = set(pinned_version_ids)
        all_v = list(active_versions)
        if new_commit_version:
            all_v.append(new_commit_version)

        all_v.sort(key=lambda x: x.get("commit_seq", 0), reverse=True)
        latest = all_v[0] if all_v else {"version_id": "v0", "commit_seq": 0}

        retained = []
        gc_ids = []

        for idx, v in enumerate(all_v):
            vid = v.get("version_id", "")
            v_age = now - v.get("timestamp", now)
            is_latest = (idx == 0)
            is_pinned = vid in pinned
            is_young = v_age <= max_retention_seconds

            if is_latest or is_pinned or is_young:
                retained.append(v)
            else:
                gc_ids.append(vid)

        return {
            "visible_version": latest,
            "retained_versions": retained,
            "garbage_collected_ids": gc_ids,
        }
