"""
================================================================================
ALGORITHM BLUEPRINT: CENTROID SHIFT DRIFT DETECTOR (ALGO-VEC-OBS-168)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Measures Euclidean and Cosine drift of global embedding centroids and per-cluster
   centroids between a baseline reference period and the current observation window.

2. MATHEMATICAL FORMULATION:
   Centroid = (1/N) * sum_{i=1}^N v_i
   Shift_L2 = ||Centroid_current - Centroid_ref||_2
   Shift_Cosine = 1 - (Centroid_current . Centroid_ref) / (||C_curr|| * ||C_ref||)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoCentroidShift:
    """
    --- contract:
      id: ALGO-VEC-OBS-168
      name: VectorObservabilityAlgoCentroidShift
      category: observability
      complexity: O(N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        reference_vectors: list[list[float]]
        current_vectors: list[list[float]]
        drift_threshold: float
      output_schema:
        global_centroid_shift_l2: float
        global_centroid_shift_cosine: float
        is_drift_detected: bool
        reference_centroid: list[float]
        current_centroid: list[float]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        reference_vectors: List[List[float]],
        current_vectors: List[List[float]],
        drift_threshold: float = 0.10,
    ) -> Dict[str, Any]:
        if not reference_vectors or not current_vectors:
            return {
                "global_centroid_shift_l2": 0.0,
                "global_centroid_shift_cosine": 0.0,
                "is_drift_detected": False,
                "reference_centroid": [],
                "current_centroid": [],
            }

        dim = len(reference_vectors[0])

        def compute_mean_vector(vectors: List[List[float]]) -> List[float]:
            n = float(len(vectors))
            mean_v = [0.0] * dim
            for v in vectors:
                for d in range(min(dim, len(v))):
                    mean_v[d] += v[d]
            return [val / n for val in mean_v]

        c_ref = compute_mean_vector(reference_vectors)
        c_curr = compute_mean_vector(current_vectors)

        l2_dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(c_ref, c_curr)))

        dot = sum(a * b for a, b in zip(c_ref, c_curr))
        norm_ref = math.sqrt(sum(a * a for a in c_ref))
        norm_curr = math.sqrt(sum(b * b for b in c_curr))
        if norm_ref == 0.0 or norm_curr == 0.0:
            cosine_dist = 0.0
        else:
            cosine_dist = 1.0 - (dot / (norm_ref * norm_curr))

        is_drift = l2_dist > drift_threshold or cosine_dist > drift_threshold

        return {
            "global_centroid_shift_l2": round(l2_dist, 4),
            "global_centroid_shift_cosine": round(max(0.0, cosine_dist), 4),
            "is_drift_detected": is_drift,
            "reference_centroid": [round(x, 4) for x in c_ref],
            "current_centroid": [round(x, 4) for x in c_curr],
        }
