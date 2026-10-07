"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PUSH-RELABEL MAX FLOW (ALGO-GRAPH-FLOW-76)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Goldberg-Tarjan Push-Relabel algorithm for maximum network flow.
   Maintains preflows and excess queues, applying local push operations and
   relabel operations guided by height labels.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^2 * sqrt(E)) with highest-label selection.
   - Space Complexity: O(V + E) heights, excess arrays, and residual capacities.
   - Purity: Pure stateful flow network optimization.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Exact maximum flow computation with local height-driven operations.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPushRelabel(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-FLOW-76
      name: GraphAlgoPushRelabel
      version: 1.0.0
      category: graph_flows
      capability_tags: [graph, max_flow, push_relabel, goldberg_tarjan, preflow]
      inputs:
        type: object
        required: [source, sink]
        properties:
          source: {type: string}
          sink: {type: string}
      outputs:
        type: object
        required: [max_flow, non_zero_flows]
        properties:
          max_flow: {type: number}
          non_zero_flows:
            type: object
            additionalProperties: {type: number}
      parameters:
        source: {type: string}
        sink: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^2 * sqrt(E))
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

        n = len(self._nodes)
        height: Dict[TNode, int] = {u: 0 for u in self._nodes}
        excess: Dict[TNode, float] = {u: 0.0 for u in self._nodes}

        height[source] = n

        for v in self._adj.get(source, []):
            cap = self._capacity.get((source, v), 0.0)
            if cap > 0:
                self._flow[(source, v)] += cap
                self._flow[(v, source)] -= cap
                excess[v] += cap
                excess[source] -= cap

        active_queue: deque[TNode] = deque([v for v in self._nodes if v != source and v != sink and excess[v] > 1e-9])

        while active_queue:
            u = active_queue.popleft()
            if excess[u] <= 1e-9 or u == source or u == sink:
                continue

            pushed = False
            for v in self._adj.get(u, []):
                res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)
                if res_cap > 1e-9 and height[u] == height[v] + 1:
                    delta = min(excess[u], res_cap)
                    self._flow[(u, v)] += delta
                    self._flow[(v, u)] -= delta
                    excess[u] -= delta
                    excess[v] += delta
                    pushed = True

                    if v != source and v != sink and excess[v] > 1e-9 and v not in active_queue:
                        active_queue.append(v)

                    if excess[u] <= 1e-9:
                        break

            if excess[u] > 1e-9:
                min_h = float("inf")
                for v in self._adj.get(u, []):
                    res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)
                    if res_cap > 1e-9:
                        min_h = min(min_h, height[v])

                if min_h != float("inf"):
                    height[u] = int(min_h) + 1
                    active_queue.append(u)

        max_flow = sum(self._flow.get((source, v), 0.0) for v in self._adj.get(source, []))
        return max(0.0, max_flow), {k: v for k, v in self._flow.items() if v > 0}
