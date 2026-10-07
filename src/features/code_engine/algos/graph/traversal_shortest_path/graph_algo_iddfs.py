"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ITERATIVE DEEPENING DFS (ALGO-GRAPH-TRV-15)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Iterative Deepening Depth-First Search (IDDFS) performs repeated depth-limited
   DFS passes with monotonically increasing depth ceilings. Combines the completeness
   and unweighted optimality of BFS with the O(depth) memory footprint of DFS.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(b^d) for branching factor b and solution depth d.
   - Space Complexity: O(d) bounded memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guardrails: Maximum depth cap enforced to prevent non-terminating explorations.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoIddfs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-15
      name: GraphAlgoIddfs
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, iddfs, iterative_deepening, memory_bounded]
      inputs:
        type: object
        required: [adjacency_list, start_node, target_node]
        properties:
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          start_node: {type: string}
          target_node: {type: string}
      outputs:
        type: object
        required: [found, path, depth, nodes_expanded]
      parameters:
        max_search_depth: {type: integer, default: 50}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(b^d)
        space: O(d)
    ---
    """

    @staticmethod
    def search(
        adjacency_list: Dict[str, List[str]],
        start_node: str,
        target_node: str,
        max_search_depth: int = 50,
    ) -> Dict[str, Any]:
        if start_node == target_node:
            return {
                "found": True,
                "path": [start_node],
                "depth": 0,
                "nodes_expanded": 1,
            }

        total_nodes_expanded = 0

        for limit in range(1, max_search_depth + 1):
            stack: List[Tuple[str, int, List[str]]] = [(start_node, 0, [start_node])]
            seen_in_path: set = {start_node}

            while stack:
                curr, depth, path = stack.pop()
                total_nodes_expanded += 1

                if curr == target_node:
                    return {
                        "found": True,
                        "path": path,
                        "depth": depth,
                        "nodes_expanded": total_nodes_expanded,
                    }

                if depth < limit:
                    neighbors = adjacency_list.get(curr, [])
                    for nb in reversed(neighbors):
                        if nb not in path:
                            stack.append((nb, depth + 1, path + [nb]))

        return {
            "found": False,
            "path": [],
            "depth": -1,
            "nodes_expanded": total_nodes_expanded,
        }
