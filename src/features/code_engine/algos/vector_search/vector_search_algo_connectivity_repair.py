"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH CONNECTIVITY REPAIR (ALGO-VEC-SRCH-74)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Proximity graph connectivity audit and automated reachability repair (#74).
   Detects isolated vector nodes ("islands") and zero in-degree dead-ends caused by
   asymmetric pruning or iterative record deletions. Executes a BFS reachability sweep
   from designated entry points, computes directed in-degree histograms, and repairs
   graph navigability by reconnecting unreachable components to their nearest reachable
   metric neighbors.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) reachability traversal + O(U * V_reachable) repair.
   - Space Complexity: O(V) visited and in-degree tracking maps.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
from collections import deque
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoConnectivityRepair:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-74
      name: VectorSearchAlgoConnectivityRepair
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, connectivity_repair, reachability, bfs]
      inputs:
        type: object
        required: [vectors, adjacency, entry_points]
        properties:
          vectors:
            type: array
            items: {type: array, items: {type: number}}
          adjacency:
            type: object
            additionalProperties: {type: array, items: {type: integer}}
          entry_points:
            type: array
            items: {type: integer}
      outputs:
        type: object
        required: [is_fully_connected, unreachable_count, zero_indegree_count, repaired_edges_added, repaired_adjacency]
        properties:
          is_fully_connected: {type: boolean}
          unreachable_count: {type: integer}
          unreachable_nodes:
            type: array
            items: {type: integer}
          zero_indegree_count: {type: integer}
          repaired_edges_added: {type: integer}
          repaired_adjacency:
            type: object
            additionalProperties: {type: array, items: {type: integer}}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(V + E + U * V)
        space: O(V)
      preconditions:
        - len(vectors) > 0
        - len(entry_points) > 0
      postconditions:
        - output.unreachable_count >= 0
      compatible_adapters:
        - ADAPTER-REPAIRED-GRAPH
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def audit_and_repair(
        cls,
        vectors: List[List[float]],
        adjacency: Dict[str, List[int]],
        entry_points: List[int],
    ) -> Dict[str, Any]:
        n = len(vectors)
        if n == 0:
            return {
                "is_fully_connected": True,
                "unreachable_count": 0,
                "unreachable_nodes": [],
                "zero_indegree_count": 0,
                "repaired_edges_added": 0,
                "repaired_adjacency": {},
            }

        graph: Dict[int, List[int]] = {
            int(k): [int(v) for v in vals if 0 <= int(v) < n]
            for k, vals in adjacency.items()
        }
        for i in range(n):
            if i not in graph:
                graph[i] = []

        in_degree: Dict[int, int] = {i: 0 for i in range(n)}
        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1

        zero_indegree = [i for i in range(n) if in_degree[i] == 0 and i not in entry_points]

        visited: Set[int] = set()
        queue = deque([ep for ep in entry_points if 0 <= ep < n])
        for ep in queue:
            visited.add(ep)

        while queue:
            curr = queue.popleft()
            for neighbor in graph.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        unreachable = [i for i in range(n) if i not in visited]
        repaired_edges_added = 0

        if unreachable:
            reachable_nodes = list(visited) if visited else [entry_points[0]]
            for unreach_idx in unreachable:
                best_reach = reachable_nodes[0]
                min_d = float("inf")
                for reach_idx in reachable_nodes:
                    d = cls._euclidean_distance(vectors[reach_idx], vectors[unreach_idx])
                    if d < min_d:
                        min_d = d
                        best_reach = reach_idx

                graph[best_reach].append(unreach_idx)
                graph[unreach_idx].append(best_reach)
                repaired_edges_added += 2
                reachable_nodes.append(unreach_idx)
                visited.add(unreach_idx)

        formatted_adj = {str(k_): v_ for k_, v_ in graph.items()}
        return {
            "is_fully_connected": len(unreachable) == 0,
            "unreachable_count": len(unreachable),
            "unreachable_nodes": unreachable,
            "zero_indegree_count": len(zero_indegree),
            "repaired_edges_added": repaired_edges_added,
            "repaired_adjacency": formatted_adj,
        }
