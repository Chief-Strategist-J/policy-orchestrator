"""
================================================================================
ALGORITHM BLUEPRINT: WHITENING (PCA / ZCA WHITENING) (ALGO-VEC-TRFM-17)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Transforms vectors to have zero mean and an identity covariance matrix (Σ = I).
   Eliminates anisotropic stretching in embedding space, mitigating the "cone effect"
   where arbitrary pairs have spuriously high cosine similarities.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Calibrates anisotropic representations so cosine
   similarity faithfully measures semantic distinction across all directions.

3. EXECUTION FLOW:
   a. Center vectors by subtracting empirical mean.
   b. Compute covariance matrix Σ = (1/N) * X^T * X.
   c. Perform eigen-decomposition Σ = U * Λ * U^T.
   d. Compute whitening transform matrix W = U * Λ^{-1/2} (PCA whitening)
      or W_ZCA = U * Λ^{-1/2} * U^T (ZCA whitening).
   e. Project vectors: X_whitened = X_centered * W.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoWhitening:
    """
    --- contract:
      id: ALGO-VEC-TRFM-17
      name: VectorTransformAlgoWhitening
      category: transform
      complexity: O(N * D^2 + D^3)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        method: str
        regularization: float
      output_schema:
        total_vectors: int
        dimension: int
        method: str
        whitened_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def whiten(
        vectors: List[List[float]],
        method: str = "pca",
        regularization: float = 1e-5,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "dimension": 0,
                "method": method,
                "whitened_vectors": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape

        mean = np.mean(X, axis=0)
        X_centered = X - mean

        cov = np.dot(X_centered.T, X_centered) / max(1, n - 1)
        cov += np.eye(d) * regularization

        eigvals, eigvecs = np.linalg.eigh(cov)
        eigvals = np.maximum(eigvals, regularization)

        diag_inv_sqrt = np.diag(1.0 / np.sqrt(eigvals))

        if method.lower() == "zca":
            W = eigvecs @ diag_inv_sqrt @ eigvecs.T
        else:
            W = eigvecs @ diag_inv_sqrt

        X_whitened = X_centered @ W

        return {
            "total_vectors": n,
            "dimension": int(X_whitened.shape[1]),
            "method": method.lower(),
            "whitened_vectors": [[round(float(v), 6) for v in row] for row in X_whitened],
        }
