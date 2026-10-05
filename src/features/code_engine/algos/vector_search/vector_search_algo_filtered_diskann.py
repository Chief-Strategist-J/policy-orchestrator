"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILTERED-DISKANN (ALGO-VEC-SRCH-75)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Label-aware proximity graph index and constrained traversal (#75).
   Addresses extreme categorical selectivity (tenancy, access privileges, classification):
   maintains dedicated label-specific entry points (label medoids) and executes
   label-constrained beam search, navigating exclusively across nodes that satisfy the
   target metadata label. Strictly guarantees VG1 invariant (in-index filtration).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(L) disk/hop evaluations restricted to filtered subgraphs.
   - Space Complexity: O(N * R) adjacency with label indices.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import heapq
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoFilteredDiskANN:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-75
      name: VectorSearchAlgoFilteredDiskANN
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, filtered_search, diskann, label_aware]
      inputs:
        type: object
        required: [vectors, labels, query, target_label]
        properties:
          vectors:
            type: array
            items: {type: array, items: {type: number}}
          labels:
            type: array
            items: {type: string}
          query:
            type: array
            items: {type: number}
          target_label: {type: string}
          k: {type: integer, default: 5}
          ef_search: {type: integer, default: 16}
          r_max_degree: {type: integer, default: 8}
      outputs:
        type: object
        required: [target_label, matching_points, label_entry_point, neighbors]
        properties:
          target_label: {type: string}
          matching_points: {type: integer}
          label_entry_point: {type: integer}
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
        time: O(L)
        space: O(N * R)
      preconditions:
        - len(vectors) == len(labels)
        - len(vectors) > 0
      postconditions:
        - all(n['label'] == input.target_label for n in output.neighbors)
      compatible_adapters:
        - ADAPTER-FILTERED-KNN
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def find_label_medoid(
        cls,
        vectors: List[List[float]],
        matching_indices: List[int],
    ) -> int:
        if not matching_indices:
            return -1
        dim = len(vectors[0])
        centroid = [
            sum(vectors[idx][d] for idx in matching_indices) / len(matching_indices)
            for d in range(dim)
        ]
        best_idx = matching_indices[0]
        min_d = float("inf")
        for idx in matching_indices:
            d = cls._euclidean_distance(centroid, vectors[idx])
            if d < min_d:
                min_d = d
                best_idx = idx
        return best_idx

    @classmethod
    def search_filtered(
        cls,
        vectors: List[List[float]],
        labels: List[str],
        query: List[float],
        target_label: str,
        k: int = 5,
        ef_search: int = 16,
        r_max_degree: int = 8,
    ) -> Dict[str, Any]:
        n = len(vectors)
        matching = [i for i, lbl in enumerate(labels) if lbl == target_label]

        if not matching:
            return {
                "target_label": target_label,
                "matching_points": 0,
                "label_entry_point": -1,
                "neighbors": [],
            }

        label_medoid = cls.find_label_medoid(vectors, matching)

        label_graph: Dict[int, List[int]] = {}
        for idx in matching:
            other_matching = [other for other in matching if other != idx]
            other_matching.sort(key=lambda o: cls._euclidean_distance(vectors[idx], vectors[o]))
            label_graph[idx] = other_matching[:r_max_degree]

        actual_ef = max(ef_search, k)
        visited: Set[int] = {label_medoid}
        candidates: List[Tuple[float, int]] = []
        w_results: List[Tuple[float, int]] = []

        d_init = cls._euclidean_distance(query, vectors[label_medoid])
        heapq.heappush(candidates, (d_init, label_medoid))
        heapq.heappush(w_results, (-d_init, label_medoid))

        while candidates:
            c_dist, c_node = heapq.heappop(candidates)
            worst_dist = -w_results[0][0]

            if c_dist > worst_dist and len(w_results) >= actual_ef:
                break

            for neighbor in label_graph.get(c_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    ndist = cls._euclidean_distance(query, vectors[neighbor])
                    worst_dist = -w_results[0][0]

                    if ndist < worst_dist or len(w_results) < actual_ef:
                        heapq.heappush(candidates, (ndist, neighbor))
                        heapq.heappush(w_results, (-ndist, neighbor))
                        if len(w_results) > actual_ef:
                            heapq.heappop(w_results)

        final_candidates = [(-d, idx) for d, idx in w_results]
        final_candidates.sort(key=lambda x: x[0])
        top_k = final_candidates[:k]

        return {
            "target_label": target_label,
            "matching_points": len(matching),
            "label_entry_point": label_medoid,
            "neighbors": [
                {
                    "id": idx,
                    "distance": d,
                    "label": labels[idx],
                    "vector": vectors[idx],
                }
                for d, idx in top_k
            ],
        }
