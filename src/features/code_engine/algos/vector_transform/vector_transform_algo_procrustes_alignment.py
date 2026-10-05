"""
================================================================================
ALGORITHM BLUEPRINT: ORTHOGONAL PROCRUSTES ALIGNMENT (ALGO-VEC-TRFM-22)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Learns an optimal orthogonal rotation matrix R to align vectors from a source
   embedding space A into a target space B: min_R ||A R - B||_F subject to R^T R = I.
   Computed in closed-form via SVD of M = A^T B = U Σ V^T, yielding R = U V^T.

2. ARCHITECTURAL ROLE:
   Operator & Transformer role (Layer 1). Enables cross-model migration, multilingual
   lexicon mapping, and embedding model stitching without re-indexing the whole corpus.

3. EXECUTION FLOW:
   a. Validate source and target anchor alignment matrices A and B.
   b. Compute cross-product matrix M = A^T B.
   c. Decompose via SVD: U, S, Vt = svd(M).
   d. Compute optimal orthogonal rotation R = U Vt.
   e. Optionally project source vectors into aligned target space: A_aligned = A R.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoProcrustesAlignment:
    """
    --- contract:
      id: ALGO-VEC-TRFM-22
      name: VectorTransformAlgoProcrustesAlignment
      category: transform
      complexity: O(N * D^2 + D^3)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        source_anchors: list[list[float]]
        target_anchors: list[list[float]]
        vectors_to_align: list[list[float]]
      output_schema:
        dimension: int
        anchor_pairs_used: int
        frobenius_error: float
        rotation_matrix: list[list[float]]
        aligned_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def align(
        source_anchors: List[List[float]],
        target_anchors: List[List[float]],
        vectors_to_align: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        if not source_anchors or not target_anchors:
            return {
                "dimension": 0,
                "anchor_pairs_used": 0,
                "frobenius_error": 0.0,
                "rotation_matrix": [],
                "aligned_vectors": [],
            }

        A = np.asarray(source_anchors, dtype=np.float64)
        B = np.asarray(target_anchors, dtype=np.float64)

        if A.shape[0] != B.shape[0] or A.shape[1] != B.shape[1]:
            raise ValueError("Source and target anchors must have identical shapes (N x D)")

        n, d = A.shape

        M = A.T @ B
        U, _, Vt = np.linalg.svd(M)
        R = U @ Vt

        A_rotated = A @ R
        error = float(np.linalg.norm(A_rotated - B, ord="fro"))

        aligned_out: List[List[float]] = []
        if vectors_to_align:
            V = np.asarray(vectors_to_align, dtype=np.float64)
            V_aligned = V @ R
            aligned_out = [[round(float(x), 6) for x in row] for row in V_aligned]

        return {
            "dimension": d,
            "anchor_pairs_used": n,
            "frobenius_error": round(error, 6),
            "rotation_matrix": [[round(float(x), 6) for x in row] for row in R],
            "aligned_vectors": aligned_out,
        }
