"""
================================================================================
ALGORITHM BLUEPRINT: ANISOTROPIC QUANTIZATION (SCANN) (ALGO-VEC-TRFM-38)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Decomposes quantization error e = x - x_hat into parallel (e_parallel) and
   orthogonal (e_ortho) components relative to vector x (Guo et al., ScaNN).
   Penalizes parallel error more heavily (loss = ||e_ortho||^2 + h_parallel · ||e_parallel||^2),
   ensuring inner product rank order is preserved during quantized retrieval.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). ScaNN-style quantization delivering maximum recall
   under dot-product maximum inner product search.

3. EXECUTION FLOW:
   a. Compute unit projection direction along vector x.
   b. For candidate centroids, project quantization error e into parallel and orthogonal components.
   c. Evaluate anisotropic weighted objective.
   d. Select centroid minimizing anisotropic loss.
   e. Return selected centroid code, loss breakdown, and reconstructed representation.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoAnisotropicQuantization:
    """
    --- contract:
      id: ALGO-VEC-TRFM-38
      name: VectorTransformAlgoAnisotropicQuantization
      category: transform
      complexity: O(K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        centroids: list[list[float]]
        parallel_weight: float
      output_schema:
        dimension: int
        selected_centroid_idx: int
        total_loss: float
        parallel_error: float
        orthogonal_error: float
        quantized_vector: list[float]
    ---
    """

    @staticmethod
    def quantize_anisotropic(
        vector: List[float],
        centroids: Optional[List[List[float]]] = None,
        parallel_weight: float = 0.2,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "selected_centroid_idx": -1,
                "total_loss": 0.0,
                "parallel_error": 0.0,
                "orthogonal_error": 0.0,
                "quantized_vector": [],
            }

        dim = len(vector)
        norm_x = math.sqrt(sum(x ** 2 for x in vector))
        unit_x = [x / norm_x for x in vector] if norm_x > 1e-12 else [0.0] * dim

        if centroids is None:
            centroids = [
                [math.sin((k + 1) * (j + 1) * 0.1) for j in range(dim)]
                for k in range(8)
            ]

        best_idx = 0
        best_loss = float("inf")
        best_par = 0.0
        best_orth = 0.0

        for idx, c in enumerate(centroids):
            e = [vector[j] - c[j] for j in range(min(dim, len(c)))]

            dot_par = sum(e[j] * unit_x[j] for j in range(len(e)))
            e_par_sq = dot_par ** 2

            total_e_sq = sum(x ** 2 for x in e)
            e_orth_sq = max(0.0, total_e_sq - e_par_sq)

            loss = e_orth_sq + parallel_weight * e_par_sq

            if loss < best_loss:
                best_loss = loss
                best_idx = idx
                best_par = math.sqrt(e_par_sq)
                best_orth = math.sqrt(e_orth_sq)

        chosen = centroids[best_idx]

        return {
            "dimension": dim,
            "selected_centroid_idx": best_idx,
            "total_loss": round(best_loss, 6),
            "parallel_error": round(best_par, 6),
            "orthogonal_error": round(best_orth, 6),
            "quantized_vector": [round(x, 6) for x in chosen[:dim]],
        }
