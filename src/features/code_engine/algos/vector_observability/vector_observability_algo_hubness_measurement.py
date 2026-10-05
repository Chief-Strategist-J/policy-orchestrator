"""
================================================================================
ALGORITHM BLUEPRINT: HUBNESS MEASUREMENT / K-OCCURRENCE SKEW (ALGO-VEC-OBS-174)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Quantifies the hubness problem in high-dimensional embedding spaces: measures
   k-occurrence frequency distribution across documents and isolates bad hub vectors
   that dominate nearest-neighbor candidate pools.

2. MATHEMATICAL FORMULATION:
   N_k(x) = count of queries where vector x appears in top-k
   Skewness S = (1/N) * sum( (N_k(x) - mean)^3 ) / (std_dev^3)
   Hubs = { x : N_k(x) > mean + 3 * std_dev }
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoHubnessMeasurement:
    """
    --- contract:
      id: ALGO-VEC-OBS-174
      name: VectorObservabilityAlgoHubnessMeasurement
      category: observability
      complexity: O(Q * k + N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        top_k_results: list[list[str]]
        all_document_ids: Optional[list[str]]
        hub_multiplier_threshold: float
      output_schema:
        skewness_score: float
        mean_k_occurrence: float
        top_hubs: list[dict[str, Any]]
        is_high_hubness_detected: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        top_k_results: List[List[str]],
        all_document_ids: Optional[List[str]] = None,
        hub_multiplier_threshold: float = 3.0,
    ) -> Dict[str, Any]:
        if not top_k_results:
            return {
                "skewness_score": 0.0,
                "mean_k_occurrence": 0.0,
                "top_hubs": [],
                "is_high_hubness_detected": False,
            }

        counts: Dict[str, int] = {}
        for result_list in top_k_results:
            for doc_id in result_list:
                counts[doc_id] = counts.get(doc_id, 0) + 1

        if all_document_ids:
            for doc_id in all_document_ids:
                if doc_id not in counts:
                    counts[doc_id] = 0

        freqs = list(counts.values())
        n = len(freqs)
        if n == 0:
            return {
                "skewness_score": 0.0,
                "mean_k_occurrence": 0.0,
                "top_hubs": [],
                "is_high_hubness_detected": False,
            }

        mean_val = sum(freqs) / float(n)
        var_val = sum((x - mean_val) ** 2 for x in freqs) / float(n)
        std_val = math.sqrt(var_val)

        if std_val > 0.0:
            skew = sum((x - mean_val) ** 3 for x in freqs) / (float(n) * (std_val ** 3))
        else:
            skew = 0.0

        hub_cutoff = mean_val + (hub_multiplier_threshold * std_val)
        hubs = []
        for doc_id, c in counts.items():
            if c > hub_cutoff and c > 1:
                hubs.append({"id": doc_id, "k_occurrences": c, "z_score": round((c - mean_val) / std_val, 2) if std_val > 0 else 0.0})

        hubs.sort(key=lambda x: x["k_occurrences"], reverse=True)
        is_high = skew > 2.0 or len(hubs) > 0

        return {
            "skewness_score": round(skew, 4),
            "mean_k_occurrence": round(mean_val, 4),
            "top_hubs": hubs[:20],
            "is_high_hubness_detected": is_high,
        }
