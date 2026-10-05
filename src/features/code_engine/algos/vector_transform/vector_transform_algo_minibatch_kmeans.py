"""
================================================================================
ALGORITHM BLUEPRINT: MINI-BATCH K-MEANS (ALGO-VEC-TRFM-41)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements online Mini-Batch k-means (Sculley, 2010). Updates cluster centroids
   using small randomly sampled batches with running per-center assignment counts:
   c = c + (1 / v) * (x - c).
   Reduces computation by orders of magnitude while converging to solutions with
   comparable inertia to full Lloyd's algorithm.

2. ARCHITECTURAL ROLE:
   Transformer & Operator role (Layer 1). Enables fast IVF coarse quantizer training
   on multi-million vector datasets without exhausting host memory.

3. EXECUTION FLOW:
   a. Initialize K centroids randomly from dataset.
   b. Initialize per-centroid sample count counters v_1, ..., v_K = 0.
   c. Sample random mini-batch of size B.
   d. Assign batch samples to closest current centroids.
   e. For each sample, increment centroid counter v and update centroid position.
   f. Repeat for n_batches and return converged centroids.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoMiniBatchKMeans:
    """
    --- contract:
      id: ALGO-VEC-TRFM-41
      name: VectorTransformAlgoMiniBatchKMeans
      category: transform
      complexity: O(n_batches * batch_size * K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        k_clusters: int
        batch_size: int
        n_batches: int
        seed: int
      output_schema:
        total_vectors: int
        k_clusters: int
        batches_processed: int
        cluster_counts: list[int]
        centroids: list[list[float]]
    ---
    """

    @staticmethod
    def train(
        vectors: List[List[float]],
        k_clusters: int = 4,
        batch_size: int = 32,
        n_batches: int = 20,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "k_clusters": k_clusters,
                "batches_processed": 0,
                "cluster_counts": [],
                "centroids": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = min(k_clusters, n)
        b_size = min(batch_size, n)

        rng = np.random.RandomState(seed)
        init_idx = rng.choice(n, size=k, replace=False)
        centroids = X[init_idx].copy()
        counts = np.zeros(k, dtype=int)

        for _ in range(n_batches):
            batch_idx = rng.choice(n, size=b_size, replace=False)
            batch = X[batch_idx]

            dists = np.zeros((b_size, k))
            for c_idx in range(k):
                dists[:, c_idx] = np.sum((batch - centroids[c_idx]) ** 2, axis=1)

            assignments = np.argmin(dists, axis=1)

            for item_idx, c_idx in enumerate(assignments):
                counts[c_idx] += 1
                eta = 1.0 / counts[c_idx]
                centroids[c_idx] += eta * (batch[item_idx] - centroids[c_idx])

        return {
            "total_vectors": n,
            "k_clusters": k,
            "batches_processed": n_batches,
            "cluster_counts": [int(c) for c in counts],
            "centroids": [[round(float(v), 6) for v in row] for row in centroids],
        }


VectorTransformAlgoMinibatchKMeans = VectorTransformAlgoMiniBatchKMeans
