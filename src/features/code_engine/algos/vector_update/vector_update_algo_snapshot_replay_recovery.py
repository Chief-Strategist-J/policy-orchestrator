"""
================================================================================
ALGORITHM BLUEPRINT: SNAPSHOT PLUS LOG REPLAY RECOVERY (ALGO-VEC-UPD-138)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Rebuilds complete in-memory index state from base checkpoint snapshots and replays
   subsequent WAL entries in sequential order.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoSnapshotReplayRecovery:
    """
    --- contract:
      id: ALGO-VEC-UPD-138
      name: VectorUpdateAlgoSnapshotReplayRecovery
      category: update
      complexity: O(Snap + Log)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        snapshot_records: dict[str, dict[str, Any]]
        snapshot_seq: int
        wal_log: list[dict[str, Any]]
      output_schema:
        recovered_state: dict[str, dict[str, Any]]
        replayed_ops_count: int
        final_sequence_num: int
    ---
    """

    @classmethod
    def recover(
        cls,
        snapshot_records: Dict[str, Dict[str, Any]],
        snapshot_seq: int,
        wal_log: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        state = {k: dict(v) for k, v in snapshot_records.items()}
        replayed = 0
        final_seq = snapshot_seq

        sorted_wal = sorted(wal_log, key=lambda x: x.get("sequence_number", 0))
        for entry in sorted_wal:
            seq = entry.get("sequence_number", 0)
            if seq <= snapshot_seq:
                continue
            replayed += 1
            final_seq = max(final_seq, seq)
            rid = entry.get("record_id", "")
            op = entry.get("op_type", "UPSERT")

            if op == "DELETE":
                state.pop(rid, None)
            else:
                state[rid] = {
                    "vector": entry.get("vector"),
                    "metadata": entry.get("metadata", {}),
                    "version": seq,
                }

        return {
            "recovered_state": state,
            "replayed_ops_count": replayed,
            "final_sequence_num": final_seq,
            "total_records": len(state),
        }
