"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: INVERTED FILE INDEX (IVF) (ALGO-VEC-SRCH-61)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Partitions the vector dataset into C coarse Voronoi clusters (#61) using
   k-means clustering. At query time, routes searches to only the top `nprobe`
   closest clusters, reducing candidate evaluations from N to (nprobe / C) * N.
   Standard enterprise indexing strategy (Faiss / Milvus / Qdrant).

2. ALGORITHMIC MECHANICS:
   - Index Construction: Runs Lloyd's k-means to compute C cluster centroids.
     Assigns each vector x_i to its nearest centroid c_j and appends x_i into
     posting list L_j.
   - Query Routing: Computes distances from query q to all C centroids.
     Selects the `nprobe` closest centroids.
   - Candidate Scan: Exhaustively scans only the vectors inside the posting lists
     of the selected `nprobe` cells, extracting the top-k nearest neighbors.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Configurable nprobe: Gracefully caps nprobe between 1 and C.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class VectorSearchAlgoIvf:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-61
      name: VectorSearchAlgoIvf
      version: 1.0.0
      category: vector
      capability_tags: [vector, ivf, inverted_file, clustering, voronoi, ann]
      inputs:
        type: object
        required: [vectors, query]
        properties:
          vectors:
            type: array
            items:
              type: array
              items: {type: number}
          query:
            type: array
            items: {type: number}
          k: {type: integer, default: 5}
          num_clusters: {type: integer, default: 4}
          nprobe: {type: integer, default: 2}
          max_kmeans_iter: {type: integer, default: 15}
          seed: {type: integer, default: 42}
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [k, dimension, num_clusters, nprobe, total_candidates, matches]
        properties:
          k: {type: integer}
          dimension: {type: integer}
          num_clusters: {type: integer}
          nprobe: {type: integer}
          total_candidates: {type: integer}
          probed_clusters:
            type: array
            items: {type: integer}
          matches:
            type: array
            items:
              type: object
              properties:
                id: {type: string}
                index: {type: integer}
                distance: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N * C) build, O(C * D + (nprobe / C) * N * D) search
        space: O(N * D + C * D)
      preconditions:
        - len(input.vectors) > 0
        - len(input.query) > 0
      postconditions:
        - len(output.matches) <= input.k
      compatible_adapters:
        - ADAPTER-IVF-SEARCH-RESULT
    ---
    """

    @classmethod
    def train_and_index(
        cls,
        vectors: np.ndarray,
        num_clusters: int,
        max_iter: int = 15,
        seed: int = 42,
    ) -> Tuple[np.ndarray, Dict[int, List[int]]]:
        N, D = vectors.shape
        C = min(num_clusters, N)
        rng = np.random.RandomState(seed)

        init_idx = rng.choice(N, size=C, replace=False)
        centroids = vectors[init_idx].copy()

        for _ in range(max_iter):
            dists = np.linalg.norm(vectors[:, None, :] - centroids[None, :, :], axis=2)
            assignments = np.argmin(dists, axis=1)

            new_centroids = np.zeros_like(centroids)
            counts = np.zeros(C, dtype=np.int32)

            for i in range(N):
                c = assignments[i]
                new_centroids[c] += vectors[i]
                counts[c] += 1

            for c in range(C):
                if counts[c] > 0:
                    centroids[c] = new_centroids[c] / counts[c]
                else:
                    centroids[c] = vectors[rng.randint(N)]

        inv_lists: Dict[int, List[int]] = {c: [] for c in range(C)}
        dists = np.linalg.norm(vectors[:, None, :] - centroids[None, :, :], axis=2)
        final_assignments = np.argmin(dists, axis=1)

        for idx, cluster_id in enumerate(final_assignments):
            inv_lists[cluster_id].append(idx)

        return centroids, inv_lists

    @classmethod
    def search(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
        query: Union[List[float], np.ndarray],
        k: int = 5,
        num_clusters: int = 4,
        nprobe: int = 2,
        max_kmeans_iter: int = 15,
        seed: int = 42,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(vectors, dtype=np.float32)
        q = np.asarray(query, dtype=np.float32)
        N, D = X.shape

        if N == 0 or k <= 0:
            return {"k": k, "dimension": D, "num_clusters": num_clusters, "nprobe": nprobe, "total_candidates": 0, "matches": []}

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        centroids, inv_lists = cls.train_and_index(X, num_clusters=num_clusters, max_iter=max_kmeans_iter, seed=seed)
        actual_clusters = centroids.shape[0]
        actual_nprobe = min(max(1, nprobe), actual_clusters)

        dist_to_centroids = np.linalg.norm(centroids - q, axis=1)
        probed_clusters = [int(idx) for idx in np.argsort(dist_to_centroids)[:actual_nprobe]]

        candidate_indices: List[int] = []
        for cluster_id in probed_clusters:
            candidate_indices.extend(inv_lists[cluster_id])

        if not candidate_indices:
            return {
                "k": k,
                "dimension": D,
                "num_clusters": actual_clusters,
                "nprobe": actual_nprobe,
                "total_candidates": 0,
                "probed_clusters": probed_clusters,
                "matches": [],
            }

        candidate_vectors = X[candidate_indices]
        dists = np.linalg.norm(candidate_vectors - q, axis=1)
        order = np.argsort(dists)[:min(k, len(candidate_indices))]

        matches = [
            {
                "id": ids[candidate_indices[idx]],
                "index": int(candidate_indices[idx]),
                "distance": float(dists[idx]),
            }
            for idx in order
        ]

        return {
            "k": k,
            "dimension": D,
            "num_clusters": actual_clusters,
            "nprobe": actual_nprobe,
            "total_candidates": len(candidate_indices),
            "probed_clusters": probed_clusters,
            "matches": matches,
        }
