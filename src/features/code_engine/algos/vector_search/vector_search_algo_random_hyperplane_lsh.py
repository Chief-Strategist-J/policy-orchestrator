"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RANDOM-HYPERPLANE LSH (ALGO-VEC-SRCH-77)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Random-hyperplane Locality Sensitive Hashing (LSH) for angular/cosine similarity (#77).
   Constructs L independent hash tables, each parameterized by b random hyperplane
   normal vectors. Computes b-bit signatures via sign(w · x) projections. At query time,
   retrieves the union of candidate vectors residing in colliding buckets across the L
   tables and refines with exact metric distance evaluation to find the top k.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(L * b * D) query hashing + O(|Candidates| * D) candidate scoring.
   - Space Complexity: O(L * N) bucket indexing storage.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoRandomHyperplaneLSH:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-77
      name: VectorSearchAlgoRandomHyperplaneLSH
      version: 1.0.0
      category: vector
      capability_tags: [vector, hashing, lsh, random_hyperplane, cosine]
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
          num_bits: {type: integer, default: 4}
          num_tables: {type: integer, default: 3}
          seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [num_tables, num_bits, total_candidates, neighbors]
        properties:
          num_tables: {type: integer}
          num_bits: {type: integer}
          total_candidates: {type: integer}
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
        time: O(L * b * D + C * D)
        space: O(L * N)
      preconditions:
        - len(vectors) > 0
        - num_bits > 0
        - num_tables > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-LSH-CANDIDATES
    ---
    """

    @staticmethod
    def _dot_product(a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def _generate_hyperplanes(cls, dim: int, num_bits: int, rnd: random.Random) -> List[List[float]]:
        hyperplanes: List[List[float]] = []
        for _ in range(num_bits):
            plane = [rnd.gauss(0.0, 1.0) for _ in range(dim)]
            norm = math.sqrt(sum(x * x for x in plane)) or 1.0
            hyperplanes.append([x / norm for x in plane])
        return hyperplanes

    @classmethod
    def _hash_vector(cls, vec: List[float], hyperplanes: List[List[float]]) -> int:
        h = 0
        for i, plane in enumerate(hyperplanes):
            if cls._dot_product(vec, plane) >= 0.0:
                h |= (1 << i)
        return h

    @classmethod
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        num_bits: int = 4,
        num_tables: int = 3,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"num_tables": num_tables, "num_bits": num_bits, "total_candidates": 0, "neighbors": []}

        n = len(vectors)
        dim = len(vectors[0])
        rnd = random.Random(seed)

        tables: List[Dict[int, List[int]]] = [{} for _ in range(num_tables)]
        table_planes: List[List[List[float]]] = []

        for t in range(num_tables):
            planes = cls._generate_hyperplanes(dim, num_bits, rnd)
            table_planes.append(planes)
            for idx, vec in enumerate(vectors):
                bucket_key = cls._hash_vector(vec, planes)
                if bucket_key not in tables[t]:
                    tables[t][bucket_key] = []
                tables[t][bucket_key].append(idx)

        neighbors: List[Dict[str, Any]] = []
        candidate_set: Set[int] = set()

        if query is not None:
            for t in range(num_tables):
                q_key = cls._hash_vector(query, table_planes[t])
                for idx in tables[t].get(q_key, []):
                    candidate_set.add(idx)

            if not candidate_set:
                candidate_set = set(range(min(k * 2, n)))

            scored = [
                (cls._euclidean_distance(query, vectors[idx]), idx)
                for idx in candidate_set
            ]
            scored.sort(key=lambda x: x[0])
            neighbors = [
                {"id": idx, "distance": d, "vector": vectors[idx]}
                for d, idx in scored[:k]
            ]

        return {
            "num_tables": num_tables,
            "num_bits": num_bits,
            "total_candidates": len(candidate_set),
            "neighbors": neighbors,
        }
