"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: YEN'S K-SHORTEST SIMPLE PATHS (ALGO-GRAPH-PATH-32)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Yen's algorithm computes the top-K loopless (simple) shortest paths between a
   designated source and target node. Utilizes deviation spur nodes, root path
   prefix sharing, and temporary edge/node bans with Dijkstra spur computations
   to maintain candidate priority heaps without exponential path branching.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(K * V * (E + V log V)).
   - Space Complexity: O(K * V) candidate path repository.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
   - Guarantees: All returned paths are strictly loopless (no repeated vertices).
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar, Set

NodeId = TypeVar("NodeId")


class GraphAlgoYenKShortestPaths(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PATH-32
      name: GraphAlgoYenKShortestPaths
      version: 1.0.0
      category: graph_shortest_path
      capability_tags: [graph, shortest_path, yens_algorithm, k_shortest_paths, loopless_paths]
      inputs:
        type: object
        required: [weighted_adjacency, start_node, target_node]
        properties:
          weighted_adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: object
                required: [target, weight]
                properties:
                  target: {type: string}
                  weight: {type: number}
          start_node: {type: string}
          target_node: {type: string}
      outputs:
        type: object
        required: [k_paths, num_paths_found]
      parameters:
        k: {type: integer, default: 3}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * V * (E + V log V))
        space: O(K * V)
    ---
    """

    @staticmethod
    def search(
        weighted_adjacency: Dict[str, List[Dict[str, Any]]],
        start_node: str,
        target_node: str,
        k: int = 3,
    ) -> Dict[str, Any]:
        initial_path, initial_cost = GraphAlgoYenKShortestPaths._dijkstra(
            weighted_adjacency, start_node, target_node, set(), set()
        )

        if not initial_path:
            return {"k_paths": [], "num_paths_found": 0}

        A: List[Dict[str, Any]] = [{"path": initial_path, "cost": initial_cost}]
        B: List[Tuple[float, List[str]]] = []
        B_set: Set[Tuple[str, ...]] = set()

        for k_idx in range(1, k):
            prev_path = A[k_idx - 1]["path"]

            for i in range(len(prev_path) - 1):
                spur_node = prev_path[i]
                root_path = prev_path[: i + 1]

                banned_edges: Set[Tuple[str, str]] = set()
                for p_dict in A:
                    p = p_dict["path"]
                    if len(p) > i and p[: i + 1] == root_path:
                        banned_edges.add((p[i], p[i + 1]))

                banned_nodes = set(root_path[:-1])

                spur_path, spur_cost = GraphAlgoYenKShortestPaths._dijkstra(
                    weighted_adjacency, spur_node, target_node, banned_nodes, banned_edges
                )

                if spur_path:
                    total_path = root_path[:-1] + spur_path
                    path_key = tuple(total_path)
                    if path_key not in B_set and not any(p["path"] == total_path for p in A):
                        total_cost = GraphAlgoYenKShortestPaths._compute_path_cost(
                            weighted_adjacency, total_path
                        )
                        heapq.heappush(B, (total_cost, total_path))
                        B_set.add(path_key)

            if not B:
                break

            cost, best_cand = heapq.heappop(B)
            A.append({"path": best_cand, "cost": cost})

        return {
            "k_paths": A,
            "num_paths_found": len(A),
            "requested_k": k,
        }

    @staticmethod
    def _dijkstra(
        adj: Dict[str, List[Dict[str, Any]]],
        start: str,
        target: str,
        banned_nodes: Set[str],
        banned_edges: Set[Tuple[str, str]],
    ) -> Tuple[List[str], float]:
        dist: Dict[str, float] = {start: 0.0}
        parent: Dict[str, Optional[str]] = {start: None}
        pq: List[Tuple[float, str]] = [(0.0, start)]

        while pq:
            d_curr, curr = heapq.heappop(pq)
            if curr == target:
                break
            if d_curr > dist.get(curr, float("inf")):
                continue

            for edge in adj.get(curr, []):
                tgt = str(edge["target"])
                wt = float(edge.get("weight", 1.0))
                if tgt in banned_nodes or (curr, tgt) in banned_edges:
                    continue

                if d_curr + wt < dist.get(tgt, float("inf")):
                    dist[tgt] = d_curr + wt
                    parent[tgt] = curr
                    heapq.heappush(pq, (dist[tgt], tgt))

        if target not in dist:
            return [], float("inf")

        path: List[str] = []
        curr_t = target
        while curr_t is not None:
            path.append(curr_t)
            curr_t = parent.get(curr_t)
        return path[::-1], dist[target]

    @staticmethod
    def _compute_path_cost(
        adj: Dict[str, List[Dict[str, Any]]],
        path: List[str],
    ) -> float:
        cost = 0.0
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            found = False
            for edge in adj.get(u, []):
                if str(edge["target"]) == v:
                    cost += float(edge.get("weight", 1.0))
                    found = True
                    break
            if not found:
                cost += 1.0
        return cost
