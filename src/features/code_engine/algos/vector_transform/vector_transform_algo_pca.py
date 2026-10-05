"""
================================================================================
ALGORITHM BLUEPRINT: PRINCIPAL COMPONENT ANALYSIS (PCA) (ALGO-VEC-TRFM-23)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Reduces vector dimensionality from D to d < D by projecting data onto the
   directions of maximal variance (eigenvectors of the sample covariance matrix).
   Calculates explained variance ratio to measure information retention.

2. ARCHITECTURAL ROLE:
   Transformer & Operator role (Layer 1). Reduces memory footprint and query latency
   for high-dimensional embeddings before graph index construction.

3. EXECUTION FLOW:
   a. Center vectors by subtracting sample mean.
   b. Compute covariance matrix or perform compact SVD: X = U S V^T.
   c. Select top d components: W = V[:d, :]^T.
   d. Project centered vectors: Z = X_centered @ W.
   e. Return transformed vectors, singular values, and explained variance ratios.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoPCA:
    """
    --- contract:
      id: ALGO-VEC-TRFM-23
      name: VectorTransformAlgoPCA
      category: transform
      complexity: O(N * D * d)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        target_dim: int
      output_schema:
        input_dim: int
        target_dim: int
        total_vectors: int
        explained_variance_ratio: list[float]
        total_variance_explained: float
        projected_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def fit_transform(
        vectors: List[List[float]],
        target_dim: int = 16,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "input_dim": 0,
                "target_dim": target_dim,
                "total_vectors": 0,
                "explained_variance_ratio": [],
                "total_variance_explained": 0.0,
                "projected_vectors": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = min(target_dim, d, n)

        mean = np.mean(X, axis=0)
        X_centered = X - mean

        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        W = Vt[:k, :].T
        Z = X_centered @ W

        variances = (S ** 2) / max(1, n - 1)
        total_var = float(np.sum(variances))
        var_ratios = [float(v / total_var) if total_var > 0 else 0.0 for v in variances[:k]]

        return {
            "input_dim": d,
            "target_dim": k,
            "total_vectors": n,
            "explained_variance_ratio": [round(r, 4) for r in var_ratios],
            "total_variance_explained": round(sum(var_ratios), 4),
            "projected_vectors": [[round(float(v), 6) for v in row] for row in Z],
        }
