"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DIJKSTRA SHORTEST PATH (ALGO-GRAPH-03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates single-source shortest paths on non-negative weighted graphs
   using a min-priority queue (heap). Reconstructs full paths and path costs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O((V + E) log V)
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Any, Tuple


class GraphAlgoDijkstraShortestPath:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-03
      name: GraphAlgoDijkstraShortestPath
      version: 1.0.0
      category: graph
      capability_tags: [graph, pathfinding, dijkstra, weighted_shortest_path]
      inputs:
        type: object
        required: [weighted_edges, start_node]
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
      outputs:
        type: object
        required: [distances, paths]
        properties:
          distances:
            type: object
            additionalProperties: {type: number}
          paths:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O((V + E) log V)
        space: O(V)
      preconditions:
        - len(input.start_node) > 0
      postconditions:
        - len(output.distances) >= 1
      compatible_adapters:
        - ADAPTER-GRAPH-TO-SHORTEST-PATH
    ---
    """

    @staticmethod
    def compute(
        weighted_edges: List[Dict[str, Any]],
        start_node: str,
        target_node: Optional[str] = None,
    ) -> Dict[str, Any]:
        adj: Dict[str, List[Tuple[str, float]]] = {}
        all_nodes = {start_node}
        for edge in weighted_edges:
            u, v, w = edge["source"], edge["target"], float(edge["weight"])
            all_nodes.add(u)
            all_nodes.add(v)
            if u not in adj:
                adj[u] = []
            adj[u].append((v, w))

        distances: Dict[str, float] = {node: float("inf") for node in all_nodes}
        predecessors: Dict[str, Optional[str]] = {node: None for node in all_nodes}
        distances[start_node] = 0.0

        pq: List[Tuple[float, str]] = [(0.0, start_node)]

        while pq:
            curr_dist, u = heapq.heappop(pq)
            if curr_dist > distances[u]:
                continue
            if target_node and u == target_node:
                break

            for v, w in adj.get(u, []):
                new_dist = curr_dist + w
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    predecessors[v] = u
                    heapq.heappush(pq, (new_dist, v))

        paths: Dict[str, List[str]] = {}
        for node in all_nodes:
            if distances[node] < float("inf"):
                path: List[str] = []
                curr: Optional[str] = node
                while curr is not None:
                    path.append(curr)
                    curr = predecessors[curr]
                path.reverse()
                paths[node] = path

        return {
            "distances": {k: v for k, v in distances.items() if v < float("inf")},
            "paths": paths,
            "target_distance": distances.get(target_node) if target_node else None,
            "target_path": paths.get(target_node) if target_node else None,
        }
