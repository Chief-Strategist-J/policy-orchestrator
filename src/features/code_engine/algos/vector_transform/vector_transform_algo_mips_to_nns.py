"""
================================================================================
ALGORITHM BLUEPRINT: MIPS TO NNS REDUCTION (ALGO-VEC-TRFM-19)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Transforms Maximum Inner Product Search (MIPS) into exact Euclidean Nearest Neighbor
   Search (NNS) via dimension augmentation (Bachrach et al. / Neyshabur & Srebro).
   Enables L2-only vector indexing structures (HNSW, BallTree, KDTree) to execute
   exact inner product search on non-normalized vectors without distortion.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Bridges unnormalized embedding representations to
   metric nearest neighbor index backends.

3. EXECUTION FLOW:
   a. Find maximum L2 norm M = max_x ||x||_2 across database vectors.
   b. Augment each database vector with extra coordinate: x' = [x, sqrt(M^2 - ||x||^2)].
      Notice ||x'||^2 = M^2 (all database vectors now have constant norm M).
   c. Augment query vector with extra zero coordinate: q' = [q, 0].
   d. Now argmin ||q' - x'||_2^2 = argmax (q · x).
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoMIPSToNNS:
    """
    --- contract:
      id: ALGO-VEC-TRFM-19
      name: VectorTransformAlgoMIPSToNNS
      category: transform
      complexity: O(N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        database_vectors: list[list[float]]
        query_vector: list[float]
        max_norm_bound: float
      output_schema:
        original_dimension: int
        augmented_dimension: int
        max_norm: float
        augmented_database_vectors: list[list[float]]
        augmented_query_vector: list[float]
    ---
    """

    @staticmethod
    def reduce_mips_to_nns(
        database_vectors: List[List[float]],
        query_vector: Optional[List[float]] = None,
        max_norm_bound: Optional[float] = None,
    ) -> Dict[str, Any]:
        if not database_vectors:
            return {
                "original_dimension": 0,
                "augmented_dimension": 0,
                "max_norm": 0.0,
                "augmented_database_vectors": [],
                "augmented_query_vector": [],
            }

        orig_dim = len(database_vectors[0])
        norms = [math.sqrt(sum(x ** 2 for x in v)) for v in database_vectors]
        actual_max_norm = max(norms)

        M = max_norm_bound if (max_norm_bound and max_norm_bound >= actual_max_norm) else actual_max_norm
        if M < 1e-12:
            M = 1.0

        augmented_db: List[List[float]] = []
        for v, norm_v in zip(database_vectors, norms):
            slack_sq = max(0.0, M ** 2 - norm_v ** 2)
            extra_coord = math.sqrt(slack_sq)
            aug_v = list(v) + [round(extra_coord, 6)]
            augmented_db.append(aug_v)

        augmented_q: List[float] = []
        if query_vector:
            augmented_q = list(query_vector) + [0.0]

        return {
            "original_dimension": orig_dim,
            "augmented_dimension": orig_dim + 1,
            "max_norm": round(M, 6),
            "augmented_database_vectors": augmented_db,
            "augmented_query_vector": augmented_q,
        }
