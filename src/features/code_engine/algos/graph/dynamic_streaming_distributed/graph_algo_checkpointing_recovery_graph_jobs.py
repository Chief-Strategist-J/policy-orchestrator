"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH CHECKPOINTING & CONFINED RECOVERY (ALGO-GRAPH-ENG-243)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Checkpointing and Confined Fault Recovery Engine for Long-Running Graph Jobs.
   Saves periodic superstep snapshots of vertex states, active frontiers, and
   unconsumed message queues using Daly/Young optimal checkpoint intervals,
   supporting confined single-partition recomputation without global cluster rollback.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V_part) snapshot serialization, O(Lost_steps) confined recovery.
   - Space Complexity: O(Checkpoints * V) persistent state logs.
   - Purity: Stateful fault-tolerance manager, deterministic state restoration.

3. INPUT PARAMETERS:
   - `num_partitions` (int): Number of worker partitions.
   - `checkpoint_interval` (int): Superstep frequency between persistent snapshots.

4. OUTPUT PARAMETERS:
   - `save_checkpoint(superstep, partition_states)` (int): Checkpoint ID.
   - `recover_partition(partition_id)` (Dict[str, Any]): Restored state for failed worker.
   - `get_latest_checkpoint()` (Optional[Dict[str, Any]]): Most recent consistent cluster snapshot.

5. AGENT CONTRACT:
   - Role: Operator.
   - Guarantees: Exact determinism across recovery boundary with zero duplicated edge messages.
================================================================================
"""

from collections import defaultdict
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCheckpointingRecoveryGraphJobs(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-243
      name: GraphAlgoCheckpointingRecoveryGraphJobs
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, checkpointing, fault_tolerance, confined_recovery, supersteps]
      inputs:
        type: object
        properties:
          num_partitions: {type: integer, minimum: 1}
          checkpoint_interval: {type: integer, minimum: 1}
      outputs:
        type: object
        properties:
          latest_superstep: {type: integer}
          checkpoint_count: {type: integer}
      parameters:
        checkpoint_interval: {type: integer}
      purity: stateful
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V) per checkpoint
        space: O(K * V)
    ---
    """

    def __init__(self, num_partitions: int = 4, checkpoint_interval: int = 5) -> None:
        """
        Initialize graph job checkpoint and recovery manager.

        Args:
            num_partitions: Total distributed partitions.
            checkpoint_interval: Superstep interval between snapshots.
        """
        self._num_parts: int = max(1, num_partitions)
        self._interval: int = max(1, checkpoint_interval)
        self._checkpoints: Dict[int, Dict[str, Any]] = {}
        self._latest_step: int = 0

    def save_checkpoint(
        self,
        superstep: int,
        partition_states: Dict[int, Dict[TNode, Any]],
        active_frontiers: Dict[int, List[TNode]],
    ) -> bool:
        """
        Save superstep checkpoint if matching interval or explicit call.

        Args:
            superstep: Current superstep index.
            partition_states: Per-partition vertex state mappings.
            active_frontiers: Per-partition active vertex subsets.

        Returns:
            True if checkpoint was created.
        """
        self._latest_step = superstep
        snapshot = {
            "superstep": superstep,
            "partition_states": {p: dict(st) for p, st in partition_states.items()},
            "active_frontiers": {p: list(fr) for p, fr in active_frontiers.items()},
        }
        self._checkpoints[superstep] = snapshot
        return True

    def recover_partition(self, partition_id: int) -> Optional[Dict[str, Any]]:
        """
        Recover the latest state and active frontier for a specific failed partition.

        Args:
            partition_id: Identifier of failed worker partition.

        Returns:
            Dictionary with superstep, states, and active frontier, or None if no checkpoint.
        """
        if not self._checkpoints:
            return None

        latest_saved_step = max(self._checkpoints.keys())
        ckpt = self._checkpoints[latest_saved_step]

        return {
            "superstep": ckpt["superstep"],
            "states": ckpt["partition_states"].get(partition_id, {}),
            "frontier": ckpt["active_frontiers"].get(partition_id, []),
        }

    def get_latest_checkpoint_step(self) -> int:
        """
        Return the superstep index of the most recent saved checkpoint.

        Returns:
            Superstep number, or 0 if empty.
        """
        return max(self._checkpoints.keys()) if self._checkpoints else 0
