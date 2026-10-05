"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MATRYOSHKA EMBEDDING SLICING (ALGO-VEC-05)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Slices high-dimensional embeddings trained with Matryoshka Representation Learning
   (MRL) down to target lower dimensions (e.g. 1536 -> 512, 256, 128, 64) and re-applies
   L2 normalization, providing continuous storage-latency-recall trade-offs.

2. MATHEMATICAL FORMULA:
   Given vector v in R^D and target dimension d <= D:
   v_sliced = v[0..d]
   v_final = v_sliced / max(norm(v_sliced), epsilon)

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Throws clear validation errors if target dimension exceeds input dimension.
================================================================================
"""

from __future__ import annotations
from typing import List
from src.features.code_engine.algos.vector.vector_algo_l2_normalization import VectorAlgoL2Normalization


class VectorAlgoMatryoshkaSlicing:
    """
    ---
    contract:
      algo_id: ALGO-VEC-05
      name: VectorAlgoMatryoshkaSlicing
      version: 1.0.0
      category: vector
      capability_tags: [vector, dimensionality_reduction, mrl, matryoshka, compression]
      inputs:
        type: object
        required: [vector]
        properties:
          vector:
            type: array
            items: {type: number}
      outputs:
        type: array
        items: {type: number}
      parameters:
        target_dim: {type: integer, default: 256}
        renormalize_l2: {type: boolean, default: true}
        epsilon: {type: number, default: 1e-12}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(d)
        space: O(d)
      preconditions:
        - len(vector) >= target_dim
        - target_dim > 0
      postconditions:
        - len(output) == target_dim
    ---
    """

    @staticmethod
    def slice_and_normalize(
        vector: List[float],
        target_dim: int = 256,
        renormalize_l2: bool = True,
        epsilon: float = 1e-12,
    ) -> List[float]:
        if target_dim <= 0:
            raise ValueError(f"Target dimension must be positive, got {target_dim}")
        if len(vector) < target_dim:
            raise ValueError(
                f"Cannot slice vector of dimension {len(vector)} to larger dimension {target_dim}"
            )
        sliced = vector[:target_dim]
        if renormalize_l2:
            return VectorAlgoL2Normalization.normalize_single(sliced, epsilon=epsilon)
        return sliced

    @staticmethod
    def slice_batch(
        vectors: List[List[float]],
        target_dim: int = 256,
        renormalize_l2: bool = True,
        epsilon: float = 1e-12,
    ) -> List[List[float]]:
        return [
            VectorAlgoMatryoshkaSlicing.slice_and_normalize(
                v, target_dim=target_dim, renormalize_l2=renormalize_l2, epsilon=epsilon
            )
            for v in vectors
        ]

    @staticmethod
    def to_qdrant_multivector_point(
        point_id: Any,
        full_vector: List[float],
        coarse_dim: int = 256,
        payload: Optional[dict] = None,
    ) -> dict:
        coarse_vector = VectorAlgoMatryoshkaSlicing.slice_and_normalize(full_vector, target_dim=coarse_dim)
        return {
            "id": point_id,
            "vector": {
                "dense_coarse": coarse_vector,
                "dense_full": full_vector,
            },
            "payload": payload or {},
        }

