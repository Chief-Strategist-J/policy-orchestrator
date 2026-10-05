"""
================================================================================
ALGORITHM BLUEPRINT: SHADOW TRAFFIC RESPONSE COMPARATOR (ALGO-VEC-OBS-196)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Compares live mirrored production search requests between active production index
   and candidate shadow index version: computes Jaccard set overlap, rank correlation,
   and latency differential without impacting user-facing queries.

2. MATHEMATICAL FORMULATION:
   JaccardOverlap = |Prod_TopK ∩ Shadow_TopK| / |Prod_TopK ∪ Shadow_TopK|
   LatencyDifferential% = (ShadowLatency - ProdLatency) / ProdLatency
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoShadowTrafficComparison:
    """
    --- contract:
      id: ALGO-VEC-OBS-196
      name: VectorObservabilityAlgoShadowTrafficComparison
      category: observability
      complexity: O(N * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        comparisons: list[dict[str, Any]]
        min_jaccard_threshold: float
      output_schema:
        evaluated_queries: int
        mean_jaccard_overlap: float
        mean_prod_latency_ms: float
        mean_shadow_latency_ms: float
        latency_change_percent: float
        is_candidate_viable: bool
    ---
    """

    @classmethod
    def compare(
        cls,
        comparisons: List[Dict[str, Any]],
        min_jaccard_threshold: float = 0.70,
    ) -> Dict[str, Any]:
        if not comparisons:
            return {
                "evaluated_queries": 0,
                "mean_jaccard_overlap": 0.0,
                "mean_prod_latency_ms": 0.0,
                "mean_shadow_latency_ms": 0.0,
                "latency_change_percent": 0.0,
                "is_candidate_viable": False,
            }

        jaccards: List[float] = []
        prod_lats: List[float] = []
        shadow_lats: List[float] = []

        for item in comparisons:
            prod_ids = set(item.get("prod_result_ids", []))
            shadow_ids = set(item.get("shadow_result_ids", []))

            union_len = len(prod_ids.union(shadow_ids))
            inter_len = len(prod_ids.intersection(shadow_ids))
            j_score = (inter_len / float(union_len)) if union_len > 0 else 1.0
            jaccards.append(j_score)

            prod_lats.append(float(item.get("prod_latency_ms", 10.0)))
            shadow_lats.append(float(item.get("shadow_latency_ms", 10.0)))

        n = len(jaccards)
        avg_j = sum(jaccards) / float(n) if n > 0 else 0.0
        avg_prod_lat = sum(prod_lats) / float(n) if n > 0 else 0.0
        avg_shadow_lat = sum(shadow_lats) / float(n) if n > 0 else 0.0

        lat_change_pct = ((avg_shadow_lat - avg_prod_lat) / avg_prod_lat * 100.0) if avg_prod_lat > 0 else 0.0
        viable = (avg_j >= min_jaccard_threshold) and (lat_change_pct <= 20.0)

        return {
            "evaluated_queries": n,
            "mean_jaccard_overlap": round(avg_j, 4),
            "mean_prod_latency_ms": round(avg_prod_lat, 2),
            "mean_shadow_latency_ms": round(avg_shadow_lat, 2),
            "latency_change_percent": round(lat_change_pct, 2),
            "is_candidate_viable": viable,
        }
