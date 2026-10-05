"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BEAM SEARCH ON GRAPHS (ALGO-VEC-SRCH-68)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Bounded beam exploration on metric proximity graphs (#68). Tracks two worklists:
   a min-heap of active frontier candidates and a bounded result list of size ef
   (or L parameter). Prunes search paths immediately when the closest unexpanded
   frontier distance exceeds the current k-th or ef-th candidate, preventing
   redundant distance computations via an O(1) visited hash set.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(ef * d_avg) distance calculations.
   - Space Complexity: O(ef + |Visited|) memory footprint.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import heapq
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoBeamSearch:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-68
      name: VectorSearchAlgoBeamSearch
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, beam_search, ef_parameter, routing]
      inputs:
        type: object
        required: [vectors, adjacency, start_nodes, query]
        properties:
          vectors:
            type: array
            items: {type: array, items: {type: number}}
          adjacency:
            type: object
            additionalProperties: {type: array, items: {type: integer}}
          start_nodes:
            type: array
            items: {type: integer}
          query:
            type: array
            items: {type: number}
          k: {type: integer, default: 5}
          ef: {type: integer, default: 16}
      outputs:
        type: object
        required: [k, ef, distance_evaluations, visited_count, neighbors]
        properties:
          k: {type: integer}
          ef: {type: integer}
          distance_evaluations: {type: integer}
          visited_count: {type: integer}
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
        time: O(ef * log ef)
        space: O(ef)
      preconditions:
        - len(vectors) > 0
        - len(start_nodes) > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-BEAM-RESULTS
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def execute_beam_search(
        cls,
        vectors: List[List[float]],
        adjacency: Dict[str, List[int]],
        start_nodes: List[int],
        query: List[float],
        k: int = 5,
        ef: int = 16,
    ) -> Dict[str, Any]:
        if not vectors or not start_nodes:
            return {
                "k": k,
                "ef": ef,
                "distance_evaluations": 0,
                "visited_count": 0,
                "neighbors": [],
            }

        actual_ef = max(ef, k)
        visited: Set[int] = set()
        dist_evals = 0

        candidates: List[Tuple[float, int]] = []
        w_results: List[Tuple[float, int]] = []

        for sn in start_nodes:
            if 0 <= sn < len(vectors):
                visited.add(sn)
                d = cls._euclidean_distance(query, vectors[sn])
                dist_evals += 1
                heapq.heappush(candidates, (d, sn))
                heapq.heappush(w_results, (-d, sn))

        while candidates:
            c_dist, c_node = heapq.heappop(candidates)
            worst_dist = -w_results[0][0]

            if c_dist > worst_dist and len(w_results) >= actual_ef:
                break

            neighbors = adjacency.get(str(c_node), adjacency.get(c_node, []))
            for n_idx in neighbors:
                if n_idx not in visited and 0 <= n_idx < len(vectors):
                    visited.add(n_idx)
                    d = cls._euclidean_distance(query, vectors[n_idx])
                    dist_evals += 1
                    worst_dist = -w_results[0][0]

                    if d < worst_dist or len(w_results) < actual_ef:
                        heapq.heappush(candidates, (d, n_idx))
                        heapq.heappush(w_results, (-d, n_idx))
                        if len(w_results) > actual_ef:
                            heapq.heappop(w_results)

        final_candidates = [(-d, idx) for d, idx in w_results]
        final_candidates.sort(key=lambda x: x[0])
        top_k = final_candidates[:k]

        return {
            "k": k,
            "ef": actual_ef,
            "distance_evaluations": dist_evals,
            "visited_count": len(visited),
            "neighbors": [
                {"id": idx, "distance": d, "vector": vectors[idx]}
                for d, idx in top_k
            ],
        }
