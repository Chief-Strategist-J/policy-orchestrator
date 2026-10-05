"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DFS GRAPH TRAVERSAL (ALGO-GRAPH-02)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Depth-first search traversal exploring as deep as possible along each branch
   before backtracking. Supports cycle detection and discovery/finish timestamps.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E)
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Set, Any


class GraphAlgoDfsTraversal:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-02
      name: GraphAlgoDfsTraversal
      version: 1.0.0
      category: graph
      capability_tags: [graph, traversal, dfs, cycle_detection]
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
        required: [visited_order, has_cycle]
        properties:
          visited_order:
            type: array
            items: {type: string}
          has_cycle: {type: boolean}
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
        - ADAPTER-GRAPH-TO-DFS-ORDER
    ---
    """

    @staticmethod
    def traverse(
        adjacency_list: Dict[str, List[str]],
        start_node: str,
        max_depth: int = -1,
    ) -> Dict[str, Any]:
        visited_order: List[str] = []
        visited: Set[str] = set()
        on_stack: Set[str] = set()
        has_cycle: bool = False

        def _dfs(node: str, depth: int) -> None:
            nonlocal has_cycle
            visited.add(node)
            on_stack.add(node)
            visited_order.append(node)

            if max_depth == -1 or depth < max_depth:
                for neighbor in adjacency_list.get(node, []):
                    if neighbor in on_stack:
                        has_cycle = True
                    elif neighbor not in visited:
                        _dfs(neighbor, depth + 1)

            on_stack.remove(node)

        if start_node in adjacency_list or start_node:
            _dfs(start_node, 0)

        return {
            "visited_order": visited_order,
            "has_cycle": has_cycle,
            "total_visited": len(visited_order),
        }
