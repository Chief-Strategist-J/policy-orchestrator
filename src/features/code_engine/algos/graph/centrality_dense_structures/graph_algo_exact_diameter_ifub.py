"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EXACT DIAMETER IFUB & DOUBLE SWEEP (ALGO-GRAPH-NET-137)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Exact graph diameter computation using Double Sweep lower bounding and
   Iterative Fringe Upper Bound (iFUB). Executes BFS sweeps from the fringes of a central
   vertex, updating lower and upper bounds dynamically to determine the exact largest
   shortest path in a small number of BFS traversals.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * (V + E)) where k is the number of evaluated fringe BFS passes.
   - Space Complexity: O(V) distance arrays.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Connected undirected graph adjacency.

4. OUTPUT PARAMETERS:
   - exact_diameter: int - Largest shortest path distance in the graph.
   - peripheral_pair: Tuple[TNode, TNode] - Endpoints realizing the maximum path distance.
   - bfs_count: int - Total number of BFS passes performed.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected graph.
   - Guardrails: Stopping rule 2 * (fringe_dist) <= lower_bound guarantees exactness without exhaustive all-pairs BFS.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoExactDiameterIfub(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-137
      name: GraphAlgoExactDiameterIfub
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, exact_diameter, double_sweep, ifub, fringe_upper_bound]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [exact_diameter, peripheral_pair, bfs_count]
        properties:
          exact_diameter: {type: integer}
          peripheral_pair: {type: array, items: {type: string}}
          bfs_count: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * (V + E))
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the exact diameter iFUB engine.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _bfs(self, start: TNode) -> Tuple[Dict[TNode, int], TNode, int]:
        dist: Dict[TNode, int] = {start: 0}
        q: Deque[TNode] = deque([start])
        farthest_node = start
        max_dist = 0

        while q:
            u = q.popleft()
            d = dist[u]
            if d > max_dist:
                max_dist = d
                farthest_node = u
            for v in self._adj.get(u, []):
                if v not in dist:
                    dist[v] = d + 1
                    q.append(v)

        return dist, farthest_node, max_dist

    def compute_exact_diameter(self) -> Tuple[int, Tuple[TNode, TNode], int]:
        """
        Execute Double Sweep and iFUB bounding to find the exact graph diameter.

        Returns:
            Tuple of (exact_diameter, peripheral_endpoints_pair, total_bfs_executions).
        """
        n = len(self._nodes)
        if n <= 1:
            return 0, (self._nodes[0], self._nodes[0]) if n == 1 else (None, None), 0

        bfs_count = 0
        v1 = self._nodes[0]
        _, u, _ = self._bfs(v1)
        bfs_count += 1

        dist_u, v, lb = self._bfs(u)
        bfs_count += 1
        best_pair = (u, v)

        center = min(self._nodes, key=lambda x: dist_u.get(x, float("inf")))
        dist_c, _, max_c_dist = self._bfs(center)
        bfs_count += 1

        fringes: Dict[int, List[TNode]] = {}
        for x, d in dist_c.items():
            if d not in fringes:
                fringes[d] = []
            fringes[d].append(x)

        current_d = max_c_dist
        while current_d > 0 and 2 * current_d > lb:
            for node in fringes.get(current_d, []):
                dist_node, far_node, d_node = self._bfs(node)
                bfs_count += 1
                if d_node > lb:
                    lb = d_node
                    best_pair = (node, far_node)
                if 2 * current_d <= lb:
                    break
            current_d -= 1

        return lb, best_pair, bfs_count
