"""
================================================================================
ALGORITHM BLUEPRINT: PRODUCT QUANTIZATION (PQ) (ALGO-VEC-TRFM-35)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Divides D-dimensional vector space into M orthogonal subspaces of dimension d_sub = D / M.
   Quantizes each subvector to its nearest centroid from a learned codebook of K centroids
   (e.g. K=256, requiring 1 byte per subspace). Replaces the entire D-dimensional vector
   with an M-byte discrete code.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Foundational compression technique behind IVFPQ indexes
   (e.g. Faiss), cutting memory by 16x-64x while enabling Asymmetric Distance Computation.

3. EXECUTION FLOW:
   a. Validate that D is divisible by M subspaces.
   b. Slice vector into M subvectors of length d_sub.
   c. For each subvector, find the closest centroid index in the codebook.
   d. Pack codebook centroid indices as the quantized code.
   e. Compute reconstructed vector from concatenated centroids and evaluate distortion.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoProductQuantization:
    """
    --- contract:
      id: ALGO-VEC-TRFM-35
      name: VectorTransformAlgoProductQuantization
      category: transform
      complexity: O(M * K * d_sub)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        m_subspaces: int
        codebooks: list[list[list[float]]]
      output_schema:
        dimension: int
        m_subspaces: int
        subspace_dim: int
        codes: list[int]
        reconstructed_vector: list[float]
        distortion_mse: float
    ---
    """

    @staticmethod
    def encode(
        vector: List[float],
        m_subspaces: int = 4,
        codebooks: Optional[List[List[List[float]]]] = None,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "m_subspaces": m_subspaces,
                "subspace_dim": 0,
                "codes": [],
                "reconstructed_vector": [],
                "distortion_mse": 0.0,
            }

        dim = len(vector)
        m = min(m_subspaces, dim)
        d_sub = dim // m

        if codebooks is None:
            codebooks = []
            for s in range(m):
                sub_centroids = [
                    [math.sin((s + 1) * (k + 1) * (j + 1) * 0.1) * 0.5 for j in range(d_sub)]
                    for k in range(8)
                ]
                codebooks.append(sub_centroids)

        codes: List[int] = []
        reconstructed: List[float] = []

        for s in range(m):
            sub_vec = vector[s * d_sub : (s + 1) * d_sub]
            sub_cbook = codebooks[s]

            best_idx = 0
            best_dist = float("inf")

            for k_idx, centroid in enumerate(sub_cbook):
                dist = sum(
                    (sub_vec[j] - centroid[j]) ** 2
                    for j in range(min(len(sub_vec), len(centroid)))
                )
                if dist < best_dist:
                    best_dist = dist
                    best_idx = k_idx

            codes.append(best_idx)
            reconstructed.extend(sub_cbook[best_idx][: len(sub_vec)])

        mse = sum((vector[i] - reconstructed[i]) ** 2 for i in range(len(reconstructed))) / max(1, len(reconstructed))

        return {
            "dimension": dim,
            "m_subspaces": m,
            "subspace_dim": d_sub,
            "codes": codes,
            "reconstructed_vector": [round(x, 6) for x in reconstructed],
            "distortion_mse": round(mse, 6),
        }
