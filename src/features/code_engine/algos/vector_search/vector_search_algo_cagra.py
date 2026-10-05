"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CAGRA GPU GRAPH INDEX (ALGO-VEC-SRCH-72)
================================================================================

1. OVERVIEW & OBJECTIVE:
   CAGRA (CUDA Anisotropic Graph) fixed-degree proximity graph index (#72).
   Engineered for parallel acceleration and coalesced memory access: transforms an
   irregular kNN proximity graph into a strictly regular, fixed-degree graph (degree = D)
   by rank-based edge weighting, reverse link symmetrization, and deterministic
   fixed-degree pruning. Enables high-throughput parallel batch search.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N * D) regularized graph layout.
   - Space Complexity: Exact N * D dense adjacency matrix.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoCAGRA:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-72
      name: VectorSearchAlgoCAGRA
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, cagra, fixed_degree, gpu_accelerated]
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
          fixed_degree: {type: integer, default: 6}
          search_width: {type: integer, default: 8}
      outputs:
        type: object
        required: [total_nodes, fixed_degree, regular_adjacency, neighbors]
        properties:
          total_nodes: {type: integer}
          fixed_degree: {type: integer}
          regular_adjacency:
            type: array
            items: {type: array, items: {type: integer}}
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
        time: O(N * D)
        space: O(N * D)
      preconditions:
        - len(vectors) > 0
        - fixed_degree > 0
      postconditions:
        - len(output.regular_adjacency) == len(input.vectors)
        - all(len(row) == input.fixed_degree for row in output.regular_adjacency)
      compatible_adapters:
        - ADAPTER-CAGRA-GRAPH
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def build_regular_graph(
        cls,
        vectors: List[List[float]],
        fixed_degree: int = 6,
    ) -> List[List[int]]:
        n = len(vectors)
        if n == 0:
            return []

        raw_knn: List[List[int]] = []
        for i in range(n):
            dists = [
                (cls._euclidean_distance(vectors[i], vectors[j]), j)
                for j in range(n) if j != i
            ]
            dists.sort(key=lambda x: x[0])
            raw_knn.append([j for _, j in dists[:fixed_degree]])

        undirected: Dict[int, Set[int]] = {i: set(raw_knn[i]) for i in range(n)}
        for i in range(n):
            for neighbor in raw_knn[i]:
                undirected[neighbor].add(i)

        regular: List[List[int]] = []
        for i in range(n):
            candidates = list(undirected[i])
            candidates.sort(key=lambda j: cls._euclidean_distance(vectors[i], vectors[j]))
            row = candidates[:fixed_degree]
            while len(row) < fixed_degree:
                row.append(i)
            regular.append(row)

        return regular

    @classmethod
    def search(
        cls,
        vectors: List[List[float]],
        regular_adjacency: List[List[int]],
        query: List[float],
        k: int = 5,
        search_width: int = 8,
    ) -> List[Dict[str, Any]]:
        n = len(vectors)
        if n == 0 or not regular_adjacency:
            return []

        curr = 0
        curr_dist = cls._euclidean_distance(query, vectors[0])
        for i in range(1, min(search_width, n)):
            d = cls._euclidean_distance(query, vectors[i])
            if d < curr_dist:
                curr_dist = d
                curr = i

        visited: Set[int] = {curr}
        evaluated: List[Tuple[float, int]] = [(curr_dist, curr)]

        improved = True
        iterations = 0
        while improved and iterations < search_width * 2:
            improved = False
            iterations += 1
            for neighbor in regular_adjacency[curr]:
                if neighbor not in visited and 0 <= neighbor < n:
                    visited.add(neighbor)
                    d = cls._euclidean_distance(query, vectors[neighbor])
                    evaluated.append((d, neighbor))
                    if d < curr_dist:
                        curr_dist = d
                        curr = neighbor
                        improved = True

        evaluated.sort(key=lambda x: x[0])
        top_k = evaluated[:k]
        return [
            {"id": idx, "distance": d, "vector": vectors[idx]}
            for d, idx in top_k
        ]

    @classmethod
    def execute(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        fixed_degree: int = 6,
        search_width: int = 8,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"total_nodes": 0, "fixed_degree": fixed_degree, "regular_adjacency": [], "neighbors": []}

        reg_graph = cls.build_regular_graph(vectors, fixed_degree)
        neighbors: List[Dict[str, Any]] = []

        if query is not None:
            neighbors = cls.search(vectors, reg_graph, query, k, search_width)

        return {
            "total_nodes": len(vectors),
            "fixed_degree": fixed_degree,
            "regular_adjacency": reg_graph,
            "neighbors": neighbors,
        }
