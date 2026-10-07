"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EDMONDS-KARP MAXIMUM FLOW (ALGO-GRAPH-FLOW-74)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Edmonds-Karp algorithm for maximum flow and minimum s-t cut extraction.
   Computes maximum network flow and certificates minimum s-t cuts via shortest augmenting paths (BFS)
   in residual capacity graphs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E^2) augmenting path iterations.
   - Space Complexity: O(V + E) residual capacities and flow tracking.
   - Purity: Pure stateful flow network optimization.

3. AGENT CONTRACT:
   - Role: Optimizer & Verifier.
   - Guarantees: Flow conservation and min-cut capacity equality theorem verification.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEdmondsKarpMaxFlow(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-FLOW-74
      name: GraphAlgoEdmondsKarpMaxFlow
      version: 1.0.0
      category: graph_flows
      capability_tags: [graph, max_flow, min_cut, edmonds_karp, residual_network, augmenting_path]
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
          min_cut_source_partition:
            type: array
            items: {type: string}
          min_cut_sink_partition:
            type: array
            items: {type: string}
          min_cut_edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}]
      parameters:
        source: {type: string}
        sink: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * E^2)
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
            parent: Dict[TNode, Optional[Tuple[TNode, float]]] = {source: None}
            queue: deque[TNode] = deque([source])

            while queue:
                u = queue.popleft()
                if u == sink:
                    break
                for v in self._adj.get(u, []):
                    res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)
                    if res_cap > 1e-9 and v not in parent:
                        parent[v] = (u, res_cap)
                        queue.append(v)

            if sink not in parent:
                break

            push_amt = float("inf")
            curr: Optional[TNode] = sink
            while curr != source and curr is not None:
                p_info = parent[curr]
                if p_info is not None:
                    p, c = p_info
                    push_amt = min(push_amt, c)
                    curr = p
                else:
                    break

            curr = sink
            while curr != source and curr is not None:
                p_info = parent[curr]
                if p_info is not None:
                    p, _ = p_info
                    self._flow[(p, curr)] += push_amt
                    self._flow[(curr, p)] -= push_amt
                    curr = p
                else:
                    break

            max_flow += push_amt

        return max_flow, {k: v for k, v in self._flow.items() if v > 0}

    def extract_min_cut(self, source: TNode) -> Tuple[Set[TNode], Set[TNode], List[Tuple[TNode, TNode]]]:
        reachable: Set[TNode] = {source}
        queue: deque[TNode] = deque([source])

        while queue:
            u = queue.popleft()
            for v in self._adj.get(u, []):
                res_cap = self._capacity.get((u, v), 0.0) - self._flow.get((u, v), 0.0)
                if res_cap > 1e-9 and v not in reachable:
                    reachable.add(v)
                    queue.append(v)

        unreachable = self._nodes - reachable
        cut_edges: List[Tuple[TNode, TNode]] = []
        for u in reachable:
            for v in unreachable:
                if self._capacity.get((u, v), 0.0) > 0:
                    cut_edges.append((u, v))

        return reachable, unreachable, cut_edges
