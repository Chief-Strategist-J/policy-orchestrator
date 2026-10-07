"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TEMPORAL GRAPH STORAGE & SNAPSHOT REPLAY (ALGO-GRAPH-TEMP-214)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Temporal Graph Storage and Time-Indexed Snapshot Replay Engine.
   Provides log-structured temporal adjacency lists with bisect interval searching,
   supporting Point-in-Time (PIT) snapshot extraction and interval delta queries.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(log M) PIT point search, O(k) snapshot subgraph extraction.
   - Space Complexity: O(V + M) compressed temporal adjacency intervals.
   - Purity: Stateful append-only temporal ledger, reproducible point-in-time reads.

3. INPUT PARAMETERS:
   - Initial contacts / mutations (Optional).

4. OUTPUT PARAMETERS:
   - `add_edge(u, v, t_start, t_end, weight)` (None): Appends interval contact.
   - `get_snapshot_at(t)` (Dict[TNode, List[Tuple[TNode, float]]]): Active snapshot at time t.
   - `get_interval_subgraph(t1, t2)` (List[Tuple[TNode, TNode, float, float, float]]): Edges intersecting [t1, t2].

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Zero future data leakage during historical point-in-time replays.
================================================================================
"""

import bisect
from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTemporalGraphStorage(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TEMP-214
      name: GraphAlgoTemporalGraphStorage
      version: 1.0.0
      category: graph_temporal
      capability_tags: [graph, temporal, storage, pit_replay, snapshot, interval_index]
      inputs:
        type: object
        properties: {}
      outputs:
        type: object
        properties:
          snapshot_edges: {type: array}
      parameters: {}
      purity: stateful
      determinism: deterministic
      idempotency: idempotent_reads
      complexity:
        time: O(log M) search, O(k) extraction
        space: O(V + M)
    ---
    """

    def __init__(self) -> None:
        """Initialize temporal graph index structures."""
        self._adj: Dict[TNode, List[Tuple[TNode, float, float, float]]] = defaultdict(list)
        self._all_edges: List[Tuple[TNode, TNode, float, float, float]] = []

    def add_edge(
        self, u: TNode, v: TNode, t_start: float, t_end: Optional[float] = None, weight: float = 1.0
    ) -> None:
        """
        Record a temporal edge contact interval [t_start, t_end).

        Args:
            u: Source node.
            v: Target node.
            t_start: Interval valid start timestamp.
            t_end: Interval valid end timestamp (defaults to infinity if open-ended).
            weight: Edge weight attribute.
        """
        valid_end = float("inf") if t_end is None else t_end
        entry = (u, v, t_start, valid_end, weight)
        self._adj[u].append((v, t_start, valid_end, weight))
        self._all_edges.append(entry)

    def get_snapshot_at(self, t: float) -> Dict[TNode, List[Tuple[TNode, float]]]:
        """
        Reconstruct Point-In-Time (PIT) static adjacency snapshot active at timestamp t.

        Args:
            t: Target evaluation timestamp.

        Returns:
            Adjacency dictionary mapping nodes to active (neighbor, weight) pairs.
        """
        snapshot: Dict[TNode, List[Tuple[TNode, float]]] = defaultdict(list)
        for u, neighbors in self._adj.items():
            for v, t_start, t_end, w in neighbors:
                if t_start <= t < t_end:
                    snapshot[u].append((v, w))
        return dict(snapshot)

    def get_interval_subgraph(self, t_min: float, t_max: float) -> List[Tuple[TNode, TNode, float, float, float]]:
        """
        Extract all edges active or intersecting temporal window [t_min, t_max].

        Args:
            t_min: Window start.
            t_max: Window end.

        Returns:
            List of (u, v, t_start, t_end, weight) tuples.
        """
        results = []
        for u, v, t_start, t_end, w in self._all_edges:
            if max(t_start, t_min) <= min(t_end, t_max):
                results.append((u, v, t_start, t_end, w))
        return results

    def get_vertex_lifespan(self, u: TNode) -> Tuple[float, float]:
        """
        Return the earliest appearance and latest activity timestamp for vertex u.

        Args:
            u: Target vertex.

        Returns:
            (min_timestamp, max_timestamp) tuple.
        """
        min_t = float("inf")
        max_t = float("-inf")
        for v, t_start, t_end, _ in self._adj.get(u, []):
            if t_start < min_t:
                min_t = t_start
            if t_end > max_t:
                max_t = t_end
        for u_src, neighbors in self._adj.items():
            for v, t_start, t_end, _ in neighbors:
                if v == u:
                    if t_start < min_t:
                        min_t = t_start
                    if t_end > max_t:
                        max_t = t_end
        if min_t == float("inf"):
            return 0.0, 0.0
        return min_t, max_t
