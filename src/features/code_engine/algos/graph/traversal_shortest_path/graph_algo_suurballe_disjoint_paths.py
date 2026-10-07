"""Suurballe-Bhandari Disjoint Shortest Paths Algorithm.

Finds pairs of edge-disjoint paths between a source and target with minimum total length
using potential reweighting, residual graph edge reversal, and second-pass Dijkstra.
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSuurballeDisjointPaths(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-40
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(E log V)
      space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: list(edges) for u, edges in adjacency.items()}
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def _dijkstra(
        self,
        src: TNode,
        graph: Dict[TNode, List[Tuple[TNode, float]]],
    ) -> Tuple[Dict[TNode, float], Dict[TNode, Optional[TNode]]]:
        dist: Dict[TNode, float] = {u: float("inf") for u in self._adj}
        prev: Dict[TNode, Optional[TNode]] = {u: None for u in self._adj}
        dist[src] = 0.0
        pq: List[Tuple[float, str, TNode]] = [(0.0, str(src), src)]

        while pq:
            d, _, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in graph.get(u, []):
                if dist[u] + w < dist.get(v, float("inf")):
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], str(v), v))

        return dist, prev

    def _reconstruct_path(self, target: TNode, prev: Dict[TNode, Optional[TNode]]) -> List[TNode]:
        path: List[TNode] = []
        curr: Optional[TNode] = target
        while curr is not None:
            path.append(curr)
            curr = prev.get(curr)
        path.reverse()
        return path

    def find_disjoint_paths(self, source: TNode, target: TNode) -> Tuple[float, List[List[TNode]]]:
        if source == target:
            return 0.0, [[source], [source]]

        dist1, prev1 = self._dijkstra(source, self._adj)
        if dist1.get(target, float("inf")) == float("inf"):
            return float("inf"), []

        path1 = self._reconstruct_path(target, prev1)
        if len(path1) < 2:
            return float("inf"), []

        p1_edges: Set[Tuple[TNode, TNode]] = set()
        for i in range(len(path1) - 1):
            p1_edges.add((path1[i], path1[i + 1]))

        mod_graph: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in self._adj}
        for u in self._adj:
            for v, w in self._adj[u]:
                if (u, v) in p1_edges:
                    continue
                w_mod = w - dist1[v] + dist1[u]
                mod_graph[u].append((v, max(0.0, w_mod)))

        for u, v in p1_edges:
            mod_graph[v].append((u, 0.0))

        dist2, prev2 = self._dijkstra(source, mod_graph)
        if dist2.get(target, float("inf")) == float("inf"):
            return dist1[target], [path1]

        path2_raw = self._reconstruct_path(target, prev2)
        p2_edges: Set[Tuple[TNode, TNode]] = set()
        for i in range(len(path2_raw) - 1):
            p2_edges.add((path2_raw[i], path2_raw[i + 1]))

        active_edges: Set[Tuple[TNode, TNode]] = set()
        for u, v in p1_edges:
            if (v, u) not in p2_edges:
                active_edges.add((u, v))
        for u, v in p2_edges:
            if (v, u) not in p1_edges:
                active_edges.add((u, v))

        outgoing: Dict[TNode, List[TNode]] = {u: [] for u in self._adj}
        for u, v in active_edges:
            outgoing[u].append(v)

        final_paths: List[List[TNode]] = []
        for first_step in list(outgoing.get(source, [])):
            cur_path = [source, first_step]
            curr = first_step
            while curr != target and outgoing.get(curr):
                nxt = outgoing[curr].pop()
                cur_path.append(nxt)
                curr = nxt
            if cur_path[-1] == target:
                final_paths.append(cur_path)

        edge_weights: Dict[Tuple[TNode, TNode], float] = {}
        for u in self._adj:
            for v, w in self._adj[u]:
                edge_weights[(u, v)] = w

        total_cost = 0.0
        for p in final_paths:
            for i in range(len(p) - 1):
                total_cost += edge_weights.get((p[i], p[i + 1]), 0.0)

        return total_cost, final_paths
