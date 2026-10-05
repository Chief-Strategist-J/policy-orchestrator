"""
================================================================================
ALGORITHM BLUEPRINT: K-MEANS CLUSTERING (LLOYD'S ALGORITHM) (ALGO-VEC-TRFM-39)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Partitions N vectors into K clusters by alternating between assigning vectors to
   nearest centroids and updating centroids as the center of mass:
   min_{C, S} sum_{k=1}^K sum_{x in S_k} ||x - c_k||^2.
   Iterates until centroid movement drops below tolerance or max_iterations is reached.

2. ARCHITECTURAL ROLE:
   Transformer & Indexer role (Layer 1). Core quantizer for building IVF coarse
   quantizers, PQ codebooks, and SPANN centroid partitions.

3. EXECUTION FLOW:
   a. Initialize K centroids (randomly or from first K points).
   b. Assign each point to its nearest centroid by Euclidean distance.
   c. Recompute each centroid as the arithmetic mean of its assigned points.
   d. Check Frobenius norm shift between consecutive iterations.
   e. Terminate on convergence and return cluster centroids, assignments, and inertia.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoKMeansClustering:
    """
    --- contract:
      id: ALGO-VEC-TRFM-39
      name: VectorTransformAlgoKMeansClustering
      category: transform
      complexity: O(max_iter * N * K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        k_clusters: int
        max_iter: int
        tol: float
        seed: int
      output_schema:
        total_vectors: int
        k_clusters: int
        iterations_run: int
        inertia: float
        centroids: list[list[float]]
        assignments: list[int]
    ---
    """

    @staticmethod
    def cluster(
        vectors: List[List[float]],
        k_clusters: int = 4,
        max_iter: int = 25,
        tol: float = 1e-4,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "k_clusters": k_clusters,
                "iterations_run": 0,
                "inertia": 0.0,
                "centroids": [],
                "assignments": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = min(k_clusters, n)

        rng = np.random.RandomState(seed)
        init_indices = rng.choice(n, size=k, replace=False)
        centroids = X[init_indices].copy()

        assignments = np.zeros(n, dtype=int)
        iters_run = 0

        for it in range(max_iter):
            iters_run = it + 1

            dists = np.zeros((n, k))
            for c_idx in range(k):
                dists[:, c_idx] = np.sum((X - centroids[c_idx]) ** 2, axis=1)

            new_assignments = np.argmin(dists, axis=1)

            new_centroids = np.zeros_like(centroids)
            for c_idx in range(k):
                pts = X[new_assignments == c_idx]
                if len(pts) > 0:
                    new_centroids[c_idx] = np.mean(pts, axis=0)
                else:
                    new_centroids[c_idx] = centroids[c_idx]

            shift = float(np.linalg.norm(new_centroids - centroids))
            centroids = new_centroids
            assignments = new_assignments

            if shift < tol:
                break

        inertia = 0.0
        for i in range(n):
            inertia += float(np.sum((X[i] - centroids[assignments[i]]) ** 2))

        return {
            "total_vectors": n,
            "k_clusters": k,
            "iterations_run": iters_run,
            "inertia": round(inertia, 4),
            "centroids": [[round(float(v), 6) for v in row] for row in centroids],
            "assignments": [int(a) for a in assignments],
        }
