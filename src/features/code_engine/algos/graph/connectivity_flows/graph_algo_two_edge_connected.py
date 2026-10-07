"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: 2-EDGE-CONNECTED COMPONENTS (ALGO-GRAPH-CONN-55)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Extracts maximal 2-edge-connected subgraphs resilient to single-link failures
   and contracts them into the tree of bridges.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) bridge detection and component contraction.
   - Space Complexity: O(V + E) component sets and bridge tree adjacency.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Full decomposition into bridge-free components and bridge tree.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTwoEdgeConnected(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CONN-55
      name: GraphAlgoTwoEdgeConnected
      version: 1.0.0
      category: graph_connectivity
      capability_tags: [graph, 2_edge_connected, bridge_tree, link_failure_resilience]
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
        required: [components, bridges, bridge_tree]
        properties:
          components:
            type: array
            items:
              type: array
              items: {type: string}
          bridges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}]
          bridge_tree:
            type: object
            additionalProperties:
              type: array
              items: {type: integer}
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

    def decompose(self) -> Tuple[List[Set[TNode]], List[Tuple[TNode, TNode]], Dict[int, List[int]]]:
        discovery: Dict[TNode, int] = {}
        low: Dict[TNode, int] = {}
        parent: Dict[TNode, Optional[TNode]] = {}
        bridges: Set[Tuple[TNode, TNode]] = set()
        timer = 0

        for node in sorted(self._adj.keys(), key=lambda x: str(x)):
            if node in discovery:
                continue

            stack: List[Tuple[TNode, int]] = [(node, 0)]
            discovery[node] = timer
            low[node] = timer
            parent[node] = None
            timer += 1

            while stack:
                u, edge_idx = stack[-1]
                neighbors = self._adj.get(u, [])

                if edge_idx < len(neighbors):
                    v = neighbors[edge_idx]
                    stack[-1] = (u, edge_idx + 1)

                    if v == parent[u]:
                        continue

                    if v in discovery:
                        low[u] = min(low[u], discovery[v])
                    else:
                        parent[v] = u
                        discovery[v] = timer
                        low[v] = timer
                        timer += 1
                        stack.append((v, 0))
                else:
                    stack.pop()
                    p = parent[u]
                    if p is not None:
                        low[p] = min(low[p], low[u])
                        if low[u] > discovery[p]:
                            bridges.add((p, u))
                            bridges.add((u, p))

        visited: Set[TNode] = set()
        components: List[Set[TNode]] = []
        node_to_comp: Dict[TNode, int] = {}

        for node in sorted(self._adj.keys(), key=lambda x: str(x)):
            if node in visited:
                continue

            comp: Set[TNode] = set()
            queue: deque[TNode] = deque([node])
            visited.add(node)

            while queue:
                u = queue.popleft()
                comp.add(u)
                node_to_comp[u] = len(components)

                for v in self._adj.get(u, []):
                    if (u, v) in bridges:
                        continue
                    if v not in visited:
                        visited.add(v)
                        queue.append(v)

            components.append(comp)

        bridge_tree: Dict[int, List[int]] = {i: [] for i in range(len(components))}
        unique_bridges: List[Tuple[TNode, TNode]] = []

        for u, v in bridges:
            if str(u) < str(v):
                unique_bridges.append((u, v))
                c_u = node_to_comp[u]
                c_v = node_to_comp[v]
                if c_v not in bridge_tree[c_u]:
                    bridge_tree[c_u].append(c_v)
                if c_u not in bridge_tree[c_v]:
                    bridge_tree[c_v].append(c_u)

        return components, unique_bridges, bridge_tree
