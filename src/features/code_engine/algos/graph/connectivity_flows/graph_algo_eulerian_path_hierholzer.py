"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HIERHOLZER EULERIAN PATH & CIRCUIT (ALGO-GRAPH-ROUT-96)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hierholzer's algorithm for finding Eulerian paths and circuits that traverse every edge exactly once.
   Validates in-degree/out-degree parity invariants and extracts the tour in linear O(E) time.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) single edge traversal.
   - Space Complexity: O(V + E) edge index pointers and path stack.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
   - Guarantees: Degree parity verification certificates existence before extraction.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEulerianPathHierholzer(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROUT-96
      name: GraphAlgoEulerianPathHierholzer
      version: 1.0.0
      category: graph_routing
      capability_tags: [graph, eulerian_path, eulerian_circuit, hierholzer, route_inspection]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          directed: {type: boolean, default: true}
      outputs:
        type: object
        required: [has_eulerian_path, is_circuit, eulerian_trail]
        properties:
          has_eulerian_path: {type: boolean}
          is_circuit: {type: boolean}
          eulerian_trail:
            type: array
            items: {type: string}
      parameters:
        directed: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], directed: bool = True) -> None:
        self._directed: bool = directed
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))

    def find_eulerian_trail(self) -> Tuple[bool, bool, List[TNode]]:
        in_deg: Dict[TNode, int] = {u: 0 for u in self._nodes}
        out_deg: Dict[TNode, int] = {u: len(self._adj.get(u, [])) for u in self._nodes}

        for u in self._nodes:
            for v in self._adj.get(u, []):
                in_deg[v] += 1

        start_node: Optional[TNode] = None
        end_node: Optional[TNode] = None
        is_circuit = True

        for u in self._nodes:
            diff = out_deg[u] - in_deg[u]
            if diff == 1:
                if start_node is not None:
                    return False, False, []
                start_node = u
                is_circuit = False
            elif diff == -1:
                if end_node is not None:
                    return False, False, []
                end_node = u
                is_circuit = False
            elif diff != 0:
                return False, False, []

        if start_node is None:
            non_isolated = [u for u in self._nodes if out_deg[u] > 0]
            start_node = non_isolated[0] if non_isolated else (self._nodes[0] if self._nodes else None)

        if start_node is None:
            return True, True, []

        cur_adj: Dict[TNode, List[TNode]] = {u: list(self._adj[u]) for u in self._nodes}
        stack: List[TNode] = [start_node]
        trail: List[TNode] = []

        while stack:
            u = stack[-1]
            if cur_adj.get(u):
                v = cur_adj[u].pop()
                stack.append(v)
            else:
                trail.append(stack.pop())

        trail.reverse()
        total_edges = sum(len(self._adj[u]) for u in self._nodes)
        if len(trail) != total_edges + 1:
            return False, False, []

        return True, is_circuit, trail
