"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BIDIRECTIONAL DIJKSTRA (ALGO-GRAPH-PATH-26)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Bidirectional Dijkstra executes simultaneous forward and backward priority
   queue searches from source and target nodes. Maintains the best candidate
   path length mu and terminates when top_f + top_b >= mu, guaranteeing exact
   shortest weighted paths while expanding a fraction of the search space.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E * log V) with up to 50% fewer settled nodes.
   - Space Complexity: O(V) for dual heap and distance tables.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
   - Preconditions: All edge weights must be strictly non-negative.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoBidirectionalDijkstra(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PATH-26
      name: GraphAlgoBidirectionalDijkstra
      version: 1.0.0
      category: graph_shortest_path
      capability_tags: [graph, shortest_path, bidirectional_dijkstra, weighted_shortest_path]
      inputs:
        type: object
        required: [forward_adjacency, backward_adjacency, start_node, target_node]
        properties:
          forward_adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: object
                required: [target, weight]
                properties:
                  target: {type: string}
                  weight: {type: number}
          backward_adjacency:
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
        required: [found, path, distance, meeting_node, nodes_settled]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E log V)
        space: O(V)
    ---
    """

    @staticmethod
    def search(
        forward_adjacency: Dict[str, List[Dict[str, Any]]],
        backward_adjacency: Dict[str, List[Dict[str, Any]]],
        start_node: str,
        target_node: str,
    ) -> Dict[str, Any]:
        if start_node == target_node:
            return {
                "found": True,
                "path": [start_node],
                "distance": 0.0,
                "meeting_node": start_node,
                "nodes_settled": 1,
            }

        dist_f: Dict[str, float] = {start_node: 0.0}
        dist_b: Dict[str, float] = {target_node: 0.0}

        parent_f: Dict[str, Optional[str]] = {start_node: None}
        parent_b: Dict[str, Optional[str]] = {target_node: None}

        settled_f: set = set()
        settled_b: set = set()

        heap_f: List[Tuple[float, str]] = [(0.0, start_node)]
        heap_b: List[Tuple[float, str]] = [(0.0, target_node)]

        mu = float("inf")
        best_meeting_node: Optional[str] = None
        nodes_settled = 0

        while heap_f and heap_b:
            if heap_f[0][0] + heap_b[0][0] >= mu:
                break

            if len(heap_f) <= len(heap_b):
                d_u, u = heapq.heappop(heap_f)
                if u in settled_f:
                    continue
                settled_f.add(u)
                nodes_settled += 1

                for edge in forward_adjacency.get(u, []):
                    v = str(edge["target"])
                    w = max(0.0, float(edge.get("weight", 1.0)))
                    if d_u + w < dist_f.get(v, float("inf")):
                        dist_f[v] = d_u + w
                        parent_f[v] = u
                        heapq.heappush(heap_f, (dist_f[v], v))

                    if v in dist_b:
                        cand_dist = dist_f[v] + dist_b[v]
                        if cand_dist < mu:
                            mu = cand_dist
                            best_meeting_node = v
            else:
                d_u, u = heapq.heappop(heap_b)
                if u in settled_b:
                    continue
                settled_b.add(u)
                nodes_settled += 1

                for edge in backward_adjacency.get(u, []):
                    v = str(edge["target"])
                    w = max(0.0, float(edge.get("weight", 1.0)))
                    if d_u + w < dist_b.get(v, float("inf")):
                        dist_b[v] = d_u + w
                        parent_b[v] = u
                        heapq.heappush(heap_b, (dist_b[v], v))

                    if v in dist_f:
                        cand_dist = dist_b[v] + dist_f[v]
                        if cand_dist < mu:
                            mu = cand_dist
                            best_meeting_node = v

        if best_meeting_node is None or mu == float("inf"):
            return {
                "found": False,
                "path": [],
                "distance": -1.0,
                "meeting_node": None,
                "nodes_settled": nodes_settled,
            }

        path_f: List[str] = []
        curr_f = best_meeting_node
        while curr_f is not None:
            path_f.append(curr_f)
            curr_f = parent_f.get(curr_f)
        path_f = path_f[::-1]

        path_b: List[str] = []
        curr_b = parent_b.get(best_meeting_node)
        while curr_b is not None:
            path_b.append(curr_b)
            curr_b = parent_b.get(curr_b)

        full_path = path_f + path_b

        return {
            "found": True,
            "path": full_path,
            "distance": mu,
            "meeting_node": best_meeting_node,
            "nodes_settled": nodes_settled,
        }
