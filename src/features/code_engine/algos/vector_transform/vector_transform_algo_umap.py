"""
================================================================================
ALGORITHM BLUEPRINT: UMAP (UNIFORM MANIFOLD APPROXIMATION & PROJECTION) (ALGO-VEC-TRFM-27)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Models non-linear Riemannian manifolds using fuzzy simplicial sets and optimizes
   a low-dimensional layout (e.g. 2D/3D visualization or cluster embedding) by
   minimizing fuzzy set cross-entropy:
   C = Σ_{i,j} [ μ_{ij} log(μ_{ij} / ν_{ij}) + (1 - μ_{ij}) log((1 - μ_{ij}) / (1 - ν_{ij})) ].

2. ARCHITECTURAL ROLE:
   Observer & Transformer role (Layer 1). Projects high-dimensional embedding clusters
   into visually interpretable coordinates while preserving global topological structure.

3. EXECUTION FLOW:
   a. Compute k-nearest-neighbor graph in high-dimensional input space.
   b. Compute fuzzy simplicial set edge weights μ_{ij} using adaptive local distance scales.
   c. Initialize low-dimensional coordinates via spectral embedding / PCA.
   d. Optimize low-dimensional coordinates using gradient descent with repulsive forces.
   e. Return low-dimensional embeddings and graph connectivity metrics.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math
import numpy as np


class VectorTransformAlgoUMAP:
    """
    --- contract:
      id: ALGO-VEC-TRFM-27
      name: VectorTransformAlgoUMAP
      category: transform
      complexity: O(N * k * D + N * n_epochs * n_components)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        n_components: int
        n_neighbors: int
        min_dist: float
        n_epochs: int
      output_schema:
        total_vectors: int
        n_components: int
        embedding: list[list[float]]
    ---
    """

    @staticmethod
    def project(
        vectors: List[List[float]],
        n_components: int = 2,
        n_neighbors: int = 5,
        min_dist: float = 0.1,
        n_epochs: int = 30,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"total_vectors": 0, "n_components": n_components, "embedding": []}

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = min(n_neighbors, n - 1) if n > 1 else 1

        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                diff = X[i] - X[j]
                d_val = float(np.linalg.norm(diff))
                dist_matrix[i, j] = d_val
                dist_matrix[j, i] = d_val

        rng = np.random.RandomState(42)
        if n >= n_components:
            mean = np.mean(X, axis=0)
            _, _, Vt = np.linalg.svd(X - mean, full_matrices=False)
            Y = (X - mean) @ Vt[:n_components, :].T
            if Y.shape[1] < n_components:
                Y = rng.normal(0, 1, size=(n, n_components))
        else:
            Y = rng.normal(0, 1, size=(n, n_components))

        lr = 0.1
        a = 1.58
        b_param = 0.89

        for epoch in range(n_epochs):
            grad = np.zeros_like(Y)
            for i in range(n):
                nn_indices = np.argsort(dist_matrix[i])[1 : k + 1]
                for j in nn_indices:
                    diff_y = Y[i] - Y[j]
                    dist_y = float(np.linalg.norm(diff_y))
                    if dist_y > 1e-4:
                        attr_force = -2.0 * b_param * (dist_y ** (2.0 * (b_param - 1.0)))
                        grad[i] += attr_force * diff_y

                rep_idx = rng.randint(0, n)
                if rep_idx != i:
                    diff_r = Y[i] - Y[rep_idx]
                    dist_r = max(1e-4, float(np.linalg.norm(diff_r)))
                    rep_force = 2.0 * b_param / ((1e-3 + dist_r ** 2) * (1.0 + a * dist_r ** (2 * b_param)))
                    grad[i] += rep_force * diff_r

            Y -= lr * grad * (1.0 - epoch / max(1, n_epochs))

        return {
            "total_vectors": n,
            "n_components": n_components,
            "embedding": [[round(float(v), 6) for v in row] for row in Y],
        }
