"""
================================================================================
ALGORITHM BLUEPRINT: VECTOR SELECTIVITY-BASED QUERY PLANNING (ALGO-VEC-FLTR-83)
================================================================================

Selectivity-based query planning estimates candidate selectivity (|S_match| / |N|)
and dynamically determines the optimal filtering execution plan. If the filter
involves security/tenant boundaries, pre-filtering or physical partition routing is
mandated (VG1). Otherwise, highly selective filters (< 5%) dispatch to pre-filtered
exact scanning, moderate selectivity (5% - 40%) dispatches to in-graph ACORN traversal,
and low selectivity (> 40%) routes to post-filtering with oversampling.
"""

from typing import Any, Dict, List, Optional


class VectorFilterAlgoSelectivityPlanner:
    """
    --- contract:
      id: ALGO-VEC-FLTR-83
      name: VectorFilterAlgoSelectivityPlanner
      category: filter
      complexity: O(|M|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        total_vectors: int
        metadata_sample: list[dict[str, any]]
        filters: dict[str, any]
        is_security_filter: bool
      output_schema:
        selectivity_ratio: float
        estimated_matching_vectors: int
        selected_strategy: str
        rationale: str
        recommended_params: dict[str, any]
    ---
    """

    @staticmethod
    def _matches_filters(item_meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if key not in item_meta:
                return False
            val = item_meta[key]
            if isinstance(expected, list):
                if val not in expected:
                    return False
            elif val != expected:
                return False
        return True

    @staticmethod
    def plan(
        total_vectors: int,
        metadata_sample: List[Dict[str, Any]],
        filters: Dict[str, Any],
        is_security_filter: bool = False,
    ) -> Dict[str, Any]:
        if total_vectors <= 0:
            return {
                "selectivity_ratio": 0.0,
                "estimated_matching_vectors": 0,
                "selected_strategy": "pre_filter_brute_force",
                "rationale": "Empty collection; default to pre-filtering",
                "recommended_params": {},
            }

        sample_size = len(metadata_sample)
        if sample_size > 0:
            matches = sum(1 for m in metadata_sample if VectorFilterAlgoSelectivityPlanner._matches_filters(m, filters))
            ratio = matches / sample_size
        else:
            ratio = 1.0

        est_matching = int(round(ratio * total_vectors))

        if is_security_filter:
            return {
                "selectivity_ratio": ratio,
                "estimated_matching_vectors": est_matching,
                "selected_strategy": "pre_filter_isolated",
                "rationale": "Mandatory tenant/security filter (VG1): post-filtering strictly prohibited",
                "recommended_params": {"enforce_strict_prefilter": True},
            }

        if ratio < 0.05 or est_matching < 1000:
            strategy = "pre_filter_brute_force"
            rationale = "High selectivity (<= 5%): pre-filtered exact scoring offers optimal latency and 100% recall"
            params = {"prefilter_batch_size": 256}
        elif ratio <= 0.40:
            strategy = "in_graph_traversal"
            rationale = "Moderate selectivity (5%-40%): ACORN in-graph traversal avoids graph disconnection"
            params = {"ef_search": 32, "two_hop_bridge": True}
        else:
            strategy = "post_filter_oversample"
            rationale = "Low selectivity (> 40%): post-filtering with 2x-4x oversampling avoids index fragmentation"
            params = {"oversample_factor": 2.5}

        return {
            "selectivity_ratio": round(ratio, 4),
            "estimated_matching_vectors": est_matching,
            "selected_strategy": strategy,
            "rationale": rationale,
            "recommended_params": params,
        }
