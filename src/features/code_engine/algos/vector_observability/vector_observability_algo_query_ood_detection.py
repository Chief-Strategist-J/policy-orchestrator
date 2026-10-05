"""
================================================================================
ALGORITHM BLUEPRINT: QUERY OUT-OF-DISTRIBUTION (OOD) DETECTOR (ALGO-VEC-OBS-177)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Identifies user queries falling outside corpus semantic coverage by measuring
   min-centroid distances and similarity bounds to prevent hallucinated weak matches.

2. MATHEMATICAL FORMULATION:
   MinCentroidDistance = min_{c in Centroids} ||q - c||_2
   IsOOD = (MinCentroidDistance > ood_distance_threshold) or (Top1Similarity < min_sim_threshold)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoQueryOodDetection:
    """
    --- contract:
      id: ALGO-VEC-OBS-177
      name: VectorObservabilityAlgoQueryOodDetection
      category: observability
      complexity: O(C * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query_vector: list[float]
        corpus_centroids: list[list[float]]
        max_distance_threshold: float
        top1_similarity: Optional[float]
        min_top1_similarity_threshold: float
      output_schema:
        is_ood: bool
        min_centroid_distance: float
        nearest_centroid_index: int
        ood_reason: Optional[str]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        query_vector: List[float],
        corpus_centroids: List[List[float]],
        max_distance_threshold: float = 1.20,
        top1_similarity: Optional[float] = None,
        min_top1_similarity_threshold: float = 0.40,
    ) -> Dict[str, Any]:
        if not query_vector or not corpus_centroids:
            return {
                "is_ood": True,
                "min_centroid_distance": 999.0,
                "nearest_centroid_index": -1,
                "ood_reason": "Missing query vector or corpus centroids",
            }

        min_dist = float("inf")
        best_c_idx = -1

        for idx, c in enumerate(corpus_centroids):
            if len(c) == len(query_vector):
                dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(query_vector, c)))
                if dist < min_dist:
                    min_dist = dist
                    best_c_idx = idx

        is_ood = False
        reason = None

        if min_dist > max_distance_threshold:
            is_ood = True
            reason = f"Distance to nearest cluster centroid ({min_dist:.3f}) exceeds threshold ({max_distance_threshold:.3f})"
        elif top1_similarity is not None and top1_similarity < min_top1_similarity_threshold:
            is_ood = True
            reason = f"Top-1 retrieval similarity ({top1_similarity:.3f}) below coverage threshold ({min_top1_similarity_threshold:.3f})"

        return {
            "is_ood": is_ood,
            "min_centroid_distance": round(min_dist, 4),
            "nearest_centroid_index": best_c_idx,
            "ood_reason": reason,
        }
