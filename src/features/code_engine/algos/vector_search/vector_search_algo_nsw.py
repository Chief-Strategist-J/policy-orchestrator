"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NAVIGABLE SMALL WORLD GRAPH (ALGO-VEC-SRCH-65)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Navigable Small World (NSW) proximity graph construction and greedy routing (#65).
   Vectors are sequentially inserted and linked to their nearest neighbors in the
   current graph. Early insertions form long-range highway shortcuts while later
   insertions form dense local clustering. Greedy best-first routing traverses long
   links across metric space followed by short-range convergence.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(log N) average routing, O(N log N) index construction.
   - Space Complexity: O(N * M) edge storage.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoNSW:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-65
      name: VectorSearchAlgoNSW
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, nsw, small_world, routing]
      inputs:
        type: object
        required: [vectors]
        properties:
          vectors:
            type: array
            items: {type: array, items: {type: number}}
          query:
            type: array
            items: {type: number}
          k: {type: integer, default: 5}
          max_edges: {type: integer, default: 6}
          num_attempts: {type: integer, default: 3}
      outputs:
        type: object
        required: [total_nodes, max_edges, neighbors]
        properties:
          total_nodes: {type: integer}
          max_edges: {type: integer}
          entry_point: {type: integer}
          neighbors:
            type: array
            items: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(log N)
        space: O(N * M)
      preconditions:
        - len(vectors) > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-GRAPH-KNN
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        max_edges: int = 6,
        num_attempts: int = 3,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"total_nodes": 0, "max_edges": max_edges, "entry_point": -1, "neighbors": []}

        n = len(vectors)
        adjacency: Dict[int, List[int]] = {i: [] for i in range(n)}

        for i in range(n):
            if i == 0:
                continue
            candidates: List[Tuple[float, int]] = []
            for j in range(i):
                d = cls._euclidean_distance(vectors[i], vectors[j])
                candidates.append((d, j))
            candidates.sort(key=lambda x: x[0])
            for d, target in candidates[:max_edges]:
                if target not in adjacency[i]:
                    adjacency[i].append(target)
                if i not in adjacency[target] and len(adjacency[target]) < max_edges * 2:
                    adjacency[target].append(i)

        entry_point = 0
        if query is None:
            return {
                "total_nodes": n,
                "max_edges": max_edges,
                "entry_point": entry_point,
                "neighbors": [],
                "adjacency": adjacency,
            }

        visited: Dict[int, float] = {}
        for attempt in range(min(num_attempts, n)):
            curr = attempt % n
            curr_dist = cls._euclidean_distance(query, vectors[curr])
            visited[curr] = curr_dist
            improved = True
            while improved:
                improved = False
                for neighbor in adjacency[curr]:
                    if neighbor not in visited:
                        ndist = cls._euclidean_distance(query, vectors[neighbor])
                        visited[neighbor] = ndist
                    else:
                        ndist = visited[neighbor]
                    if ndist < curr_dist:
                        curr_dist = ndist
                        curr = neighbor
                        improved = True

        sorted_results = sorted(visited.items(), key=lambda x: x[1])[:k]
        result_items = [
            {"id": node_id, "distance": dist, "vector": vectors[node_id]}
            for node_id, dist in sorted_results
        ]

        return {
            "total_nodes": n,
            "max_edges": max_edges,
            "entry_point": entry_point,
            "neighbors": result_items,
        }
