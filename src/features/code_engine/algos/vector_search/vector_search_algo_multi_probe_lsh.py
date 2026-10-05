"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MULTI-PROBE LSH (ALGO-VEC-SRCH-78)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Multi-Probe Locality Sensitive Hashing (LSH) (#78). Reduces hash table memory
   overheads by systematically probing neighboring perturbation buckets adjacent
   to the primary hash key. Computes projection margins |w_i · q| against hyperplane
   boundaries, sorts bit flip priorities, probes the most probable colliding buckets
   under a strict probe budget, and extracts refined top-k nearest neighbors.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(b * D) hashing + O(P * |Bucket|) probe retrieval.
   - Space Complexity: O(N) single-table memory footprint.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoMultiProbeLSH:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-78
      name: VectorSearchAlgoMultiProbeLSH
      version: 1.0.0
      category: vector
      capability_tags: [vector, hashing, multi_probe, lsh, perturbation_search]
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
          num_bits: {type: integer, default: 6}
          probe_budget: {type: integer, default: 4}
          seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [num_bits, probe_budget, probed_buckets, total_candidates, neighbors]
        properties:
          num_bits: {type: integer}
          probe_budget: {type: integer}
          probed_buckets:
            type: array
            items: {type: integer}
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
        time: O(b * D + P * B)
        space: O(N)
      preconditions:
        - len(vectors) > 0
        - num_bits > 0
        - probe_budget > 0
      postconditions:
        - len(output.neighbors) <= input.k
      compatible_adapters:
        - ADAPTER-MULTIPROBE-CANDIDATES
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
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        num_bits: int = 6,
        probe_budget: int = 4,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "num_bits": num_bits,
                "probe_budget": probe_budget,
                "probed_buckets": [],
                "total_candidates": 0,
                "neighbors": [],
            }

        n = len(vectors)
        dim = len(vectors[0])
        rnd = random.Random(seed)
        planes = cls._generate_hyperplanes(dim, num_bits, rnd)

        table: Dict[int, List[int]] = {}
        for idx, vec in enumerate(vectors):
            h = 0
            for b, plane in enumerate(planes):
                if cls._dot_product(vec, plane) >= 0.0:
                    h |= (1 << b)
            if h not in table:
                table[h] = []
            table[h].append(idx)

        probed_buckets: List[int] = []
        candidate_set: Set[int] = set()
        neighbors: List[Dict[str, Any]] = []

        if query is not None:
            q_margins: List[Tuple[float, int]] = []
            base_hash = 0
            for b, plane in enumerate(planes):
                val = cls._dot_product(query, plane)
                if val >= 0.0:
                    base_hash |= (1 << b)
                q_margins.append((abs(val), b))

            q_margins.sort(key=lambda x: x[0])

            probed_buckets.append(base_hash)
            for _, bit_pos in q_margins:
                if len(probed_buckets) >= probe_budget:
                    break
                perturbed = base_hash ^ (1 << bit_pos)
                if perturbed not in probed_buckets:
                    probed_buckets.append(perturbed)

            for b_key in probed_buckets:
                for idx in table.get(b_key, []):
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
            "num_bits": num_bits,
            "probe_budget": probe_budget,
            "probed_buckets": probed_buckets,
            "total_candidates": len(candidate_set),
            "neighbors": neighbors,
        }
