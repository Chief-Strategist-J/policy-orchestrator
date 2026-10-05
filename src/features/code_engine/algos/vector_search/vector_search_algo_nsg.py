"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NAVIGATING SPREADING-OUT GRAPH (ALGO-VEC-SRCH-71)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Navigating Spreading-out Graph (NSG) index construction and routing (#71). Builds
   a single-layer monotonic relative neighborhood graph starting from an approximate
   kNN graph and a central navigating entry node. Prunes candidate edges via the
   MRNG edge selection property (no edge pq if there exists r such that pr and qr
   are strictly shorter than pq), followed by a connectivity spanning repair to
   guarantee reachability.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N * kNN + N * Search) build, O(log N) query traversal.
   - Space Complexity: O(N * R) sparse navigable graph.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoNSG:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-71
      name: VectorSearchAlgoNSG
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, nsg, mrng, routing]
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
          candidate_pool_size: {type: integer, default: 16}
      outputs:
        type: object
        required: [total_nodes, navigating_node, r_max_degree, neighbors]
        properties:
          total_nodes: {type: integer}
          navigating_node: {type: integer}
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
        time: O(log N)
        space: O(N * R)
      preconditions:
        - len(vectors) > 0
        - r_max_degree > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-NSG-GRAPH
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def find_navigating_node(cls, vectors: List[List[float]]) -> int:
        n = len(vectors)
        if n == 0:
            return -1
        dim = len(vectors[0])
        mean_vec = [sum(vectors[i][d] for i in range(n)) / n for d in range(dim)]
        best_idx = 0
        min_d = float("inf")
        for i in range(n):
            d = cls._euclidean_distance(mean_vec, vectors[i])
            if d < min_d:
                min_d = d
                best_idx = i
        return best_idx

    @classmethod
    def mrng_prune(
        cls,
        base_idx: int,
        candidates: List[int],
        vectors: List[List[float]],
        r_max: int,
    ) -> List[int]:
        base_vec = vectors[base_idx]
        sorted_candidates: List[Tuple[float, int]] = []
        for c in candidates:
            if c != base_idx:
                d = cls._euclidean_distance(base_vec, vectors[c])
                sorted_candidates.append((d, c))
        sorted_candidates.sort(key=lambda x: x[0])

        selected: List[int] = []
        for dist_c, c in sorted_candidates:
            if len(selected) >= r_max:
                break
            vec_c = vectors[c]
            keep = True
            for s in selected:
                vec_s = vectors[s]
                d_c_s = cls._euclidean_distance(vec_c, vec_s)
                if d_c_s < dist_c:
                    keep = False
                    break
            if keep:
                selected.append(c)

        return selected

    @classmethod
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        r_max_degree: int = 8,
        candidate_pool_size: int = 16,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"total_nodes": 0, "navigating_node": -1, "r_max_degree": r_max_degree, "neighbors": []}

        n = len(vectors)
        nav_node = cls.find_navigating_node(vectors)
        adjacency: Dict[int, List[int]] = {i: [] for i in range(n)}

        for i in range(n):
            initial_pool = sorted(
                range(n),
                key=lambda j: cls._euclidean_distance(vectors[i], vectors[j])
            )[:min(n, candidate_pool_size + 1)]

            selected = cls.mrng_prune(i, initial_pool, vectors, r_max_degree)
            adjacency[i] = selected

        visited_nodes: Set[int] = set()
        queue = [nav_node]
        while queue:
            curr = queue.pop(0)
            if curr not in visited_nodes:
                visited_nodes.add(curr)
                for neighbor in adjacency[curr]:
                    if neighbor not in visited_nodes:
                        queue.append(neighbor)

        for i in range(n):
            if i not in visited_nodes:
                adjacency[nav_node].append(i)
                visited_nodes.add(i)

        neighbors: List[Dict[str, Any]] = []
        if query is not None:
            curr = nav_node
            curr_dist = cls._euclidean_distance(query, vectors[curr])
            visited: Set[int] = {curr}
            best_results: List[Tuple[float, int]] = [(curr_dist, curr)]

            improved = True
            while improved:
                improved = False
                for neighbor in adjacency[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        ndist = cls._euclidean_distance(query, vectors[neighbor])
                        best_results.append((ndist, neighbor))
                        if ndist < curr_dist:
                            curr_dist = ndist
                            curr = neighbor
                            improved = True

            best_results.sort(key=lambda x: x[0])
            top_k = best_results[:k]
            neighbors = [
                {"id": idx, "distance": d, "vector": vectors[idx]}
                for d, idx in top_k
            ]

        return {
            "total_nodes": n,
            "navigating_node": nav_node,
            "r_max_degree": r_max_degree,
            "neighbors": neighbors,
            "adjacency": {str(k_): v_ for k_, v_ in adjacency.items()},
        }
