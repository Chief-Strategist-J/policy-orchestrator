"""
================================================================================
ALGORITHM BLUEPRINT: PARTITION & CLUSTER BALANCE MONITOR (ALGO-VEC-OBS-173)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Measures structural skew across inverted index lists (IVF centroids), shards,
   and partition buckets using Coefficient of Variation (CV) and Gini Coefficient.

2. MATHEMATICAL FORMULATION:
   Gini = sum_{i=1}^P sum_{j=1}^P |s_i - s_j| / (2 * P * sum(s_i))
   CV = std_dev(sizes) / mean(sizes)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoPartitionClusterBalance:
    """
    --- contract:
      id: ALGO-VEC-OBS-173
      name: VectorObservabilityAlgoPartitionClusterBalance
      category: observability
      complexity: O(P log P)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        partition_sizes: list[int]
        max_allowed_imbalance_ratio: float
      output_schema:
        total_vectors: int
        partition_count: int
        mean_size: float
        max_size: int
        min_size: int
        gini_coefficient: float
        coefficient_of_variation: float
        is_rebalance_recommended: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        partition_sizes: List[int],
        max_allowed_imbalance_ratio: float = 3.0,
    ) -> Dict[str, Any]:
        if not partition_sizes:
            return {
                "total_vectors": 0,
                "partition_count": 0,
                "mean_size": 0.0,
                "max_size": 0,
                "min_size": 0,
                "gini_coefficient": 0.0,
                "coefficient_of_variation": 0.0,
                "is_rebalance_recommended": False,
            }

        p = len(partition_sizes)
        total = sum(partition_sizes)
        mean_s = total / float(p) if p > 0 else 0.0
        max_s = max(partition_sizes)
        min_s = min(partition_sizes)

        var_s = sum((s - mean_s) ** 2 for s in partition_sizes) / float(p) if p > 0 else 0.0
        cv = (math.sqrt(var_s) / mean_s) if mean_s > 0 else 0.0

        sorted_s = sorted(partition_sizes)
        gini_num = sum((2 * i - p - 1) * val for i, val in enumerate(sorted_s, start=1))
        gini_den = p * total if total > 0 else 1
        gini = gini_num / float(gini_den) if total > 0 else 0.0

        imbalance_ratio = (max_s / float(mean_s)) if mean_s > 0 else 1.0
        rebalance = gini > 0.40 or cv > 0.75 or imbalance_ratio > max_allowed_imbalance_ratio

        return {
            "total_vectors": total,
            "partition_count": p,
            "mean_size": round(mean_s, 2),
            "max_size": max_s,
            "min_size": min_s,
            "gini_coefficient": round(max(0.0, gini), 4),
            "coefficient_of_variation": round(cv, 4),
            "is_rebalance_recommended": rebalance,
        }
