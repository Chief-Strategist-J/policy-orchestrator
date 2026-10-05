"""
================================================================================
ALGORITHM BLUEPRINT: MERGEABLE QUANTILE SKETCH (DDSKETCH / T-DIGEST) (ALGO-VEC-OBS-190)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides bounded-memory, mergeable quantile sketch data structures (logarithmic
   bucket DDSketch) allowing cross-shard/cross-replica percentile aggregation without loss of relative accuracy.

2. MATHEMATICAL FORMULATION:
   Bucket index k = floor(ln(val) / ln(gamma)) where gamma = (1 + alpha) / (1 - alpha)
   Percentile lookup: accumulate bucket counts to rank q * TotalCount
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoQuantileSketches:
    """
    --- contract:
      id: ALGO-VEC-OBS-190
      name: VectorObservabilityAlgoQuantileSketches
      category: observability
      complexity: O(N + B log B)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        shard_data_streams: list[list[float]]
        relative_error_alpha: float
        quantiles_to_query: Optional[list[float]]
      output_schema:
        total_count: int
        quantiles: dict[str, float]
        merged_bucket_count: int
    ---
    """

    @classmethod
    def evaluate(
        cls,
        shard_data_streams: List[List[float]],
        relative_error_alpha: float = 0.01,
        quantiles_to_query: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not shard_data_streams:
            return {
                "total_count": 0,
                "quantiles": {},
                "merged_bucket_count": 0,
            }

        alpha = max(0.001, min(0.2, relative_error_alpha))
        gamma = (1.0 + alpha) / (1.0 - alpha)
        ln_gamma = math.log(gamma)

        def make_sketch(values: List[float]) -> Dict[int, int]:
            buckets: Dict[int, int] = {}
            for v in values:
                if v > 0.0:
                    k = int(math.floor(math.log(v) / ln_gamma))
                    buckets[k] = buckets.get(k, 0) + 1
            return buckets

        merged_sketch: Dict[int, int] = {}
        total_items = 0
        for stream in shard_data_streams:
            s_buckets = make_sketch(stream)
            total_items += len(stream)
            for k, count in s_buckets.items():
                merged_sketch[k] = merged_sketch.get(k, 0) + count

        if not merged_sketch or total_items == 0:
            return {
                "total_count": 0,
                "quantiles": {},
                "merged_bucket_count": 0,
            }

        sorted_buckets = sorted(merged_sketch.items(), key=lambda x: x[0])
        queries = quantiles_to_query or [0.50, 0.90, 0.95, 0.99]
        quant_results: Dict[str, float] = {}

        for q in queries:
            target_rank = int(math.ceil(q * total_items))
            cum_count = 0
            est_val = 0.0
            for k, count in sorted_buckets:
                cum_count += count
                if cum_count >= target_rank:
                    est_val = math.exp((k + 0.5) * ln_gamma)
                    break
            quant_results[f"p{int(q*100)}"] = round(est_val, 2)

        return {
            "total_count": total_items,
            "quantiles": quant_results,
            "merged_bucket_count": len(merged_sketch),
        }
