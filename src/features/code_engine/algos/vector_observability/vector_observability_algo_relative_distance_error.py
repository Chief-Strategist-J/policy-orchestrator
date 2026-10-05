"""
================================================================================
ALGORITHM BLUEPRINT: RELATIVE DISTANCE ERROR (RDE) (ALGO-VEC-OBS-162)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates the relative distance error between approximate nearest neighbor
   returned distances and exact brute force true nearest neighbor distances.

2. MATHEMATICAL FORMULATION:
   RDE_i,j = (approx_dist_i,j - exact_dist_i,j) / max(exact_dist_i,j, eps)
   MeanRDE = (1 / (N * k)) * sum_{i,j} RDE_i,j
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoRelativeDistanceError:
    """
    --- contract:
      id: ALGO-VEC-OBS-162
      name: VectorObservabilityAlgoRelativeDistanceError
      category: observability
      complexity: O(N * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        approximate_distances: list[list[float]]
        exact_distances: list[list[float]]
        eps: float
      output_schema:
        mean_relative_distance_error: float
        max_relative_distance_error: float
        per_query_mean_rde: list[float]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        approximate_distances: List[List[float]],
        exact_distances: List[List[float]],
        eps: float = 1e-6,
    ) -> Dict[str, Any]:
        if not approximate_distances or not exact_distances:
            return {
                "mean_relative_distance_error": 0.0,
                "max_relative_distance_error": 0.0,
                "per_query_mean_rde": [],
            }

        num_queries = min(len(approximate_distances), len(exact_distances))
        all_errors: List[float] = []
        per_query: List[float] = []

        for i in range(num_queries):
            approx_k = approximate_distances[i]
            exact_k = exact_distances[i]
            k_len = min(len(approx_k), len(exact_k))
            if k_len == 0:
                per_query.append(0.0)
                continue

            query_errs = []
            for j in range(k_len):
                d_approx = approx_k[j]
                d_exact = exact_k[j]
                denom = max(abs(d_exact), eps)
                err = abs(d_approx - d_exact) / denom
                query_errs.append(err)
                all_errors.append(err)

            per_query.append(sum(query_errs) / float(len(query_errs)))

        mean_rde = sum(all_errors) / float(len(all_errors)) if all_errors else 0.0
        max_rde = max(all_errors) if all_errors else 0.0

        return {
            "mean_relative_distance_error": round(mean_rde, 4),
            "max_relative_distance_error": round(max_rde, 4),
            "per_query_mean_rde": [round(e, 4) for e in per_query],
        }
