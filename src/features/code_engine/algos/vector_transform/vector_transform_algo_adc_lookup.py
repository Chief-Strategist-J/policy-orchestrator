"""
================================================================================
ALGORITHM BLUEPRINT: ASYMMETRIC DISTANCE COMPUTATION (ADC) (ALGO-VEC-TRFM-43)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements Asymmetric Distance Computation (Jégou et al., 2011) where the query
   vector q is kept in uncompressed full FP32 precision, while database vectors are
   represented as M discrete codebook indices. Precomputes an M x K distance lookup
   table D[m, k] = ||q_m - c_{m, k}||^2 so candidate distances require only M table lookups
   and additions without decompressing vectors.

2. ARCHITECTURAL ROLE:
   Retriever & Transformer role (Layer 1). Core sub-millisecond distance evaluator
   for product-quantized vector engines.

3. EXECUTION FLOW:
   a. Divide uncompressed query vector q into M subvectors.
   b. Construct M x K lookup table of squared Euclidean distances to codebook centroids.
   c. For each candidate represented by code tuple [c_1, ..., c_M], sum D[m, c_m].
   d. Return candidate squared distances and lookup table summary.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoADCLookup:
    """
    --- contract:
      id: ALGO-VEC-TRFM-43
      name: VectorTransformAlgoADCLookup
      category: transform
      complexity: O(M * K * d_sub + N_candidates * M)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query_vector: list[float]
        codebooks: list[list[list[float]]]
        candidate_pq_codes: list[list[int]]
      output_schema:
        m_subspaces: int
        subspace_dim: int
        total_candidates: int
        lookup_table_shape: list[int]
        candidate_distances: list[float]
    ---
    """

    @staticmethod
    def compute_adc(
        query_vector: List[float],
        codebooks: List[List[List[float]]],
        candidate_pq_codes: List[List[int]],
    ) -> Dict[str, Any]:
        if not query_vector or not codebooks or not candidate_pq_codes:
            return {
                "m_subspaces": len(codebooks),
                "subspace_dim": 0,
                "total_candidates": len(candidate_pq_codes),
                "lookup_table_shape": [len(codebooks), 0],
                "candidate_distances": [],
            }

        m = len(codebooks)
        dim = len(query_vector)
        d_sub = dim // m
        k_centroids = len(codebooks[0])

        lut: List[List[float]] = []
        for s in range(m):
            q_sub = query_vector[s * d_sub : (s + 1) * d_sub]
            sub_cbook = codebooks[s]
            lut_row: List[float] = []

            for c in sub_cbook:
                d_sq = sum(
                    (q_sub[j] - c[j]) ** 2
                    for j in range(min(len(q_sub), len(c)))
                )
                lut_row.append(d_sq)
            lut.append(lut_row)

        distances: List[float] = []
        for code_tuple in candidate_pq_codes:
            acc = 0.0
            for s in range(min(m, len(code_tuple))):
                c_idx = code_tuple[s]
                if 0 <= c_idx < len(lut[s]):
                    acc += lut[s][c_idx]
            distances.append(round(acc, 6))

        return {
            "m_subspaces": m,
            "subspace_dim": d_sub,
            "total_candidates": len(candidate_pq_codes),
            "lookup_table_shape": [m, k_centroids],
            "candidate_distances": distances,
        }
