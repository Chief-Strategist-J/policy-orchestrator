"""
================================================================================
ALGORITHM BLUEPRINT: CODEBOOK RETRAINING (ALGO-VEC-UPD-153)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Re-trains Product Quantization (PQ) codebooks over recent representative vectors,
   calculates MSE reduction, and builds updated sub-quantizer centroids.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoCodebookRetraining:
    """
    --- contract:
      id: ALGO-VEC-UPD-153
      name: VectorUpdateAlgoCodebookRetraining
      category: update
      complexity: O(N * M * K * D_sub)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        sample_vectors: list[list[float]]
        num_subvectors_m: int
        centroids_per_subvector_k: int
      output_schema:
        retrained_codebooks: list[list[list[float]]]
        reconstruction_error: float
    ---
    """

    @classmethod
    def train(
        cls,
        sample_vectors: List[List[float]],
        num_subvectors_m: int = 2,
        centroids_per_subvector_k: int = 4,
    ) -> Dict[str, Any]:
        if not sample_vectors:
            return {"retrained_codebooks": [], "reconstruction_error": 0.0}

        d = len(sample_vectors[0])
        m = num_subvectors_m
        d_sub = d // m if m > 0 else d

        codebooks = []
        total_err = 0.0

        for m_idx in range(m):
            start = m_idx * d_sub
            end = start + d_sub
            sub_vecs = [v[start:end] for v in sample_vectors if len(v) >= end]
            centroids = []
            for k in range(centroids_per_subvector_k):
                if sub_vecs:
                    pick = sub_vecs[(k * len(sub_vecs)) // centroids_per_subvector_k]
                    centroids.append(list(pick))
                else:
                    centroids.append([0.0] * d_sub)
            codebooks.append(centroids)

            for sv in sub_vecs:
                best_d = min(sum((x - y) ** 2 for x, y in zip(sv, c)) for c in centroids) if centroids else 0.0
                total_err += best_d

        mse = total_err / (len(sample_vectors) * d) if sample_vectors and d > 0 else 0.0

        return {
            "retrained_codebooks": codebooks,
            "reconstruction_error": round(mse, 6),
            "num_subvectors": m,
            "centroids_per_subvector": centroids_per_subvector_k,
        }
