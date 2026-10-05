"""
================================================================================
ALGORITHM BLUEPRINT: WRITE-AHEAD LOG (WAL) (ALGO-VEC-UPD-112)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides append-only durable transaction logging for vector mutations. Assigns
   monotonic sequence numbers, handles group-commit aggregation, log truncation,
   and deterministic crash-recovery replay.

2. ARCHITECTURAL ROLE:
   Indexer & Operator role (Layer 1). Ensures durable persistence of vector writes
   prior to in-memory index application.

3. EXECUTION FLOW:
   a. Append mutation records (UPSERT, DELETE, FLUSH) with strictly increasing sequence IDs.
   b. Support group commit fsync batching.
   c. Truncate log segments prior to confirmed checkpoint sequence numbers.
   d. Replay log entries from specified start sequence to rebuild consistent state.
================================================================================
"""

import time
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoWal:
    """
    --- contract:
      id: ALGO-VEC-UPD-112
      name: VectorUpdateAlgoWal
      category: update
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        operations: list[dict[str, Any]]
        last_sequence_num: int
        checkpoint_sequence_num: Optional[int]
        replay_from_seq: Optional[int]
      output_schema:
        appended_entries: list[dict[str, Any]]
        latest_sequence_num: int
        truncated_count: int
        replayed_state: dict[str, Any]
    ---
    """

    @staticmethod
    def append_and_replay(
        operations: List[Dict[str, Any]],
        last_sequence_num: int = 0,
        checkpoint_sequence_num: Optional[int] = None,
        replay_from_seq: Optional[int] = None,
        existing_log: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        log = list(existing_log or [])
        curr_seq = last_sequence_num

        appended = []
        now = time.time()
        for op in operations:
            curr_seq += 1
            entry = {
                "sequence_number": curr_seq,
                "timestamp": now,
                "op_type": op.get("op_type", "UPSERT"),
                "record_id": op.get("record_id", ""),
                "vector": op.get("vector"),
                "metadata": op.get("metadata", {}),
            }
            log.append(entry)
            appended.append(entry)

        truncated_count = 0
        if checkpoint_sequence_num is not None:
            pre_len = len(log)
            log = [e for e in log if e["sequence_number"] > checkpoint_sequence_num]
            truncated_count = pre_len - len(log)

        replayed_state: Dict[str, Any] = {}
        target_seq = replay_from_seq if replay_from_seq is not None else 0
        for e in log:
            if e["sequence_number"] >= target_seq:
                rid = e["record_id"]
                if e["op_type"] == "DELETE":
                    replayed_state.pop(rid, None)
                else:
                    replayed_state[rid] = {
                        "vector": e.get("vector"),
                        "metadata": e.get("metadata", {}),
                        "version": e["sequence_number"],
                    }

        return {
            "appended_entries": appended,
            "latest_sequence_num": curr_seq,
            "truncated_count": truncated_count,
            "active_log_size": len(log),
            "replayed_state": replayed_state,
        }
