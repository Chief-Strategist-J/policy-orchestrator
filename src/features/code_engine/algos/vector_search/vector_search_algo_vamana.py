"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VAMANA DISKANN GRAPH INDEX (ALGO-VEC-SRCH-69)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Vamana / DiskANN single-layer proximity graph index (#69). Engineered for SSD
   and hybrid DRAM-disk scale. Identifies the global geometric medoid as entry point,
   executes two-pass construction (first alpha = 1.0 for fine local geometry, second
   alpha > 1.0 for wide highway shortcuts), applying RobustPrune (#70) at every node.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N * L * log N) index construction, O(L) disk search path.
   - Space Complexity: O(N * R) fixed-degree adjacency.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import heapq
import math
from typing import Any, Dict, List, Optional, Set, Tuple
from src.features.code_engine.algos.vector_search.vector_search_algo_robust_prune import VectorSearchAlgoRobustPrune


class VectorSearchAlgoVamana:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-69
      name: VectorSearchAlgoVamana
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, vamana, diskann, ssd_scale]
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
          r_max_degree: {type: integer, default: 8}
          l_search_list_size: {type: integer, default: 16}
          alpha: {type: number, default: 1.2}
      outputs:
        type: object
        required: [total_nodes, medoid_entry_point, r_max_degree, neighbors]
        properties:
          total_nodes: {type: integer}
          medoid_entry_point: {type: integer}
          r_max_degree: {type: integer}
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
        - len(vectors) > 0
        - r_max_degree > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-DISKANN-INDEX
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def find_medoid(cls, vectors: List[List[float]]) -> int:
        n = len(vectors)
        if n == 0:
            return -1
        dim = len(vectors[0])
        centroid = [sum(vectors[i][d] for i in range(n)) / n for d in range(dim)]
        best_idx = 0
        best_dist = float("inf")
        for i in range(n):
            d = cls._euclidean_distance(centroid, vectors[i])
            if d < best_dist:
                best_dist = d
                best_idx = i
        return best_idx

    @classmethod
    def greedy_search(
        cls,
        query: List[float],
        vectors: List[List[float]],
        adjacency: Dict[int, List[int]],
        entry_point: int,
        l_size: int,
    ) -> List[Tuple[float, int]]:
        visited: Set[int] = {entry_point}
        candidates: List[Tuple[float, int]] = []
        w_results: List[Tuple[float, int]] = []

        d = cls._euclidean_distance(query, vectors[entry_point])
        heapq.heappush(candidates, (d, entry_point))
        heapq.heappush(w_results, (-d, entry_point))

        while candidates:
            c_dist, c_node = heapq.heappop(candidates)
            worst_dist = -w_results[0][0]

            if c_dist > worst_dist and len(w_results) >= l_size:
                break

            for neighbor in adjacency.get(c_node, []):
                if neighbor not in visited and 0 <= neighbor < len(vectors):
                    visited.add(neighbor)
                    ndist = cls._euclidean_distance(query, vectors[neighbor])
                    worst_dist = -w_results[0][0]

                    if ndist < worst_dist or len(w_results) < l_size:
                        heapq.heappush(candidates, (ndist, neighbor))
                        heapq.heappush(w_results, (-ndist, neighbor))
                        if len(w_results) > l_size:
                            heapq.heappop(w_results)

        results = [(-d, idx) for d, idx in w_results]
        results.sort(key=lambda x: x[0])
        return results

    @classmethod
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        r_max_degree: int = 8,
        l_search_list_size: int = 16,
        alpha: float = 1.2,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_nodes": 0,
                "medoid_entry_point": -1,
                "r_max_degree": r_max_degree,
                "neighbors": [],
            }

        n = len(vectors)
        medoid = cls.find_medoid(vectors)
        adjacency: Dict[int, List[int]] = {i: [] for i in range(n)}

        for pass_alpha in [1.0, alpha]:
            for i in range(n):
                path = cls.greedy_search(
                    vectors[i], vectors, adjacency, medoid, l_search_list_size
                )
                candidate_ids = [idx for _, idx in path if idx != i]
                candidate_vecs = [vectors[idx] for idx in candidate_ids]

                pruned = VectorSearchAlgoRobustPrune.prune(
                    point=vectors[i],
                    candidate_vectors=candidate_vecs,
                    candidate_ids=candidate_ids,
                    alpha=pass_alpha,
                    r_max_degree=r_max_degree,
                )
                adjacency[i] = pruned["selected_ids"]

                for target in adjacency[i]:
                    if i not in adjacency[target]:
                        adjacency[target].append(i)
                        if len(adjacency[target]) > r_max_degree:
                            t_candidates = [
                                vectors[other] for other in adjacency[target]
                            ]
                            t_pruned = VectorSearchAlgoRobustPrune.prune(
                                point=vectors[target],
                                candidate_vectors=t_candidates,
                                candidate_ids=adjacency[target],
                                alpha=pass_alpha,
                                r_max_degree=r_max_degree,
                            )
                            adjacency[target] = t_pruned["selected_ids"]

        neighbors: List[Dict[str, Any]] = []
        if query is not None:
            results = cls.greedy_search(
                query, vectors, adjacency, medoid, max(l_search_list_size, k)
            )
            top_k = results[:k]
            neighbors = [
                {"id": idx, "distance": d, "vector": vectors[idx]}
                for d, idx in top_k
            ]

        return {
            "total_nodes": n,
            "medoid_entry_point": medoid,
            "r_max_degree": r_max_degree,
            "neighbors": neighbors,
            "adjacency": {str(k_): v_ for k_, v_ in adjacency.items()},
        }
