"""
================================================================================
ALGORITHM BLUEPRINT: RESIDUAL & ADDITIVE QUANTIZATION (ALGO-VEC-TRFM-37)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Quantizes vectors across M sequential residual stages (RQ) or additive codebooks (AQ):
   Stage 1: c_1 = argmin ||x - c||, r_1 = x - c_1.
   Stage 2: c_2 = argmin ||r_1 - c||, r_2 = r_1 - c_2.
   Reconstruction: x_hat = sum_{m=1}^M c_m.
   Yields exponentially smaller quantization error than single-stage quantization.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Multi-tier quantization allowing progressive refinement
   of candidate vectors during high-precision search.

3. EXECUTION FLOW:
   a. Initialize residual r_0 = x.
   b. For stage m = 1..M, find nearest codebook centroid to r_{m-1}.
   c. Record chosen centroid index in code tuple.
   d. Compute next residual r_m = r_{m-1} - c_m.
   e. Return stage codes, reconstructed vector, and stage-by-stage residual norms.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoResidualQuantization:
    """
    --- contract:
      id: ALGO-VEC-TRFM-37
      name: VectorTransformAlgoResidualQuantization
      category: transform
      complexity: O(M_stages * K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        num_stages: int
        stage_codebooks: list[list[list[float]]]
      output_schema:
        dimension: int
        num_stages: int
        stage_codes: list[int]
        residual_norms: list[float]
        reconstructed_vector: list[float]
    ---
    """

    @staticmethod
    def quantize_residual(
        vector: List[float],
        num_stages: int = 3,
        stage_codebooks: Optional[List[List[List[float]]]] = None,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "num_stages": num_stages,
                "stage_codes": [],
                "residual_norms": [],
                "reconstructed_vector": [],
            }

        dim = len(vector)
        m = num_stages

        if stage_codebooks is None:
            stage_codebooks = []
            for s in range(m):
                scale = 1.0 / (2.0 ** s)
                stage_centroids = [
                    [math.sin((s + 1) * (k + 1) * (j + 1) * 0.1) * scale for j in range(dim)]
                    for k in range(8)
                ]
                stage_codebooks.append(stage_centroids)

        current_res = list(vector)
        codes: List[int] = []
        residual_norms: List[float] = []
        reconstruction = [0.0] * dim

        for s in range(min(m, len(stage_codebooks))):
            norm_res = math.sqrt(sum(x ** 2 for x in current_res))
            residual_norms.append(round(norm_res, 6))

            cbook = stage_codebooks[s]
            best_idx = 0
            best_dist = float("inf")

            for k_idx, centroid in enumerate(cbook):
                dist = sum(
                    (current_res[j] - centroid[j]) ** 2
                    for j in range(min(dim, len(centroid)))
                )
                if dist < best_dist:
                    best_dist = dist
                    best_idx = k_idx

            codes.append(best_idx)
            chosen_c = cbook[best_idx]

            for d in range(dim):
                reconstruction[d] += chosen_c[d]
                current_res[d] -= chosen_c[d]

        final_norm = math.sqrt(sum(x ** 2 for x in current_res))
        residual_norms.append(round(final_norm, 6))

        return {
            "dimension": dim,
            "num_stages": len(codes),
            "stage_codes": codes,
            "residual_norms": residual_norms,
            "reconstructed_vector": [round(x, 6) for x in reconstruction],
        }
