"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: 0-1 BFS SHORTEST PATH (ALGO-GRAPH-TRV-21)
================================================================================

1. OVERVIEW & OBJECTIVE:
   0-1 Breadth-First Search computes exact shortest paths on graphs with binary
   edge weights {0, 1} in strict O(V + E) linear time. Utilizes a double-ended
   queue (deque), pushing 0-weight relaxed edges to the front and 1-weight edges
   to the back, eliminating priority queue log(V) heap overheads.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) strictly linear.
   - Space Complexity: O(V) for distance table and deque.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: All edge weights must belong strictly to {0, 1}.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoZeroOneBfs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-21
      name: GraphAlgoZeroOneBfs
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, 0_1_bfs, binary_weights, linear_shortest_path]
      inputs:
        type: object
        required: [weighted_adjacency, start_node]
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
                  weight: {type: integer, enum: [0, 1]}
          start_node: {type: string}
          target_node: {type: string}
      outputs:
        type: object
        required: [distances, parents, shortest_path_to_target]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    @staticmethod
    def compute(
        weighted_adjacency: Dict[str, List[Dict[str, Any]]],
        start_node: str,
        target_node: Optional[str] = None,
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(weighted_adjacency.keys()))
        distances: Dict[str, float] = {n: float("inf") for n in all_nodes}
        parents: Dict[str, Optional[str]] = {n: None for n in all_nodes}

        distances[start_node] = 0
        queue: deque[str] = deque([start_node])

        while queue:
            curr = queue.popleft()
            curr_dist = distances[curr]

            if target_node is not None and curr == target_node:
                pass

            for edge in weighted_adjacency.get(curr, []):
                tgt = str(edge["target"])
                wt = int(edge.get("weight", 1))
                if wt not in (0, 1):
                    continue

                if curr_dist + wt < distances.get(tgt, float("inf")):
                    distances[tgt] = curr_dist + wt
                    parents[tgt] = curr
                    if wt == 0:
                        queue.appendleft(tgt)
                    else:
                        queue.append(tgt)

        shortest_path: List[str] = []
        if target_node and distances.get(target_node, float("inf")) != float("inf"):
            curr_t = target_node
            while curr_t is not None:
                shortest_path.append(curr_t)
                curr_t = parents.get(curr_t)
            shortest_path = shortest_path[::-1]

        valid_distances = {k: int(v) for k, v in distances.items() if v != float("inf")}

        return {
            "distances": valid_distances,
            "parents": {k: v for k, v in parents.items() if distances.get(k, float("inf")) != float("inf")},
            "shortest_path_to_target": shortest_path,
            "target_distance": valid_distances.get(target_node, -1) if target_node else None,
            "total_reachable": len(valid_distances),
        }
