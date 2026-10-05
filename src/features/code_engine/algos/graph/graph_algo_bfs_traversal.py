"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BFS GRAPH TRAVERSAL (ALGO-GRAPH-01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Breadth-first search traversal exploring all neighboring nodes level by level.
   Computes distances and predecessor trees from single or multi-source starting nodes.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E)
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Set, Any


class GraphAlgoBfsTraversal:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-01
      name: GraphAlgoBfsTraversal
      version: 1.0.0
      category: graph
      capability_tags: [graph, traversal, bfs, shortest_path_unweighted]
      inputs:
        type: object
        required: [adjacency_list, start_node]
        properties:
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          start_node: {type: string}
      outputs:
        type: object
        required: [visited_order, distances]
        properties:
          visited_order:
            type: array
            items: {type: string}
          distances:
            type: object
            additionalProperties: {type: integer}
      parameters:
        max_depth: {type: integer, default: -1}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(V + E)
        space: O(V)
      preconditions:
        - len(input.start_node) > 0
      postconditions:
        - len(output.visited_order) >= 1
      compatible_adapters:
        - ADAPTER-GRAPH-TO-BFS-ORDER
    ---
    """

    @staticmethod
    def traverse(
        adjacency_list: Dict[str, List[str]],
        start_node: str,
        max_depth: int = -1,
    ) -> Dict[str, Any]:
        if start_node not in adjacency_list and start_node:
            adjacency_list = {**adjacency_list, start_node: []}

        visited_order: List[str] = []
        distances: Dict[str, int] = {start_node: 0}
        queue: deque = deque([start_node])
        seen: Set[str] = {start_node}

        while queue:
            curr = queue.popleft()
            visited_order.append(curr)
            curr_dist = distances[curr]

            if max_depth != -1 and curr_dist >= max_depth:
                continue

            for neighbor in adjacency_list.get(curr, []):
                if neighbor not in seen:
                    seen.add(neighbor)
                    distances[neighbor] = curr_dist + 1
                    queue.append(neighbor)

        return {
            "visited_order": visited_order,
            "distances": distances,
            "total_visited": len(visited_order),
        }
