"""Karp's Minimum Cycle Mean Algorithm.

Computes the minimum average edge weight cycle in a directed weighted graph
via dynamic programming over path lengths of size 0 to n.
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoKarpMinMeanCycle(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-45
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(V * E)
      space: O(V^2)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._nodes: List[TNode] = list(adjacency.keys())
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {
            u: list(edges) for u, edges in adjacency.items()
        }
        for u in list(self._nodes):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []
                    self._nodes.append(v)
        self._node_to_idx: Dict[TNode, int] = {node: i for i, node in enumerate(self._nodes)}

    def compute_min_cycle_mean(self) -> Tuple[Optional[float], Optional[List[TNode]]]:
        n = len(self._nodes)
        if n == 0:
            return None, None

        dp: List[Dict[TNode, float]] = [{u: 0.0 for u in self._nodes}]
        parent: List[Dict[TNode, Optional[TNode]]] = [{u: None for u in self._nodes}]

        for k in range(1, n + 1):
            curr_dist: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
            curr_parent: Dict[TNode, Optional[TNode]] = {u: None for u in self._nodes}

            for u in self._nodes:
                prev_d = dp[k - 1][u]
                if prev_d == float("inf"):
                    continue
                for v, w in self._adj.get(u, []):
                    if prev_d + w < curr_dist[v]:
                        curr_dist[v] = prev_d + w
                        curr_parent[v] = u

            dp.append(curr_dist)
            parent.append(curr_parent)

        min_mean = float("inf")
        best_v: Optional[TNode] = None

        for v in self._nodes:
            d_n_v = dp[n][v]
            if d_n_v == float("inf"):
                continue

            max_ratio = float("-inf")
            for k in range(n):
                d_k_v = dp[k][v]
                if d_k_v == float("inf"):
                    continue
                ratio = (d_n_v - d_k_v) / (n - k)
                if ratio > max_ratio:
                    max_ratio = ratio

            if max_ratio != float("-inf") and max_ratio < min_mean:
                min_mean = max_ratio
                best_v = v

        if min_mean == float("inf") or best_v is None:
            return None, None

        cycle = self._extract_cycle(best_v, parent, n)
        return min_mean, cycle

    def _extract_cycle(
        self,
        start_node: TNode,
        parent: List[Dict[TNode, Optional[TNode]]],
        n: int,
    ) -> List[TNode]:
        path: List[TNode] = []
        curr = start_node
        k = n
        while k > 0 and curr is not None:
            path.append(curr)
            curr = parent[k].get(curr)
            k -= 1

        seen: Dict[TNode, int] = {}
        for idx, node in enumerate(path):
            if node in seen:
                cycle_slice = path[seen[node]:idx + 1]
                cycle_slice.reverse()
                return cycle_slice
            seen[node] = idx

        return path
