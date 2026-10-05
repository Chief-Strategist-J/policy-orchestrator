"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: E2LSH P-STABLE L2 HASHING (ALGO-VEC-SRCH-79)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Exact Euclidean Locality-Sensitive Hashing (E2LSH) using 2-stable distributions (#79).
   Projects unnormalized continuous vectors onto Gaussian random projection lines
   divided into uniform quantization slots of width w with uniform phase offset b:
   h_{a,b}(x) = floor((a · x + b) / w). Concatenates m projection keys across L
   independent hash tables to provide rigorous collision probability guarantees
   directly proportional to Euclidean distance.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(L * m * D) query projection + O(|Candidates| * D) scoring.
   - Space Complexity: O(L * N) multi-table bucket indexing.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoE2LSH:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-79
      name: VectorSearchAlgoE2LSH
      version: 1.0.0
      category: vector
      capability_tags: [vector, hashing, e2lsh, p_stable, euclidean_lsh]
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
          slot_width_w: {type: number, default: 4.0}
          num_projections_m: {type: integer, default: 4}
          num_tables_l: {type: integer, default: 3}
          seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [slot_width_w, num_projections_m, num_tables_l, total_candidates, neighbors]
        properties:
          slot_width_w: {type: number}
          num_projections_m: {type: integer}
          num_tables_l: {type: integer}
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
        time: O(L * m * D + C * D)
        space: O(L * N)
      preconditions:
        - len(vectors) > 0
        - slot_width_w > 0.0
        - num_projections_m > 0
        - num_tables_l > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-E2LSH-CANDIDATES
    ---
    """

    @staticmethod
    def _dot_product(a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def _hash_vector(
        cls,
        vec: List[float],
        projections: List[List[float]],
        offsets: List[float],
        w: float,
    ) -> Tuple[int, ...]:
        keys = []
        for a, b in zip(projections, offsets):
            val = cls._dot_product(vec, a) + b
            keys.append(int(math.floor(val / w)))
        return tuple(keys)

    @classmethod
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        slot_width_w: float = 4.0,
        num_projections_m: int = 4,
        num_tables_l: int = 3,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "slot_width_w": slot_width_w,
                "num_projections_m": num_projections_m,
                "num_tables_l": num_tables_l,
                "total_candidates": 0,
                "neighbors": [],
            }

        n = len(vectors)
        dim = len(vectors[0])
        rnd = random.Random(seed)

        tables: List[Dict[Tuple[int, ...], List[int]]] = [{} for _ in range(num_tables_l)]
        table_params: List[Tuple[List[List[float]], List[float]]] = []

        for _ in range(num_tables_l):
            projections = [[rnd.gauss(0.0, 1.0) for _ in range(dim)] for _ in range(num_projections_m)]
            offsets = [rnd.uniform(0.0, slot_width_w) for _ in range(num_projections_m)]
            table_params.append((projections, offsets))

        for t in range(num_tables_l):
            projections, offsets = table_params[t]
            for idx, vec in enumerate(vectors):
                key = cls._hash_vector(vec, projections, offsets, slot_width_w)
                if key not in tables[t]:
                    tables[t][key] = []
                tables[t][key].append(idx)

        candidate_set: Set[int] = set()
        neighbors: List[Dict[str, Any]] = []

        if query is not None:
            for t in range(num_tables_l):
                projections, offsets = table_params[t]
                q_key = cls._hash_vector(query, projections, offsets, slot_width_w)
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
            "slot_width_w": slot_width_w,
            "num_projections_m": num_projections_m,
            "num_tables_l": num_tables_l,
            "total_candidates": len(candidate_set),
            "neighbors": neighbors,
        }
