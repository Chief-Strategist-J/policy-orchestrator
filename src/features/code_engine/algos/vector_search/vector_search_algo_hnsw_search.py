"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HNSW SEARCH (ALGO-VEC-SRCH-66)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hierarchical Navigable Small World (HNSW) multilayer search (#66). Navigates a
   scale-free hierarchical graph hierarchy: performs greedy routing at coarse upper
   layers to locate optimal local entry points, then descends to dense layer 0 for
   bounded beam exploration with size ef >= k.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(log N) metric distance evaluations.
   - Space Complexity: O(ef) working set queue.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import heapq
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoHNSWSearch:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-66
      name: VectorSearchAlgoHNSWSearch
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, hnsw, hierarchical, search]
      inputs:
        type: object
        required: [vectors, layers, entry_point, top_layer, query]
        properties:
          vectors:
            type: array
            items: {type: array, items: {type: number}}
          layers:
            type: array
            items: {type: object}
          entry_point: {type: integer}
          top_layer: {type: integer}
          query:
            type: array
            items: {type: number}
          k: {type: integer, default: 5}
          ef: {type: integer, default: 16}
      outputs:
        type: object
        required: [k, ef, neighbors]
        properties:
          k: {type: integer}
          ef: {type: integer}
          distance_evaluations: {type: integer}
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
        space: O(ef)
      preconditions:
        - len(vectors) > 0
        - ef >= k
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-HNSW-RESULTS
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def search_layer(
        cls,
        query: List[float],
        vectors: List[List[float]],
        adjacency: Dict[str, List[int]],
        enter_points: List[int],
        ef: int,
    ) -> Tuple[List[Tuple[float, int]], int]:
        dist_evals = 0
        visited: Set[int] = set(enter_points)
        candidates: List[Tuple[float, int]] = []
        w_results: List[Tuple[float, int]] = []

        for ep in enter_points:
            d = cls._euclidean_distance(query, vectors[ep])
            dist_evals += 1
            heapq.heappush(candidates, (d, ep))
            heapq.heappush(w_results, (-d, ep))

        while candidates:
            c_dist, c_node = heapq.heappop(candidates)
            furthest_w_dist = -w_results[0][0]

            if c_dist > furthest_w_dist:
                break

            neighbors = adjacency.get(str(c_node), [])
            for n_node in neighbors:
                if n_node not in visited:
                    visited.add(n_node)
                    d = cls._euclidean_distance(query, vectors[n_node])
                    dist_evals += 1
                    furthest_w_dist = -w_results[0][0]

                    if d < furthest_w_dist or len(w_results) < ef:
                        heapq.heappush(candidates, (d, n_node))
                        heapq.heappush(w_results, (-d, n_node))
                        if len(w_results) > ef:
                            heapq.heappop(w_results)

        final_candidates = [(-d, node) for d, node in w_results]
        final_candidates.sort(key=lambda x: x[0])
        return final_candidates, dist_evals

    @classmethod
    def search(
        cls,
        vectors: List[List[float]],
        layers: List[Dict[str, Any]],
        entry_point: int,
        top_layer: int,
        query: List[float],
        k: int = 5,
        ef: int = 16,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"k": k, "ef": ef, "distance_evaluations": 0, "neighbors": []}

        actual_ef = max(ef, k)
        curr_ep = entry_point
        total_evals = 0

        for lc in range(top_layer, 0, -1):
            layer_adj = layers[lc] if lc < len(layers) else {}
            curr_dist = cls._euclidean_distance(query, vectors[curr_ep])
            total_evals += 1
            improved = True
            while improved:
                improved = False
                for neighbor in layer_adj.get(str(curr_ep), []):
                    ndist = cls._euclidean_distance(query, vectors[neighbor])
                    total_evals += 1
                    if ndist < curr_dist:
                        curr_dist = ndist
                        curr_ep = neighbor
                        improved = True

        layer0_adj = layers[0] if len(layers) > 0 else {}
        w, evals = cls.search_layer(query, vectors, layer0_adj, [curr_ep], actual_ef)
        total_evals += evals

        top_k = w[:k]
        neighbors = [
            {"id": node_id, "distance": dist, "vector": vectors[node_id]}
            for dist, node_id in top_k
        ]

        return {
            "k": k,
            "ef": actual_ef,
            "distance_evaluations": total_evals,
            "neighbors": neighbors,
        }
