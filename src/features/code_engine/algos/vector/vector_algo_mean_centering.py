"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR MEAN CENTERING (ALGO-VEC-02)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates and subtracts the corpus mean vector from all vectors to eliminate
   vector space anisotropy (directional bunching where all cosine similarities cluster
   in high ranges like 0.75-0.95), restoring angular variance and discriminative power.

2. MATHEMATICAL FORMULA:
   mean_vector[j] = (1 / N) * sum(vectors[i][j] for i in 1..N)
   centered_vector[i][j] = vectors[i][j] - mean_vector[j]

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Preserves dimensionality and supports optional post-centering L2 normalization.
================================================================================
"""

from __future__ import annotations
from typing import List, Tuple
from src.features.code_engine.algos.vector.vector_algo_l2_normalization import VectorAlgoL2Normalization


class VectorAlgoMeanCentering:
    """
    ---
    contract:
      algo_id: ALGO-VEC-02
      name: VectorAlgoMeanCentering
      version: 1.0.0
      category: vector
      capability_tags: [vector, normalization, mean_centering, anisotropy_removal]
      inputs:
        type: object
        required: [vectors]
        properties:
          vectors:
            type: array
            items:
              type: array
              items: {type: number}
      outputs:
        type: object
        required: [centered_vectors, mean_vector]
        properties:
          centered_vectors:
            type: array
            items: {type: array, items: {type: number}}
          mean_vector:
            type: array
            items: {type: number}
      parameters:
        renormalize_l2: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: non_idempotent
      reversibility: reversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N * D)
        space: O(N * D)
      preconditions:
        - len(vectors) > 0
        - all(len(v) == len(vectors[0]) for v in vectors)
      postconditions:
        - len(centered_vectors) == len(vectors)
    ---
    """

    @staticmethod
    def compute_corpus_mean(vectors: List[List[float]]) -> List[float]:
        if not vectors:
            return []
        dim = len(vectors[0])
        count = len(vectors)
        mean_vec = [0.0] * dim
        for v in vectors:
            for d in range(dim):
                mean_vec[d] += v[d]
        inv_count = 1.0 / count
        return [m * inv_count for m in mean_vec]

    @staticmethod
    def center_vectors(
        vectors: List[List[float]],
        mean_vector: List[float] | None = None,
        renormalize_l2: bool = True,
    ) -> Tuple[List[List[float]], List[float]]:
        if not vectors:
            return [], []
        mean_vec = mean_vector if mean_vector is not None else VectorAlgoMeanCentering.compute_corpus_mean(vectors)
        dim = len(mean_vec)
        centered: List[List[float]] = []
        for v in vectors:
            c_vec = [v[d] - mean_vec[d] for d in range(dim)]
            if renormalize_l2:
                c_vec = VectorAlgoL2Normalization.normalize_single(c_vec)
            centered.append(c_vec)
        return centered, mean_vec
