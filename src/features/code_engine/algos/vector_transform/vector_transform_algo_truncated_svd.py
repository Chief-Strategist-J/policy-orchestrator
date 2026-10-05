"""
================================================================================
ALGORITHM BLUEPRINT: TRUNCATED SVD (ALGO-VEC-TRFM-24)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Performs low-rank matrix approximation via Truncated Singular Value Decomposition
   without requiring explicit mean centering (LSA / Latent Semantic Analysis style).
   Preserves sparsity of sparse inputs while projecting to k latent semantic components.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Effective for term-document matrices and uncentered
   sparse vectors where mean-centering would destroy memory sparsity.

3. EXECUTION FLOW:
   a. Decompose matrix X (N x D) into U_k, S_k, V_k^T.
   b. Project data: X_transformed = X @ V_k.
   c. Return transformed vectors and singular value spectrum.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoTruncatedSVD:
    """
    --- contract:
      id: ALGO-VEC-TRFM-24
      name: VectorTransformAlgoTruncatedSVD
      category: transform
      complexity: O(N * D * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        n_components: int
      output_schema:
        original_dim: int
        n_components: int
        singular_values: list[float]
        projected_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def transform(
        vectors: List[List[float]],
        n_components: int = 8,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "original_dim": 0,
                "n_components": n_components,
                "singular_values": [],
                "projected_vectors": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = min(n_components, d, n)

        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        V_k = Vt[:k, :].T
        Z = X @ V_k

        return {
            "original_dim": d,
            "n_components": k,
            "singular_values": [round(float(s), 4) for s in S[:k]],
            "projected_vectors": [[round(float(v), 6) for v in row] for row in Z],
        }
