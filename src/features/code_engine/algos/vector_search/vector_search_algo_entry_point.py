"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ENTRY-POINT SELECTION (ALGO-VEC-SRCH-73)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Adaptive and geometric entry-point selection for metric proximity graph routing (#73).
   Avoids disconnected trapping and minimizes path hops across multi-modal vector distributions:
   supports (1) global medoid calculation, (2) dispersed multi-seed initialization via
   furthest point sampling (FPS), and (3) query-adaptive entry-point selection routing
   to the nearest cluster centroid seed.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N * D) medoid/FPS, O(S * D) per-query seed selection.
   - Space Complexity: O(S) seed index cache.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple


class VectorSearchAlgoEntryPoint:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-73
      name: VectorSearchAlgoEntryPoint
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, entry_point, medoid, furthest_point_sampling]
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
          strategy:
            type: string
            enum: [medoid, multi_seed, query_adaptive]
            default: query_adaptive
          num_seeds: {type: integer, default: 4}
      outputs:
        type: object
        required: [strategy, selected_entry_point, seed_indices]
        properties:
          strategy: {type: string}
          selected_entry_point: {type: integer}
          seed_indices:
            type: array
            items: {type: integer}
          seed_distances:
            type: array
            items: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(S * D)
        space: O(S)
      preconditions:
        - len(vectors) > 0
        - num_seeds > 0
      postconditions:
        - 0 <= output.selected_entry_point < len(input.vectors)
      compatible_adapters:
        - ADAPTER-GRAPH-ENTRY-POINTS
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def calculate_medoid(cls, vectors: List[List[float]]) -> int:
        n = len(vectors)
        if n == 0:
            return 0
        dim = len(vectors[0])
        centroid = [sum(vectors[i][d] for i in range(n)) / n for d in range(dim)]
        best_idx = 0
        min_dist = float("inf")
        for i in range(n):
            d = cls._euclidean_distance(centroid, vectors[i])
            if d < min_dist:
                min_dist = d
                best_idx = i
        return best_idx

    @classmethod
    def furthest_point_sampling(
        cls,
        vectors: List[List[float]],
        num_seeds: int,
    ) -> List[int]:
        n = len(vectors)
        if n <= num_seeds:
            return list(range(n))

        first_seed = cls.calculate_medoid(vectors)
        seeds: List[int] = [first_seed]
        min_distances = [cls._euclidean_distance(vectors[i], vectors[first_seed]) for i in range(n)]

        while len(seeds) < num_seeds:
            next_seed = max(range(n), key=lambda i: min_distances[i])
            seeds.append(next_seed)
            for i in range(n):
                d = cls._euclidean_distance(vectors[i], vectors[next_seed])
                if d < min_distances[i]:
                    min_distances[i] = d

        return seeds

    @classmethod
    def select_entry_point(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        strategy: str = "query_adaptive",
        num_seeds: int = 4,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "strategy": strategy,
                "selected_entry_point": -1,
                "seed_indices": [],
                "seed_distances": [],
            }

        n = len(vectors)
        k_seeds = min(num_seeds, n)

        if strategy == "medoid":
            medoid = cls.calculate_medoid(vectors)
            return {
                "strategy": "medoid",
                "selected_entry_point": medoid,
                "seed_indices": [medoid],
                "seed_distances": [cls._euclidean_distance(query, vectors[medoid])] if query else [0.0],
            }

        seeds = cls.furthest_point_sampling(vectors, k_seeds)

        if query is None or strategy == "multi_seed":
            return {
                "strategy": strategy,
                "selected_entry_point": seeds[0],
                "seed_indices": seeds,
                "seed_distances": [],
            }

        seed_dists = [cls._euclidean_distance(query, vectors[s]) for s in seeds]
        best_seed_idx = min(range(len(seeds)), key=lambda i: seed_dists[i])
        selected = seeds[best_seed_idx]

        return {
            "strategy": strategy,
            "selected_entry_point": selected,
            "seed_indices": seeds,
            "seed_distances": seed_dists,
        }
