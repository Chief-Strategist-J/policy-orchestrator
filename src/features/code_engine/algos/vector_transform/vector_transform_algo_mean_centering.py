"""
================================================================================
ALGORITHM BLUEPRINT: MEAN CENTERING (ALGO-VEC-TRFM-16)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Translates vectors to zero empirical mean across the corpus: v' = v - μ.
   Removes static global bias directions and shifts the vector cluster origin to
   the coordinate center, increasing effective angular dispersion.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Preprocessing step prior to PCA whitening,
   quantization, or angular cosine indexing.

3. EXECUTION FLOW:
   a. If mean vector μ is provided, subtract μ from input vector.
   b. If batch of vectors is provided without μ, calculate empirical mean μ_batch.
   c. Subtract mean vector from each input vector.
   d. Return centered vectors and the mean vector used for provenance tracking.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorTransformAlgoMeanCentering:
    """
    --- contract:
      id: ALGO-VEC-TRFM-16
      name: VectorTransformAlgoMeanCentering
      category: transform
      complexity: O(N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        corpus_mean: list[float]
      output_schema:
        total_vectors: int
        dimension: int
        applied_mean: list[float]
        centered_vectors: list[list[float]]
    ---
    """

    @staticmethod
    def center(
        vectors: List[List[float]],
        corpus_mean: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "dimension": 0,
                "applied_mean": [],
                "centered_vectors": [],
            }

        n = len(vectors)
        dim = len(vectors[0])

        if corpus_mean is None:
            mean = [0.0] * dim
            for v in vectors:
                for d in range(dim):
                    mean[d] += v[d]
            mean = [round(m / n, 6) for m in mean]
        else:
            mean = corpus_mean

        centered: List[List[float]] = []
        for v in vectors:
            centered.append([
                round(v[d] - mean[d], 6) for d in range(min(dim, len(mean)))
            ])

        return {
            "total_vectors": n,
            "dimension": dim,
            "applied_mean": mean,
            "centered_vectors": centered,
        }
