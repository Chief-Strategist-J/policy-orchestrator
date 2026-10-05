"""
================================================================================
ALGORITHM BLUEPRINT: RANDOM PROJECTION (JOHNSON-LINDENSTRAUSS) (ALGO-VEC-TRFM-25)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Reduces dimensionality using the Johnson-Lindenstrauss lemma: projecting N vectors
   into d = O(log N / ε^2) dimensions using a random Gaussian or Achlioptas sparse matrix
   preserves pairwise Euclidean distances within (1 ± ε) relative error with high probability.
   Requires zero training data or eigen-decomposition.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Ultra-fast dimensionality reduction that runs in linear
   time without requiring global dataset fitting or synchronization.

3. EXECUTION FLOW:
   a. Seed pseudo-random generator deterministically for repeatability.
   b. Generate random projection matrix R (D x d) from N(0, 1/d) or Achlioptas distribution.
   c. Project input vectors: X_proj = X @ R.
   d. Return dimension-reduced vectors.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoRandomProjection:
    """
    --- contract:
      id: ALGO-VEC-TRFM-25
      name: VectorTransformAlgoRandomProjection
      category: transform
      complexity: O(N * D * target_dim)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        target_dim: int
        seed: int
        density: str
      output_schema:
        original_dim: int
        target_dim: int
        total_vectors: int
        projected_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def project(
        vectors: List[List[float]],
        target_dim: int = 16,
        seed: int = 42,
        density: str = "gaussian",
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "original_dim": 0,
                "target_dim": target_dim,
                "total_vectors": 0,
                "projected_vectors": [],
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        k = target_dim

        rng = np.random.RandomState(seed)

        if density.lower() == "sparse":
            s = 3.0
            probs = [1.0 / (2.0 * s), 1.0 - (1.0 / s), 1.0 / (2.0 * s)]
            vals = [-np.sqrt(s / k), 0.0, np.sqrt(s / k)]
            R = rng.choice(vals, size=(d, k), p=probs)
        else:
            R = rng.normal(loc=0.0, scale=1.0 / np.sqrt(k), size=(d, k))

        Z = X @ R

        return {
            "original_dim": d,
            "target_dim": k,
            "total_vectors": n,
            "projected_vectors": [[round(float(v), 6) for v in row] for row in Z],
        }
