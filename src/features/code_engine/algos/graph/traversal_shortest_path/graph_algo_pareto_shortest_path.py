"""Multi-Criteria Pareto Shortest Path Algorithm.

Computes the non-dominated Pareto front of paths between source and target
under multiple conflicting objective criteria (e.g. latency, cost, risk).
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoParetoShortestPath(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-42
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(|V| * |Pareto_Front| * log(|V| * |Pareto_Front|))
      space: O(|V| * |Pareto_Front|)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, Tuple[float, ...]]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, Tuple[float, ...]]]] = {
            u: list(edges) for u, edges in adjacency.items()
        }
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def _dominates(self, vec_a: Tuple[float, ...], vec_b: Tuple[float, ...]) -> bool:
        return all(a <= b for a, b in zip(vec_a, vec_b)) and any(a < b for a, b in zip(vec_a, vec_b))

    def find_pareto_front(
        self,
        source: TNode,
        target: TNode,
        max_front_size: int = 50,
    ) -> List[Tuple[Tuple[float, ...], List[TNode]]]:
        if source == target:
            first_edge = next(iter(self._adj.get(source, [])), None)
            dim = len(first_edge[1]) if first_edge else 2
            zero_vec = tuple(0.0 for _ in range(dim))
            return [(zero_vec, [source])]

        pareto_labels: Dict[TNode, List[Tuple[Tuple[float, ...], List[TNode]]]] = {
            u: [] for u in self._adj
        }
        
        first_edge = None
        for u in self._adj:
            if self._adj[u]:
                first_edge = self._adj[u][0]
                break
        dim = len(first_edge[1]) if first_edge else 2
        zero_cost = tuple(0.0 for _ in range(dim))

        pq: List[Tuple[float, Tuple[float, ...], str, TNode, List[TNode]]] = [
            (0.0, zero_cost, str(source), source, [source])
        ]

        while pq:
            scalar_sum, cost_vec, _, u, path = heapq.heappop(pq)

            if any(self._dominates(existing_vec, cost_vec) for existing_vec, _ in pareto_labels[u]):
                continue

            pareto_labels[u] = [
                (existing_vec, p)
                for existing_vec, p in pareto_labels[u]
                if not self._dominates(cost_vec, existing_vec)
            ]
            pareto_labels[u].append((cost_vec, path))

            if len(pareto_labels[u]) > max_front_size:
                pareto_labels[u].sort(key=lambda item: sum(item[0]))
                pareto_labels[u] = pareto_labels[u][:max_front_size]

            if u == target:
                continue

            for v, edge_vec in self._adj.get(u, []):
                new_vec = tuple(a + b for a, b in zip(cost_vec, edge_vec))
                if not any(self._dominates(existing_vec, new_vec) for existing_vec, _ in pareto_labels[v]):
                    heapq.heappush(
                        pq,
                        (sum(new_vec), new_vec, str(v), v, path + [v]),
                    )

        target_front = pareto_labels.get(target, [])
        target_front.sort(key=lambda item: sum(item[0]))
        return target_front
