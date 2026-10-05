"""
================================================================================
ALGORITHM BLUEPRINT: LEADER-FOLLOWER REPLICATION (ALGO-VEC-UPD-135)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Streams replication logs from leader node to follower replicas, tracks per-replica
   sequence lag, and dynamically routes read requests to in-sync followers.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoLeaderFollower:
    """
    --- contract:
      id: ALGO-VEC-UPD-135
      name: VectorUpdateAlgoLeaderFollower
      category: update
      complexity: O(R)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        leader_sequence_num: int
        followers: list[dict[str, Any]]
        max_tolerable_lag: int
      output_schema:
        in_sync_followers: list[str]
        lagging_followers: list[dict[str, Any]]
        eligible_read_replicas: list[str]
        replication_health: str
    ---
    """

    @classmethod
    def evaluate_replicas(
        cls,
        leader_sequence_num: int,
        followers: List[Dict[str, Any]],
        max_tolerable_lag: int = 2,
    ) -> Dict[str, Any]:
        in_sync = []
        lagging = []
        eligible = []

        for f in followers:
            fid = f.get("replica_id", "")
            f_seq = f.get("sequence_num", 0)
            lag = max(0, leader_sequence_num - f_seq)
            if lag == 0:
                in_sync.append(fid)
                eligible.append(fid)
            elif lag <= max_tolerable_lag:
                eligible.append(fid)
                lagging.append({"replica_id": fid, "lag": lag})
            else:
                lagging.append({"replica_id": fid, "lag": lag})

        health = "HEALTHY"
        if len(in_sync) == 0:
            health = "DEGRADED"
        if len(eligible) == 0:
            health = "CRITICAL"

        return {
            "in_sync_followers": in_sync,
            "lagging_followers": lagging,
            "eligible_read_replicas": eligible,
            "replication_health": health,
        }
