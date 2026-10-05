"""
================================================================================
ALGORITHM BLUEPRINT: REMOVING DOMINANT DIRECTIONS (ALGO-VEC-TRFM-18)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements the "All-but-the-top" transformation (Mu & Viswanath, ICLR 2018).
   Identifies the top-k principal components across the corpus representing common
   word frequency / syntax noise and projects them out: v' = v - sum_{i=1}^k (v · u_i) * u_i.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Eliminates dominant non-semantic directions that artificially
   inflate mutual cosine similarity between unrelated texts.

3. EXECUTION FLOW:
   a. Center vectors by subtracting corpus mean vector.
   b. Compute principal components (SVD or PCA top components u_1, ..., u_k).
   c. For each vector, subtract projections along the top-k components.
   d. Return cleaned vectors with removed direction variance statistics.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoRemoveDominantDirections:
    """
    --- contract:
      id: ALGO-VEC-TRFM-18
      name: VectorTransformAlgoRemoveDominantDirections
      category: transform
      complexity: O(N * D * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        num_components_to_remove: int
      output_schema:
        total_vectors: int
        dimension: int
        components_removed: int
        processed_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def remove_dominant(
        vectors: List[List[float]],
        num_components_to_remove: int = 3,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "dimension": 0,
                "components_removed": 0,
                "processed_vectors": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape

        mean = np.mean(X, axis=0)
        X_centered = X - mean

        k = min(num_components_to_remove, d, n)
        if k > 0:
            _, _, Vt = np.linalg.svd(X_centered, full_matrices=False)
            top_components = Vt[:k, :]
            projection = X_centered @ top_components.T @ top_components
            X_clean = X_centered - projection
        else:
            X_clean = X_centered

        return {
            "total_vectors": n,
            "dimension": d,
            "components_removed": k,
            "processed_vectors": [[round(float(v), 6) for v in row] for row in X_clean],
        }
