"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DIRECTION-OPTIMIZING FRONTIER SWITCHING (ALGO-GRAPH-PAR-222)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Direction-Optimizing Dynamic Frontier Representation Switching Engine.
   Dynamically switches between sparse vertex list representation (for low-density
   push steps) and dense bitset / boolean array representation (for high-density
   pull steps) based on active frontier volume thresholds, minimizing memory bandwidth.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|Frontier|) in sparse mode, O(V + M) in dense mode.
   - Space Complexity: O(V) bitmap and frontier buffers.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Forward graph adjacency.
   - `transpose_adjacency` (Optional[Dict[TNode, List[TNode]]]): Reverse graph adjacency for pull steps.
   - `alpha` (float): Threshold parameter for sparse-to-dense transition.
   - `beta` (float): Threshold parameter for dense-to-sparse transition.

4. OUTPUT PARAMETERS:
   - `run_bfs(source)` (Dict[TNode, int]): Shortest hop levels using direction-optimizing switching.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact shortest path levels matching standard BFS with minimal edge examinations.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoFrontierRepresentationSwitching(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-222
      name: GraphAlgoFrontierRepresentationSwitching
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, direction_optimizing, frontier_switching, push_pull, bfs]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          alpha: {type: number}
          beta: {type: number}
      outputs:
        type: object
        properties:
          distances: {type: object}
          mode_switches: {type: integer}
      parameters:
        alpha: {type: number}
        beta: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + M)
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        transpose_adjacency: Optional[Dict[TNode, List[TNode]]] = None,
        alpha: float = 14.0,
        beta: float = 24.0,
    ) -> None:
        """
        Initialize direction-optimizing frontier engine.

        Args:
            adjacency: Forward adjacency map.
            transpose_adjacency: Backward adjacency map (auto-constructed if None).
            alpha: Sparse-to-dense threshold constant (m_f > m_unvisited / alpha).
            beta: Dense-to-sparse threshold constant (n_f < n / beta).
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        if transpose_adjacency is not None:
            self._trans_adj = {u: list(nbrs) for u, nbrs in transpose_adjacency.items()}
        else:
            self._trans_adj = {u: [] for u in self._adj}
            for u, nbrs in self._adj.items():
                for v in nbrs:
                    if v not in self._trans_adj:
                        self._trans_adj[v] = []
                    self._trans_adj[v].append(u)

        self._alpha: float = alpha
        self._beta: float = beta
        self._nodes: List[TNode] = list(self._adj.keys())
        self._n: int = len(self._nodes)
        self._m: int = sum(len(nbrs) for nbrs in self._adj.values())

    def run_bfs(self, source: TNode) -> Tuple[Dict[TNode, int], int]:
        """
        Execute direction-optimizing BFS with push/pull frontier representation switching.

        Args:
            source: Root node.

        Returns:
            Tuple of (distances_dict, mode_switches_count).
        """
        if source not in self._adj:
            return {}, 0

        distances: Dict[TNode, int] = {source: 0}
        frontier_sparse: Set[TNode] = {source}
        mode_is_dense = False
        switches = 0
        depth = 0
        unvisited_edges = self._m

        while frontier_sparse or mode_is_dense:
            depth += 1

            if not mode_is_dense:
                frontier_edges = sum(len(self._adj.get(u, [])) for u in frontier_sparse)
                if frontier_edges > unvisited_edges / self._alpha:
                    mode_is_dense = True
                    switches += 1

            if not mode_is_dense:
                next_sparse: Set[TNode] = set()
                for u in frontier_sparse:
                    for v in self._adj.get(u, []):
                        if v not in distances:
                            distances[v] = depth
                            next_sparse.add(v)
                unvisited_edges -= sum(len(self._adj.get(v, [])) for v in next_sparse)
                frontier_sparse = next_sparse
                if not frontier_sparse:
                    break
            else:
                next_frontier: Set[TNode] = set()
                for v in self._nodes:
                    if v not in distances:
                        for u in self._trans_adj.get(v, []):
                            if u in distances and distances[u] == depth - 1:
                                distances[v] = depth
                                next_frontier.add(v)
                                break

                unvisited_edges -= sum(len(self._adj.get(v, [])) for v in next_frontier)

                if len(next_frontier) < self._n / self._beta:
                    mode_is_dense = False
                    switches += 1

                frontier_sparse = next_frontier
                if not frontier_sparse:
                    break

        return distances, switches
