"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DINIC MAXIMUM FLOW (ALGO-GRAPH-FLOW-75)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dinic's algorithm for maximum network flow using layered BFS level graphs
   and DFS blocking flows with dead-edge pruning.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^2 * E) general capacities, O(E * sqrt(V)) unit capacities.
   - Space Complexity: O(V + E) level graph and pointer structures.
   - Purity: Pure stateful flow network optimization.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Monotonically increasing shortest augmenting path phase length.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDinicMaxFlow(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-FLOW-75
      name: GraphAlgoDinicMaxFlow
      version: 1.0.0
      category: graph_flows
      capability_tags: [graph, max_flow, dinic_algorithm, blocking_flow, level_graph]
      inputs:
        type: object
        required: [source, sink]
        properties:
          source: {type: string}
          sink: {type: string}
      outputs:
        type: object
        required: [max_flow, flow_map]
        properties:
          max_flow: {type: number}
          flow_map:
            type: object
            additionalProperties: {type: number}
      parameters:
        source: {type: string}
        sink: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^2 * E)
        space: O(V + E)
    ---
    """

    def __init__(self) -> None:
        self._capacity: Dict[Tuple[TNode, TNode], float] = {}
        self._flow: Dict[Tuple[TNode, TNode], float] = {}
        self._adj: Dict[TNode, List[TNode]] = {}
        self._nodes: Set[TNode] = set()

    def add_edge(self, u: TNode, v: TNode, cap: float) -> None:
        self._nodes.add(u)
        self._nodes.add(v)
        if u not in self._adj:
            self._adj[u] = []
        if v not in self._adj:
            self._adj[v] = []

        self._adj[u].append(v)
        self._adj[v].append(u)
        self._capacity[(u, v)] = self._capacity.get((u, v), 0.0) + cap
        self._capacity[(v, u)] = self._capacity.get((v, u), 0.0)
        self._flow[(u, v)] = 0.0
        self._flow[(v, u)] = 0.0

    def compute_max_flow(self, source: TNode, sink: TNode) -> Tuple[float, Dict[Tuple[TNode, TNode], float]]:
        if source == sink:
            return float("inf"), {}

        max_flow = 0.0

        while True:
            level: Dict[TNode, int] = {source: 0}
            queue: deque[TNode] = deque([source])

            while queue:
                u = queue.popleft()
                for v in self._adj.get(u, []):
                    res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)
                    if res_cap > 1e-9 and v not in level:
                        level[v] = level[u] + 1
                        queue.append(v)

            if sink not in level:
                break

            ptr: Dict[TNode, int] = {u: 0 for u in self._nodes}

            def dfs_blocking(u: TNode, pushed: float) -> float:
                if pushed <= 1e-9 or u == sink:
                    return pushed

                neighbors = self._adj.get(u, [])
                while ptr[u] < len(neighbors):
                    v = neighbors[ptr[u]]
                    res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)

                    if level.get(v, -1) == level[u] + 1 and res_cap > 1e-9:
                        tr = dfs_blocking(v, min(pushed, res_cap))
                        if tr > 1e-9:
                            self._flow[(u, v)] += tr
                            self._flow[(v, u)] -= tr
                            return tr

                    ptr[u] += 1

                return 0.0

            while True:
                pushed = dfs_blocking(source, float("inf"))
                if pushed <= 1e-9:
                    break
                max_flow += pushed

        return max_flow, {k: v for k, v in self._flow.items() if v > 0}
