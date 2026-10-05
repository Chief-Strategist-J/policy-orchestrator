"""
================================================================================
ALGORITHM BLUEPRINT: L2 NORMALIZATION (ALGO-VEC-TRFM-15)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Scales vectors to unit Euclidean norm (||v||_2 = 1.0) on the unit hypersphere.
   Converts inner products into exact cosine similarities, stabilizing distance
   computations across diverse vector dimensions and magnitude variations.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Mandatory post-pooling and post-projection step
   satisfying Rule V3 (identical normalization at index and query time).

3. EXECUTION FLOW:
   a. Compute Euclidean norm ||v||_2 = sqrt(sum(v_i^2)).
   b. If norm <= epsilon, return zero or fallback vector without zero-division.
   c. Divide each element by norm.
   d. Return normalized vector with original and transformed norm metadata.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoL2Norm:
    """
    --- contract:
      id: ALGO-VEC-TRFM-15
      name: VectorTransformAlgoL2Norm
      category: transform
      complexity: O(D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        epsilon: float
      output_schema:
        dimension: int
        original_norm: float
        normalized_vector: list[float]
    ---
    """

    @staticmethod
    def normalize(
        vector: List[float],
        epsilon: float = 1e-12,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "original_norm": 0.0,
                "normalized_vector": [],
            }

        dim = len(vector)
        norm_sq = sum(x ** 2 for x in vector)
        orig_norm = math.sqrt(norm_sq)

        if orig_norm <= epsilon:
            return {
                "dimension": dim,
                "original_norm": 0.0,
                "normalized_vector": [0.0] * dim,
            }

        norm_vec = [round(x / orig_norm, 6) for x in vector]

        return {
            "dimension": dim,
            "original_norm": round(orig_norm, 6),
            "normalized_vector": norm_vec,
        }
