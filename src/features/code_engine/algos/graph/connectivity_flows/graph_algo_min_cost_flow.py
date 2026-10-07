"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MIN-COST FLOW (ALGO-GRAPH-FLOW-81)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Successive Shortest Path algorithm with node potentials for minimum-cost network flow.
   Maintains dual potentials to guarantee non-negative reduced costs, repeatedly sending
   flow along shortest residual paths using Dijkstra.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Flow * E log V) using Dijkstra on reduced costs.
   - Space Complexity: O(V + E) capacity, cost, and residual flow tracking.
   - Purity: Pure stateful flow network optimization.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Absence of negative-cost cycles in final residual network proves optimality.
================================================================================
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMinCostFlow(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-FLOW-81
      name: GraphAlgoMinCostFlow
      version: 1.0.0
      category: graph_flows
      capability_tags: [graph, min_cost_flow, successive_shortest_path, potentials, dijkstra]
      inputs:
        type: object
        required: [source, sink, target_flow]
        properties:
          source: {type: string}
          sink: {type: string}
          target_flow: {type: number}
      outputs:
        type: object
        required: [total_cost, achieved_flow, flow_map]
        properties:
          total_cost: {type: number}
          achieved_flow: {type: number}
          flow_map:
            type: object
            additionalProperties: {type: number}
      parameters:
        source: {type: string}
        sink: {type: string}
        target_flow: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(Flow * E log V)
        space: O(V + E)
    ---
    """

    def __init__(self) -> None:
        self._capacity: Dict[Tuple[TNode, TNode], float] = {}
        self._cost: Dict[Tuple[TNode, TNode], float] = {}
        self._flow: Dict[Tuple[TNode, TNode], float] = {}
        self._adj: Dict[TNode, List[TNode]] = {}
        self._nodes: Set[TNode] = set()

    def add_edge(self, u: TNode, v: TNode, cap: float, unit_cost: float) -> None:
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
        self._cost[(u, v)] = unit_cost
        self._cost[(v, u)] = -unit_cost
        self._flow[(u, v)] = 0.0
        self._flow[(v, u)] = 0.0

    def compute_min_cost_flow(
        self, source: TNode, sink: TNode, target_flow: float
    ) -> Tuple[float, float, Dict[Tuple[TNode, TNode], float]]:
        potential: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
        total_flow = 0.0
        total_cost = 0.0

        while total_flow < target_flow:
            dist: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
            prev_node: Dict[TNode, Optional[TNode]] = {u: None for u in self._nodes}
            dist[source] = 0.0

            pq: List[Tuple[float, str, TNode]] = [(0.0, str(source), source)]

            while pq:
                d, _, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue

                for v in self._adj.get(u, []):
                    res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)
                    if res_cap > 1e-9:
                        reduced_cost = self._cost.get((u, v), 0.0) + potential[u] - potential[v]
                        if dist[u] + reduced_cost < dist.get(v, float("inf")):
                            dist[v] = dist[u] + reduced_cost
                            prev_node[v] = u
                            heapq.heappush(pq, (dist[v], str(v), v))

            if dist[sink] == float("inf"):
                break

            for u in self._nodes:
                if dist[u] < float("inf"):
                    potential[u] += dist[u]

            push = target_flow - total_flow
            curr: Optional[TNode] = sink
            while curr != source and curr is not None:
                p = prev_node[curr]
                if p is not None:
                    res_cap = self._capacity.get((p, curr), 0.0) - self._flow.get((p, curr), 0.0)
                    push = min(push, res_cap)
                    curr = p
                else:
                    break

            curr = sink
            while curr != source and curr is not None:
                p = prev_node[curr]
                if p is not None:
                    self._flow[(p, curr)] += push
                    self._flow[(curr, p)] -= push
                    total_cost += push * self._cost.get((p, curr), 0.0)
                    curr = p
                else:
                    break

            total_flow += push

        return total_cost, total_flow, {k: v for k, v in self._flow.items() if v > 0}
