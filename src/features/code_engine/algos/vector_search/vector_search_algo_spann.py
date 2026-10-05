"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SPANN HYBRID PARTITIONING (ALGO-VEC-SRCH-76)
================================================================================

1. OVERVIEW & OBJECTIVE:
   SPANN (Space-Partitioned Approximate Nearest Neighbor) hybrid indexing (#76).
   Keeps coarse centroid routing points in fast memory while streaming sequential
   partition blocks from disk. Vectors positioned near partition boundaries are
   duplicated into neighboring posting lists governed by boundary slack factor
   epsilon, eliminating edge-case partition misses and reducing random disk seeks.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(C * D) centroid routing + O(nprobe * |Partition| * D) search.
   - Space Complexity: O(N * (1 + duplication_factor)) storage footprint.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple


class VectorSearchAlgoSPANN:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-76
      name: VectorSearchAlgoSPANN
      version: 1.0.0
      category: vector
      capability_tags: [vector, hybrid_index, spann, boundary_duplication, ssd_scale]
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
          num_centroids: {type: integer, default: 4}
          nprobe: {type: integer, default: 2}
          slack_factor: {type: number, default: 1.2}
      outputs:
        type: object
        required: [num_centroids, nprobe, total_postings, duplication_ratio, neighbors]
        properties:
          num_centroids: {type: integer}
          nprobe: {type: integer}
          total_postings: {type: integer}
          duplication_ratio: {type: number}
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
        time: O(C + nprobe * S)
        space: O(N * (1 + delta))
      preconditions:
        - len(vectors) > 0
        - num_centroids > 0
      postconditions:
        - output.duplication_ratio >= 1.0
      compatible_adapters:
        - ADAPTER-SPANN-INDEX
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def train_centroids(cls, vectors: List[List[float]], c: int) -> List[List[float]]:
        n = len(vectors)
        step = max(1, n // c)
        centroids = [list(vectors[i * step]) for i in range(c)]

        for _ in range(5):
            clusters: List[List[List[float]]] = [[] for _ in range(c)]
            for vec in vectors:
                best_idx = 0
                min_d = float("inf")
                for j in range(c):
                    d = cls._euclidean_distance(vec, centroids[j])
                    if d < min_d:
                        min_d = d
                        best_idx = j
                clusters[best_idx].append(vec)

            for j in range(c):
                if clusters[j]:
                    dim = len(vectors[0])
                    centroids[j] = [
                        sum(vec[d] for vec in clusters[j]) / len(clusters[j])
                        for d in range(dim)
                    ]
        return centroids

    @classmethod
    def build_and_search(
        cls,
        vectors: List[List[float]],
        query: Optional[List[float]] = None,
        k: int = 5,
        num_centroids: int = 4,
        nprobe: int = 2,
        slack_factor: float = 1.2,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "num_centroids": 0,
                "nprobe": nprobe,
                "total_postings": 0,
                "duplication_ratio": 1.0,
                "neighbors": [],
            }

        n = len(vectors)
        c = min(num_centroids, n)
        actual_nprobe = min(nprobe, c)
        centroids = cls.train_centroids(vectors, c)

        posting_lists: List[List[int]] = [[] for _ in range(c)]
        total_postings = 0

        for idx, vec in enumerate(vectors):
            centroid_dists = [
                (cls._euclidean_distance(vec, centroids[j]), j)
                for j in range(c)
            ]
            centroid_dists.sort(key=lambda x: x[0])
            primary_dist, primary_centroid = centroid_dists[0]
            posting_lists[primary_centroid].append(idx)
            total_postings += 1

            for dist_j, centroid_j in centroid_dists[1:]:
                if dist_j <= primary_dist * slack_factor:
                    posting_lists[centroid_j].append(idx)
                    total_postings += 1

        duplication_ratio = total_postings / max(1, n)
        neighbors: List[Dict[str, Any]] = []

        if query is not None:
            ranked_centroids = [
                (cls._euclidean_distance(query, centroids[j]), j)
                for j in range(c)
            ]
            ranked_centroids.sort(key=lambda x: x[0])
            candidate_ids = set()
            for _, centroid_idx in ranked_centroids[:actual_nprobe]:
                candidate_ids.update(posting_lists[centroid_idx])

            scored = [
                (cls._euclidean_distance(query, vectors[idx]), idx)
                for idx in candidate_ids
            ]
            scored.sort(key=lambda x: x[0])
            neighbors = [
                {"id": idx, "distance": d, "vector": vectors[idx]}
                for d, idx in scored[:k]
            ]

        return {
            "num_centroids": c,
            "nprobe": actual_nprobe,
            "total_postings": total_postings,
            "duplication_ratio": round(duplication_ratio, 4),
            "neighbors": neighbors,
        }
