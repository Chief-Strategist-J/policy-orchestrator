"""
================================================================================
ALGORITHM BLUEPRINT: OPTIMIZED PRODUCT QUANTIZATION (OPQ) (ALGO-VEC-TRFM-36)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Optimizes Product Quantization distortion by finding an orthogonal rotation matrix R
   that decorrelates dimensions across subspace boundaries: min_{R, C} ||X R - C(X R)||_F^2
   subject to R^T R = I (Ge et al., 2013). Minimizes quantization distortion by aligning
   correlated features into identical subspaces.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Pre-rotation step before standard PQ indexing, improving
   recall by up to 20% over standard axis-aligned PQ.

3. EXECUTION FLOW:
   a. Apply learned orthogonal rotation matrix R to input vector: x_rot = x @ R.
   b. Decompose rotated vector into M subspaces.
   c. Assign each subspace slice to nearest centroid in rotated codebooks.
   d. Return OPQ codes, rotated vector, and reconstruction fidelity.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoOptimizedProductQuantization:
    """
    --- contract:
      id: ALGO-VEC-TRFM-36
      name: VectorTransformAlgoOptimizedProductQuantization
      category: transform
      complexity: O(D^2 + M * K * d_sub)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        rotation_matrix: list[list[float]]
        m_subspaces: int
        codebooks: list[list[list[float]]]
      output_schema:
        dimension: int
        m_subspaces: int
        rotated_vector: list[float]
        opq_codes: list[int]
        reconstruction_error: float
    ---
    """

    @staticmethod
    def encode_opq(
        vector: List[float],
        rotation_matrix: Optional[List[List[float]]] = None,
        m_subspaces: int = 4,
        codebooks: Optional[List[List[List[float]]]] = None,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "m_subspaces": m_subspaces,
                "rotated_vector": [],
                "opq_codes": [],
                "reconstruction_error": 0.0,
            }

        x = np.asarray(vector, dtype=np.float64)
        d = len(x)

        if rotation_matrix is not None:
            R = np.asarray(rotation_matrix, dtype=np.float64)
            x_rot = x @ R
        else:
            x_rot = x

        m = min(m_subspaces, d)
        d_sub = d // m

        if codebooks is None:
            codebooks = []
            for s in range(m):
                sub_c = [
                    [float(np.sin((s + 1) * (k + 1) * (j + 1) * 0.1)) for j in range(d_sub)]
                    for k in range(8)
                ]
                codebooks.append(sub_c)

        codes: List[int] = []
        recon_rot: List[float] = []

        for s in range(m):
            sub_vec = x_rot[s * d_sub : (s + 1) * d_sub]
            sub_cbook = codebooks[s]

            best_idx = 0
            best_dist = float("inf")

            for k_idx, c in enumerate(sub_cbook):
                dist = float(np.sum((sub_vec - c[: len(sub_vec)]) ** 2))
                if dist < best_dist:
                    best_dist = dist
                    best_idx = k_idx

            codes.append(best_idx)
            recon_rot.extend(sub_cbook[best_idx][: len(sub_vec)])

        recon_arr = np.asarray(recon_rot, dtype=np.float64)
        mse = float(np.mean((x_rot - recon_arr) ** 2))

        return {
            "dimension": d,
            "m_subspaces": m,
            "rotated_vector": [round(float(v), 6) for v in x_rot],
            "opq_codes": codes,
            "reconstruction_error": round(mse, 6),
        }
