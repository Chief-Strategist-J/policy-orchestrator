"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CHINESE POSTMAN (ALGO-GRAPH-ROUT-95)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Chinese Postman (Route Inspection) Problem solver for undirected graphs.
   Computes the minimum total weight closed walk traversing every edge at least once
   by matching odd-degree vertices via shortest path duplication and Euler circuit tracing.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^3 + 2^k * k^2) where k is the number of odd-degree vertices.
   - Space Complexity: O(V^2) distance matrices and multigraph adjacency.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Optimal edge-covering inspection tour.
================================================================================
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoChinesePostman(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROUT-95
      name: GraphAlgoChinesePostman
      version: 1.0.0
      category: graph_routing
      capability_tags: [graph, route_inspection, chinese_postman, eulerian_circuit, odd_matching]
      inputs:
        type: object
        required: [edges]
        properties:
          edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
      outputs:
        type: object
        required: [tour_cost, tour_path]
        properties:
          tour_cost: {type: number}
          tour_path:
            type: array
            items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^3 + 2^K * K^2)
        space: O(V^2)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode, float]]) -> None:
        self._edges: List[Tuple[TNode, TNode, float]] = edges
        self._nodes: Set[TNode] = set()
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {}

        for u, v, w in edges:
            self._nodes.add(u)
            self._nodes.add(v)
            if u not in self._adj:
                self._adj[u] = []
            if v not in self._adj:
                self._adj[v] = []
            self._adj[u].append((v, w))
            self._adj[v].append((u, w))

    def _dijkstra(self, src: TNode) -> Tuple[Dict[TNode, float], Dict[TNode, Optional[TNode]]]:
        dist: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
        prev: Dict[TNode, Optional[TNode]] = {u: None for u in self._nodes}
        dist[src] = 0.0
        pq: List[Tuple[float, str, TNode]] = [(0.0, str(src), src)]

        while pq:
            d, _, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in self._adj.get(u, []):
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], str(v), v))

        return dist, prev

    def _get_path(self, target: TNode, prev: Dict[TNode, Optional[TNode]]) -> List[TNode]:
        path: List[TNode] = []
        curr: Optional[TNode] = target
        while curr is not None:
            path.append(curr)
            curr = prev.get(curr)
        path.reverse()
        return path

    def compute_inspection_tour(self) -> Tuple[float, List[TNode]]:
        odd_nodes = [u for u in self._nodes if len(self._adj.get(u, [])) % 2 != 0]
        odd_nodes.sort(key=lambda x: str(x))

        augmented_edges: List[Tuple[TNode, TNode, float]] = list(self._edges)
        total_weight = sum(w for _, _, w in self._edges)

        if odd_nodes:
            all_pairs_dist: Dict[Tuple[TNode, TNode], float] = {}
            all_pairs_path: Dict[Tuple[TNode, TNode], List[TNode]] = {}

            for u in odd_nodes:
                d, p = self._dijkstra(u)
                for v in odd_nodes:
                    if u != v:
                        all_pairs_dist[(u, v)] = d[v]
                        all_pairs_path[(u, v)] = self._get_path(v, p)

            k = len(odd_nodes)
            memo: Dict[int, Tuple[float, List[Tuple[TNode, TNode]]]] = {}

            def min_weight_matching(mask: int) -> Tuple[float, List[Tuple[TNode, TNode]]]:
                if mask == 0:
                    return 0.0, []
                if mask in memo:
                    return memo[mask]

                first_idx = 0
                while (mask & (1 << first_idx)) == 0:
                    first_idx += 1

                min_res = float("inf")
                best_pairs: List[Tuple[TNode, TNode]] = []
                u_node = odd_nodes[first_idx]

                for second_idx in range(first_idx + 1, k):
                    if mask & (1 << second_idx):
                        v_node = odd_nodes[second_idx]
                        pair_cost = all_pairs_dist.get((u_node, v_node), float("inf"))
                        next_mask = mask ^ (1 << first_idx) ^ (1 << second_idx)
                        rem_cost, rem_pairs = min_weight_matching(next_mask)
                        if pair_cost + rem_cost < min_res:
                            min_res = pair_cost + rem_cost
                            best_pairs = [(u_node, v_node)] + rem_pairs

                memo[mask] = (min_res, best_pairs)
                return memo[mask]

            added_cost, matching = min_weight_matching((1 << k) - 1)
            total_weight += added_cost

            for u, v in matching:
                p = all_pairs_path[(u, v)]
                for idx in range(len(p) - 1):
                    p_u, p_v = p[idx], p[idx + 1]
                    w = all_pairs_dist.get((p_u, p_v), 1.0)
                    augmented_edges.append((p_u, p_v, w))

        multigraph_adj: Dict[TNode, List[TNode]] = {u: [] for u in self._nodes}
        for u, v, _ in augmented_edges:
            multigraph_adj[u].append(v)
            multigraph_adj[v].append(u)

        start_node = next(iter(self._nodes)) if self._nodes else None
        if start_node is None:
            return 0.0, []

        stack: List[TNode] = [start_node]
        tour: List[TNode] = []

        while stack:
            u = stack[-1]
            if multigraph_adj[u]:
                v = multigraph_adj[u].pop()
                multigraph_adj[v].remove(u)
                stack.append(v)
            else:
                tour.append(stack.pop())

        tour.reverse()
        return total_weight, tour
