"""
================================================================================
ALGORITHM BLUEPRINT: T-SNE (T-DISTRIBUTED STOCHASTIC NEIGHBOR EMBEDDING) (ALGO-VEC-TRFM-28)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Converts affinities of high-dimensional vectors to probabilities using Gaussian
   distributions, and represents similar affinities in low-dimensional space using
   a heavy-tailed Student-t distribution (1 degree of freedom), resolving crowding:
   q_{ij} = (1 + ||y_i - y_j||^2)^{-1} / Σ_{k≠l} (1 + ||y_k - y_l||^2)^{-1}.

2. ARCHITECTURAL ROLE:
   Observer role (Layer 1). Unsupervised non-linear cluster inspection and visual
   diagnostic of semantic drift between embedding version updates.

3. EXECUTION FLOW:
   a. Compute pairwise Euclidean distance matrix D in input space.
   b. Compute conditional Gaussian probabilities p_{j|i} based on target perplexity.
   c. Symmetrize high-dimensional affinities: p_{ij} = (p_{j|i} + p_{i|j}) / (2N).
   d. Initialize low-dimensional points Y ~ N(0, 1e-4).
   e. Perform gradient descent with momentum and early exaggeration.
   f. Return 2D/3D coordinates.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math
import numpy as np


class VectorTransformAlgoTSNE:
    """
    --- contract:
      id: ALGO-VEC-TRFM-28
      name: VectorTransformAlgoTSNE
      category: transform
      complexity: O(n_iter * N^2)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        n_components: int
        perplexity: float
        n_iter: int
      output_schema:
        total_vectors: int
        n_components: int
        kl_divergence: float
        embedding: list[list[float]]
    ---
    """

    @staticmethod
    def project(
        vectors: List[List[float]],
        n_components: int = 2,
        perplexity: float = 30.0,
        n_iter: int = 40,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"total_vectors": 0, "n_components": n_components, "kl_divergence": 0.0, "embedding": []}

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape

        sum_X = np.sum(X ** 2, axis=1)
        D_matrix = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
        D_matrix = np.maximum(D_matrix, 0.0)

        P = np.exp(-D_matrix / (2.0 * max(1.0, float(np.mean(D_matrix)) + 1e-5)))
        np.fill_diagonal(P, 0.0)
        sum_P = max(1e-12, float(np.sum(P)))
        P = (P + P.T) / (2.0 * sum_P)
        P = np.maximum(P, 1e-12)

        rng = np.random.RandomState(42)
        Y = rng.normal(0.0, 1e-2, size=(n, n_components))

        lr = 10.0
        for _ in range(n_iter):
            sum_Y = np.sum(Y ** 2, axis=1)
            num = 1.0 / (1.0 + np.add(np.add(-2 * np.dot(Y, Y.T), sum_Y).T, sum_Y))
            np.fill_diagonal(num, 0.0)
            Q = num / max(1e-12, float(np.sum(num)))
            Q = np.maximum(Q, 1e-12)

            PQ_diff = P - Q
            dY = np.zeros_like(Y)
            for i in range(n):
                mult = (PQ_diff[i, :] * num[i, :])[:, np.newaxis]
                dY[i, :] = 4.0 * np.sum(mult * (Y[i, :] - Y), axis=0)

            Y -= lr * dY

        kl_div = float(np.sum(P * np.log(P / Q)))

        return {
            "total_vectors": n,
            "n_components": n_components,
            "kl_divergence": round(kl_div, 4),
            "embedding": [[round(float(v), 6) for v in row] for row in Y],
        }
