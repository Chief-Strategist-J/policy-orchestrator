"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MULTI-SOURCE BFS & VORONOI (ALGO-GRAPH-TRV-24)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Multi-Source Breadth-First Search initiates wavefront expansion from multiple
   starting seeds concurrently. Computes the minimum distance to the closest
   source node and assigns every vertex to its owning source cell, generating
   discrete graph Voronoi diagrams for catchment area modeling and facility assignment.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) strictly linear across all partitions.
   - Space Complexity: O(V) for closest source, distance, and parent maps.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Any, Set, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoMultiSourceBfs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-24
      name: GraphAlgoMultiSourceBfs
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, multi_source_bfs, voronoi_partition, catchment_areas]
      inputs:
        type: object
        required: [adjacency_list, source_nodes]
        properties:
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          source_nodes:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [distances, closest_sources, voronoi_cells, total_reachable]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    @staticmethod
    def traverse(
        adjacency_list: Dict[str, List[str]],
        source_nodes: List[str],
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(adjacency_list.keys()))
        distances: Dict[str, int] = {n: -1 for n in all_nodes}
        closest_source: Dict[str, Optional[str]] = {n: None for n in all_nodes}
        parents: Dict[str, Optional[str]] = {n: None for n in all_nodes}

        queue: deque[str] = deque()
        valid_sources = sorted(list(set(source_nodes)))

        for src in valid_sources:
            if src in distances:
                distances[src] = 0
                closest_source[src] = src
                queue.append(src)

        while queue:
            curr = queue.popleft()
            curr_dist = distances[curr]
            curr_src = closest_source[curr]

            for neighbor in adjacency_list.get(curr, []):
                if distances.get(neighbor, -1) == -1:
                    distances[neighbor] = curr_dist + 1
                    closest_source[neighbor] = curr_src
                    parents[neighbor] = curr
                    queue.append(neighbor)

        voronoi_cells: Dict[str, List[str]] = {s: [] for s in valid_sources}
        for node, src in closest_source.items():
            if src is not None and distances[node] != -1:
                voronoi_cells[src].append(node)

        for s in voronoi_cells:
            voronoi_cells[s].sort()

        reachable_distances = {k: v for k, v in distances.items() if v != -1}

        return {
            "distances": reachable_distances,
            "closest_sources": {k: v for k, v in closest_source.items() if v is not None},
            "parents": {k: v for k, v in parents.items() if v is not None},
            "voronoi_cells": voronoi_cells,
            "total_reachable": len(reachable_distances),
            "num_sources": len(valid_sources),
        }
