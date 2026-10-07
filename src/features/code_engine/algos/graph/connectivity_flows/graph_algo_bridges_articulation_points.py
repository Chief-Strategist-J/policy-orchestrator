"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BRIDGES & ARTICULATION POINTS (ALGO-GRAPH-CONN-53)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tarjan's Lowlink algorithm for finding all cut vertices (articulation points)
   and cut edges (bridges) whose removal increases graph connected components.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) single DFS traversal.
   - Space Complexity: O(V + E) discovery and lowlink arrays.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact identification of all single points of failure.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBridgesArticulationPoints(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CONN-53
      name: GraphAlgoBridgesArticulationPoints
      version: 1.0.0
      category: graph_connectivity
      capability_tags: [graph, connectivity, bridges, articulation_points, tarjan_lowlink]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [articulation_points, bridges]
        properties:
          articulation_points:
            type: array
            items: {type: string}
          bridges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def analyze(self) -> Tuple[Set[TNode], List[Tuple[TNode, TNode]]]:
        discovery: Dict[TNode, int] = {}
        low: Dict[TNode, int] = {}
        parent: Dict[TNode, Optional[TNode]] = {}
        articulation_points: Set[TNode] = set()
        bridges: List[Tuple[TNode, TNode]] = []
        timer = 0

        for node in sorted(self._adj.keys(), key=lambda x: str(x)):
            if node in discovery:
                continue

            stack: List[Tuple[TNode, int, int]] = [(node, 0, 0)]
            discovery[node] = timer
            low[node] = timer
            parent[node] = None
            timer += 1
            children_count: Dict[TNode, int] = {node: 0}

            while stack:
                u, edge_idx, state = stack[-1]
                neighbors = self._adj.get(u, [])

                if edge_idx < len(neighbors):
                    v = neighbors[edge_idx]
                    stack[-1] = (u, edge_idx + 1, state)

                    if v == parent[u]:
                        continue

                    if v in discovery:
                        low[u] = min(low[u], discovery[v])
                    else:
                        parent[v] = u
                        children_count[u] = children_count.get(u, 0) + 1
                        discovery[v] = timer
                        low[v] = timer
                        timer += 1
                        stack.append((v, 0, 0))
                else:
                    stack.pop()
                    p = parent[u]
                    if p is not None:
                        low[p] = min(low[p], low[u])
                        if low[u] > discovery[p]:
                            bridges.append((p, u))
                        if parent[p] is not None and low[u] >= discovery[p]:
                            articulation_points.add(p)
                    elif children_count.get(u, 0) > 1:
                        articulation_points.add(u)

        return articulation_points, bridges
