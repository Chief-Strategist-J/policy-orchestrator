"""
================================================================================
ALGORITHM BLUEPRINT: INTRINSIC DIMENSIONALITY ESTIMATOR (TWO-NN) (ALGO-VEC-OBS-175)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Estimates the true intrinsic topological dimensionality of high-dimensional embedding
   spaces using the Two-NN algorithm (ratio of distances to 1st and 2nd nearest neighbors).

2. MATHEMATICAL FORMULATION:
   mu_i = r_{i,2} / r_{i,1}
   Cumulative Empirical Distribution F(mu) = 1 - mu^{-d}
   Intrinsic Dimension d_MLE = N / sum_{i=1}^N ln(mu_i)
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoIntrinsicDimension:
    """
    --- contract:
      id: ALGO-VEC-OBS-175
      name: VectorObservabilityAlgoIntrinsicDimension
      category: observability
      complexity: O(N^2 * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        sample_size: Optional[int]
      output_schema:
        estimated_intrinsic_dimension: float
        nominal_dimension: int
        dimension_compression_ratio: float
        two_nn_sample_count: int
    ---
    """

    @classmethod
    def evaluate(
        cls,
        vectors: List[List[float]],
        sample_size: Optional[int] = 100,
    ) -> Dict[str, Any]:
        if not vectors or len(vectors) < 3:
            return {
                "estimated_intrinsic_dimension": 0.0,
                "nominal_dimension": len(vectors[0]) if vectors else 0,
                "dimension_compression_ratio": 1.0,
                "two_nn_sample_count": 0,
            }

        nominal_d = len(vectors[0])
        n = len(vectors)
        limit = min(n, sample_size) if sample_size is not None and sample_size > 0 else n

        sampled_indices = list(range(limit))
        log_mu_sum = 0.0
        valid_samples = 0
        eps = 1e-7

        for i in sampled_indices:
            v_i = vectors[i]
            dists: List[float] = []
            for j in range(n):
                if i != j:
                    v_j = vectors[j]
                    dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(v_i, v_j)))
                    dists.append(dist)

            dists.sort()
            if len(dists) >= 2:
                r1 = max(dists[0], eps)
                r2 = max(dists[1], r1 + eps)
                mu = r2 / r1
                if mu > 1.0:
                    log_mu_sum += math.log(mu)
                    valid_samples += 1

        if valid_samples > 0 and log_mu_sum > 0:
            d_est = float(valid_samples) / log_mu_sum
        else:
            d_est = float(nominal_d)

        d_clamped = max(1.0, min(float(nominal_d), d_est))
        ratio = d_clamped / float(nominal_d) if nominal_d > 0 else 1.0

        return {
            "estimated_intrinsic_dimension": round(d_clamped, 2),
            "nominal_dimension": nominal_d,
            "dimension_compression_ratio": round(ratio, 4),
            "two_nn_sample_count": valid_samples,
        }
