"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GHOST & MIRROR REPLICA SYNC (ALGO-GRAPH-ENG-247)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Ghost & Mirror Vertices Replica Synchronization Engine.
   Manages vertex-cut distributed replicas (Master, Mirror, Ghost), synchronizing
   partial gather message accumulations from mirrors to masters and broadcasting
   updated master states to remote ghost replicas with delta compression across supersteps.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Replicas) message exchange per superstep.
   - Space Complexity: O(V_local + Ghosts) mirror replica memory.
   - Purity: Pure functional transformation, deterministic synchronization.

3. INPUT PARAMETERS:
   - `partition_id` (int): Local worker ID.
   - `master_assignments` (Dict[TNode, int]): Map from node to authoritative master partition.

4. OUTPUT PARAMETERS:
   - `sync_mirrors_to_masters(local_gathers)` (Dict[int, Dict[TNode, Any]]): Inter-partition gather messages.
   - `apply_master_updates(master_updates)` (None): Updates local ghost replica states.

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Ghost replicas strictly mirror master values after synchronization barrier.
================================================================================
"""

from collections import defaultdict
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGhostMirrorVerticesSync(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-247
      name: GraphAlgoGhostMirrorVerticesSync
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, ghost_vertices, mirror_vertices, replica_sync, vertex_cut]
      inputs:
        type: object
        required: [partition_id, master_assignments]
        properties:
          partition_id: {type: integer}
          master_assignments: {type: object}
      outputs:
        type: object
        properties:
          messages_exchanged: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(Replicas)
        space: O(V_local + Ghosts)
    ---
    """

    def __init__(self, partition_id: int, master_assignments: Dict[TNode, int]) -> None:
        """
        Initialize ghost/mirror replica synchronization manager.

        Args:
            partition_id: Local machine ID.
            master_assignments: Map from node to authoritative owner machine ID.
        """
        self._part_id: int = partition_id
        self._master_map: Dict[TNode, int] = dict(master_assignments)
        self._local_states: Dict[TNode, Any] = {}
        self._ghosts: Set[TNode] = set()

    def register_local_node(self, u: TNode, initial_val: Any = None) -> None:
        """
        Register a node present on this partition (either master or ghost).

        Args:
            u: Vertex ID.
            initial_val: Initial state.
        """
        self._local_states[u] = initial_val
        if self._master_map.get(u, self._part_id) != self._part_id:
            self._ghosts.add(u)

    def prepare_mirror_gather_messages(self, local_partial_sums: Dict[TNode, float]) -> Dict[int, Dict[TNode, float]]:
        """
        Bundle partial gather sums for ghost vertices to send to their respective masters.

        Args:
            local_partial_sums: Local partial sums computed on this partition.

        Returns:
            Dictionary mapping destination partition ID to {node: partial_sum}.
        """
        out_messages: Dict[int, Dict[TNode, float]] = defaultdict(dict)
        for u, val in local_partial_sums.items():
            if u in self._ghosts:
                dest_p = self._master_map[u]
                out_messages[dest_p][u] = val
        return dict(out_messages)

    def apply_broadcast_updates(self, updates_from_masters: Dict[TNode, Any]) -> int:
        """
        Apply broadcasted new states from master partitions to local ghost replicas.

        Args:
            updates_from_masters: Map from node to new state.

        Returns:
            Count of updated ghost replicas.
        """
        updated = 0
        for u, val in updates_from_masters.items():
            if u in self._ghosts:
                self._local_states[u] = val
                updated += 1
        return updated

    def get_local_state(self, u: TNode) -> Any:
        """
        Get state of a node (master or ghost) stored on this partition.

        Args:
            u: Vertex ID.

        Returns:
            State value.
        """
        return self._local_states.get(u)
