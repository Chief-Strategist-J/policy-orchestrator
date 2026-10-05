"""
================================================================================
ALGORITHM BLUEPRINT: EMBEDDING OUTLIER DETECTION (K-NN / LOF) (ALGO-VEC-OBS-176)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Identifies poisoned, corrupt, spam, or garbled text vectors using k-NN distance
   and density thresholding to quarantine out-of-boundary embeddings.

2. MATHEMATICAL FORMULATION:
   OutlierScore(x) = (1/k) * sum_{y in N_k(x)} dist(x, y)
   IsOutlier(x) = OutlierScore(x) > mean(scores) + threshold_std * std_dev(scores)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoOutlierDetection:
    """
    --- contract:
      id: ALGO-VEC-OBS-176
      name: VectorObservabilityAlgoOutlierDetection
      category: observability
      complexity: O(N^2 * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[dict[str, Any]]
        k_neighbors: int
        outlier_z_threshold: float
      output_schema:
        total_examined: int
        outlier_count: int
        outlier_records: list[dict[str, Any]]
        mean_knn_distance: float
    ---
    """

    @classmethod
    def evaluate(
        cls,
        vectors: List[Dict[str, Any]],
        k_neighbors: int = 5,
        outlier_z_threshold: float = 2.5,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_examined": 0,
                "outlier_count": 0,
                "outlier_records": [],
                "mean_knn_distance": 0.0,
            }

        n = len(vectors)
        k = min(max(1, k_neighbors), max(1, n - 1))
        scores: List[float] = []

        for i in range(n):
            v_i = vectors[i].get("vector", [])
            dists = []
            for j in range(n):
                if i != j:
                    v_j = vectors[j].get("vector", [])
                    if len(v_i) == len(v_j):
                        d = math.sqrt(sum((a - b) ** 2 for a, b in zip(v_i, v_j)))
                        dists.append(d)
            dists.sort()
            top_k_dists = dists[:k]
            avg_dist = sum(top_k_dists) / float(len(top_k_dists)) if top_k_dists else 0.0
            scores.append(avg_dist)

        mean_s = sum(scores) / float(n) if n > 0 else 0.0
        var_s = sum((s - mean_s) ** 2 for s in scores) / float(n) if n > 0 else 0.0
        std_s = math.sqrt(var_s)

        outliers = []
        for idx in range(n):
            z = (scores[idx] - mean_s) / std_s if std_s > 0 else 0.0
            if z > outlier_z_threshold:
                rec_id = vectors[idx].get("id", f"vec-{idx}")
                outliers.append({
                    "id": rec_id,
                    "knn_distance": round(scores[idx], 4),
                    "z_score": round(z, 2),
                })

        return {
            "total_examined": n,
            "outlier_count": len(outliers),
            "outlier_records": outliers,
            "mean_knn_distance": round(mean_s, 4),
        }
