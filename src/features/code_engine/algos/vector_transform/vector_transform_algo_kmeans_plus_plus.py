"""
================================================================================
ALGORITHM BLUEPRINT: K-MEANS++ INITIALIZATION (ALGO-VEC-TRFM-40)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Selects initial k-means cluster centers using D^2 probability weighting (Arthur &
   Vassilvitskii, 2007). Chooses the first center uniformly at random, and chooses each
   subsequent center with probability proportional to D(x)^2 (squared distance to the
   closest already-chosen center). Guarantees O(log k) competitive ratio to optimal clustering.

2. ARCHITECTURAL ROLE:
   Transformer & Indexer role (Layer 1). Prevents pathological poor local minima and
   accelerates Lloyd's algorithm convergence by 2x-5x on vector collections.

3. EXECUTION FLOW:
   a. Choose 1st centroid c_1 uniformly from dataset X.
   b. For remaining k - 1 centers:
      i. For every point x, compute D(x)^2 = min_{j < m} ||x - c_j||^2.
      ii. Form discrete probability distribution p(x) = D(x)^2 / sum_x D(x)^2.
      iii. Sample next centroid according to p(x).
   c. Return initialized centroids and initial inertia estimate.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoKMeansPlusPlus:
    """
    --- contract:
      id: ALGO-VEC-TRFM-40
      name: VectorTransformAlgoKMeansPlusPlus
      category: transform
      complexity: O(k * N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        k_clusters: int
        seed: int
      output_schema:
        total_vectors: int
        k_clusters: int
        selected_indices: list[int]
        centroids: list[list[float]]
    ---
    """

    @staticmethod
    def initialize_centroids(
        vectors: List[List[float]],
        k_clusters: int = 4,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "k_clusters": k_clusters,
                "selected_indices": [],
                "centroids": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = min(k_clusters, n)

        rng = np.random.RandomState(seed)

        first_idx = int(rng.randint(0, n))
        selected_indices = [first_idx]
        centroids = [X[first_idx].copy()]

        closest_dist_sq = np.sum((X - centroids[0]) ** 2, axis=1)

        for _ in range(1, k):
            total_dist = float(np.sum(closest_dist_sq))
            if total_dist <= 1e-12:
                remaining = [i for i in range(n) if i not in selected_indices]
                next_idx = int(rng.choice(remaining)) if remaining else 0
            else:
                probs = closest_dist_sq / total_dist
                next_idx = int(rng.choice(n, p=probs))

            selected_indices.append(next_idx)
            new_c = X[next_idx].copy()
            centroids.append(new_c)

            new_dists = np.sum((X - new_c) ** 2, axis=1)
            closest_dist_sq = np.minimum(closest_dist_sq, new_dists)

        return {
            "total_vectors": n,
            "k_clusters": k,
            "selected_indices": selected_indices,
            "centroids": [[round(float(v), 6) for v in row] for row in centroids],
        }
