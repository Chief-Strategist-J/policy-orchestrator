"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SLIDING-WINDOW GRAPH MAINTENANCE (ALGO-GRAPH-STRM-211)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Sliding-Window Graph Maintenance Engine.
   Maintains dynamic graph connectivity, vertex degrees, and active topologies over
   either a time-duration window (T - W, T] or count-based FIFO window (last N edges)
   with deterministic eviction and real-time degree/subgraph querying.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Amortized O(1) per edge insertion and expiration.
   - Space Complexity: O(W) active edges and O(|V_active|) adjacency entries.
   - Purity: Stateful window manager, strictly deterministic eviction.

3. INPUT PARAMETERS:
   - `window_size` (float): Duration in seconds or count of maximum active edges.
   - `is_time_window` (bool): If True, window is temporal [t_curr - W, t_curr], else FIFO edge count.

4. OUTPUT PARAMETERS:
   - `add_edge(u, v, timestamp, weight)` (None): Inserts edge and triggers expired evictions.
   - `get_degree(u)` (int): Current window-active degree of node u.
   - `get_active_edges()` (List[Tuple[TNode, TNode, float, float]]): Active edges in window.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: All queried statistics strictly reflect valid window elements with zero stale edges.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSlidingWindowGraph(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-STRM-211
      name: GraphAlgoSlidingWindowGraph
      version: 1.0.0
      category: graph_streaming
      capability_tags: [graph, streaming, sliding_window, temporal_graph, eviction, degree_tracking]
      inputs:
        type: object
        properties:
          window_size: {type: number, minimum: 1}
          is_time_window: {type: boolean}
      outputs:
        type: object
        properties:
          active_edge_count: {type: integer}
          active_vertex_count: {type: integer}
      parameters:
        window_size: {type: number}
      purity: stateful
      determinism: deterministic
      idempotency: non_idempotent
      complexity:
        time: O(1) amortized
        space: O(W)
    ---
    """

    def __init__(self, window_size: float = 3600.0, is_time_window: bool = True) -> None:
        """
        Initialize sliding window graph container.

        Args:
            window_size: Window duration (seconds) or maximum edge count.
            is_time_window: True for time-based window, False for count-based window.
        """
        self._window_size: float = max(1.0, float(window_size))
        self._is_time_window: bool = is_time_window
        self._queue: Deque[Tuple[TNode, TNode, float, float]] = deque()
        self._adj: Dict[TNode, Dict[TNode, int]] = {}
        self._latest_time: float = 0.0

    def add_edge(self, u: TNode, v: TNode, timestamp: float = 0.0, weight: float = 1.0) -> None:
        """
        Ingest timestamped edge and evict expired records.

        Args:
            u: Source vertex.
            v: Target vertex.
            timestamp: Event arrival timestamp.
            weight: Edge attribute.
        """
        if timestamp > self._latest_time:
            self._latest_time = timestamp
        self._queue.append((u, v, timestamp, weight))
        if u not in self._adj:
            self._adj[u] = {}
        self._adj[u][v] = self._adj[u].get(v, 0) + 1
        self._evict_expired()

    def _evict_expired(self) -> None:
        if self._is_time_window:
            cutoff = self._latest_time - self._window_size
            while self._queue and self._queue[0][2] < cutoff:
                u, v, _, _ = self._queue.popleft()
                self._remove_from_adj(u, v)
        else:
            max_edges = int(self._window_size)
            while len(self._queue) > max_edges:
                u, v, _, _ = self._queue.popleft()
                self._remove_from_adj(u, v)

    def _remove_from_adj(self, u: TNode, v: TNode) -> None:
        if u in self._adj and v in self._adj[u]:
            self._adj[u][v] -= 1
            if self._adj[u][v] <= 0:
                del self._adj[u][v]
            if not self._adj[u]:
                del self._adj[u]

    def get_degree(self, u: TNode) -> int:
        """
        Get active out-degree in current window.

        Args:
            u: Target vertex.

        Returns:
            Current window degree count.
        """
        self._evict_expired()
        return sum(self._adj.get(u, {}).values())

    def get_active_edges(self) -> List[Tuple[TNode, TNode, float, float]]:
        """
        Retrieve all edges currently in the window.

        Returns:
            List of (u, v, timestamp, weight) tuples.
        """
        self._evict_expired()
        return list(self._queue)

    def get_active_vertex_count(self) -> int:
        """
        Return count of unique active vertices with active incident edges.

        Returns:
            Vertex count.
        """
        self._evict_expired()
        nodes: Set[TNode] = set()
        for u, v, _, _ in self._queue:
            nodes.add(u)
            nodes.add(v)
        return len(nodes)
