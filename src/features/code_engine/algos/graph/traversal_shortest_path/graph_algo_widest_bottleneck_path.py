"""Widest Path (Maximum Bottleneck Capacity) Algorithm.

Computes the path between source and target that maximizes the minimum edge capacity
along the path using a modified Dijkstra with a maximum-priority heap.
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoWidestBottleneckPath(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-44
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(E log V)
      space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {
            u: list(edges) for u, edges in adjacency.items()
        }
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def find_widest_path(self, source: TNode, target: TNode) -> Tuple[float, List[TNode]]:
        if source == target:
            return float("inf"), [source]

        bottleneck: Dict[TNode, float] = {u: 0.0 for u in self._adj}
        parent: Dict[TNode, Optional[TNode]] = {u: None for u in self._adj}
        bottleneck[source] = float("inf")

        pq: List[Tuple[float, str, TNode]] = [(-float("inf"), str(source), source)]
        visited: Dict[TNode, bool] = {}

        while pq:
            neg_cap, _, u = heapq.heappop(pq)
            cap = -neg_cap

            if visited.get(u, False):
                continue
            visited[u] = True

            if u == target:
                break

            for v, edge_cap in self._adj.get(u, []):
                new_cap = min(cap, edge_cap)
                if new_cap > bottleneck.get(v, 0.0):
                    bottleneck[v] = new_cap
                    parent[v] = u
                    heapq.heappush(pq, (-new_cap, str(v), v))

        if bottleneck[target] == 0.0:
            return 0.0, []

        path: List[TNode] = []
        curr: Optional[TNode] = target
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()

        return bottleneck[target], path
