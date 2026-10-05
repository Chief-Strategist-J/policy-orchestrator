"""
================================================================================
ALGORITHM BLUEPRINT: QUORUM READS AND WRITES (ALGO-VEC-UPD-137)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates Strict Quorum invariants (R + W > N), performs read-repair reconciliation
   across returned replica versions, and returns the highest authoritative state.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoQuorumReadsWrites:
    """
    --- contract:
      id: ALGO-VEC-UPD-137
      name: VectorUpdateAlgoQuorumReadsWrites
      category: update
      complexity: O(R)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        total_replicas_n: int
        write_ack_count_w: int
        read_responses: list[dict[str, Any]]
      output_schema:
        is_write_quorum_met: bool
        is_strict_quorum: bool
        authoritative_record: Optional[dict[str, Any]]
        stale_replica_ids: list[str]
    ---
    """

    @classmethod
    def evaluate_quorum(
        cls,
        total_replicas_n: int,
        write_ack_count_w: int,
        read_responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        r = len(read_responses)
        w = write_ack_count_w
        n = total_replicas_n

        strict = (r + w) > n
        w_met = w >= ((n // 2) + 1)

        authoritative = None
        stale_ids = []
        if read_responses:
            sorted_resp = sorted(read_responses, key=lambda x: x.get("version", 0), reverse=True)
            authoritative = sorted_resp[0]
            max_ver = authoritative.get("version", 0)
            for resp in sorted_resp[1:]:
                if resp.get("version", 0) < max_ver:
                    stale_ids.append(resp.get("replica_id", ""))

        return {
            "is_write_quorum_met": w_met,
            "is_strict_quorum": strict,
            "authoritative_record": authoritative,
            "stale_replica_ids": [sid for sid in stale_ids if sid],
        }
