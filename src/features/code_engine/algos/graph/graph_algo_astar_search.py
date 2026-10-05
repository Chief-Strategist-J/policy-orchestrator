"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: A* HEURISTIC GRAPH SEARCH (ALGO-GRAPH-04)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Informed graph search algorithm using evaluation function f(n) = g(n) + h(n)
   where g(n) is the exact cost from start to n and h(n) is an admissible heuristic
   estimate from n to target. Finds the optimal path with fewer node expansions.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E) best case, O(b^d) worst case.
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Any, Tuple


class GraphAlgoAstarSearch:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-04
      name: GraphAlgoAstarSearch
      version: 1.0.0
      category: graph
      capability_tags: [graph, pathfinding, astar, heuristic_search]
      inputs:
        type: object
        required: [weighted_edges, start_node, target_node]
        properties:
          weighted_edges:
            type: array
            items:
              type: object
              required: [source, target, weight]
              properties:
                source: {type: string}
                target: {type: string}
                weight: {type: number}
          start_node: {type: string}
          target_node: {type: string}
          heuristics:
            type: object
            additionalProperties: {type: number}
      outputs:
        type: object
        required: [found, path, cost, nodes_expanded]
        properties:
          found: {type: boolean}
          path:
            type: array
            items: {type: string}
          cost: {type: number}
          nodes_expanded: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(E)
        space: O(V)
      preconditions:
        - len(input.start_node) > 0
        - len(input.target_node) > 0
      postconditions:
        - output.nodes_expanded >= 0
      compatible_adapters:
        - ADAPTER-GRAPH-TO-ASTAR-PATH
    ---
    """

    @staticmethod
    def search(
        weighted_edges: List[Dict[str, Any]],
        start_node: str,
        target_node: str,
        heuristics: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        h = heuristics or {}
        adj: Dict[str, List[Tuple[str, float]]] = {}
        for edge in weighted_edges:
            u, v, w = edge["source"], edge["target"], float(edge["weight"])
            if u not in adj:
                adj[u] = []
            adj[u].append((v, w))

        g_score: Dict[str, float] = {start_node: 0.0}
        f_score: Dict[str, float] = {start_node: h.get(start_node, 0.0)}
        came_from: Dict[str, str] = {}

        open_set: List[Tuple[float, str]] = [(f_score[start_node], start_node)]
        open_set_nodes = {start_node}
        nodes_expanded = 0

        while open_set:
            _, curr = heapq.heappop(open_set)
            open_set_nodes.discard(curr)
            nodes_expanded += 1

            if curr == target_node:
                path = [curr]
                while curr in came_from:
                    curr = came_from[curr]
                    path.append(curr)
                path.reverse()
                return {
                    "found": True,
                    "path": path,
                    "cost": g_score[target_node],
                    "nodes_expanded": nodes_expanded,
                }

            for neighbor, weight in adj.get(curr, []):
                tentative_g = g_score[curr] + weight
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = curr
                    g_score[neighbor] = tentative_g
                    f = tentative_g + h.get(neighbor, 0.0)
                    f_score[neighbor] = f
                    if neighbor not in open_set_nodes:
                        open_set_nodes.add(neighbor)
                        heapq.heappush(open_set, (f, neighbor))

        return {
            "found": False,
            "path": [],
            "cost": float("inf"),
            "nodes_expanded": nodes_expanded,
        }
