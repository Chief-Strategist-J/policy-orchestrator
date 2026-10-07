"""Resource-Constrained Shortest Path (RCSP) Algorithm.

Solves the shortest path problem subject to an upper bound on an auxiliary resource (e.g. latency, fuel, hops)
using multiobjective label setting with Pareto dominance pruning.
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoResourceConstrainedShortestPath(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-41
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(|V| * R_max * log(|V| * R_max) + |E| * R_max)
      space: O(|V| * R_max)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float, float]]] = {
            u: list(edges) for u, edges in adjacency.items()
        }
        for u in list(self._adj.keys()):
            for v, _, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def find_shortest_constrained_path(
        self,
        source: TNode,
        target: TNode,
        max_resource: float,
        max_labels_per_node: int = 50,
    ) -> Tuple[float, float, List[TNode]]:
        if source == target:
            return 0.0, 0.0, [source]

        labels: Dict[TNode, List[Tuple[float, float]]] = {u: [] for u in self._adj}
        
        pq: List[Tuple[float, float, str, TNode, List[TNode]]] = [
            (0.0, 0.0, str(source), source, [source])
        ]
        
        while pq:
            cost, res, _, u, path = heapq.heappop(pq)
            
            if res > max_resource:
                continue
                
            if any(l_cost <= cost and l_res <= res for l_cost, l_res in labels[u]):
                continue
                
            labels[u] = [
                (l_cost, l_res)
                for l_cost, l_res in labels[u]
                if not (cost <= l_cost and res <= l_res)
            ]
            labels[u].append((cost, res))
            
            if len(labels[u]) > max_labels_per_node:
                labels[u].sort(key=lambda item: item[0])
                labels[u] = labels[u][:max_labels_per_node]
                
            if u == target:
                return cost, res, path
                
            for v, edge_cost, edge_res in self._adj.get(u, []):
                new_cost = cost + edge_cost
                new_res = res + edge_res
                
                if new_res <= max_resource:
                    is_dominated = any(
                        l_cost <= new_cost and l_res <= new_res
                        for l_cost, l_res in labels[v]
                    )
                    if not is_dominated:
                        heapq.heappush(
                            pq,
                            (new_cost, new_res, str(v), v, path + [v]),
                        )

        return float("inf"), float("inf"), []
