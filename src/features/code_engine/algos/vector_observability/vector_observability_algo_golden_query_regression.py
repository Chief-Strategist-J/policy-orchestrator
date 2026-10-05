"""
================================================================================
ALGORITHM BLUEPRINT: GOLDEN QUERY SET REGRESSION TESTER (ALGO-VEC-OBS-164)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Executes deterministic regression gate testing on golden curated query sets
   comparing candidate retrieval configurations vs baseline metrics.

2. MATHEMATICAL FORMULATION:
   Delta_nDCG = candidate_nDCG - baseline_nDCG
   Regression occurs when Delta_Metric < -max_allowed_drop_tolerance.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoGoldenQueryRegression:
    """
    --- contract:
      id: ALGO-VEC-OBS-164
      name: VectorObservabilityAlgoGoldenQueryRegression
      category: observability
      complexity: O(Q * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        baseline_results: list[dict[str, Any]]
        candidate_results: list[dict[str, Any]]
        golden_expected_ids: list[dict[str, List[str]]]
        max_allowed_drop: float
      output_schema:
        is_promotion_approved: bool
        baseline_recall: float
        candidate_recall: float
        delta_recall: float
        regressed_queries: list[str]
        improved_queries: list[str]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        baseline_results: List[Dict[str, Any]],
        candidate_results: List[Dict[str, Any]],
        golden_expected_ids: List[Dict[str, List[str]]],
        max_allowed_drop: float = 0.02,
    ) -> Dict[str, Any]:
        if not baseline_results or not candidate_results or not golden_expected_ids:
            return {
                "is_promotion_approved": False,
                "baseline_recall": 0.0,
                "candidate_recall": 0.0,
                "delta_recall": 0.0,
                "regressed_queries": [],
                "improved_queries": [],
            }

        golden_map: Dict[str, set] = {}
        for item in golden_expected_ids:
            for q_id, exp_ids in item.items():
                golden_map[q_id] = set(exp_ids)

        base_recalls: Dict[str, float] = {}
        for item in baseline_results:
            q_id = item.get("query_id", "")
            ret = set(item.get("retrieved_ids", []))
            expected = golden_map.get(q_id, set())
            if expected:
                base_recalls[q_id] = len(ret.intersection(expected)) / float(len(expected))

        cand_recalls: Dict[str, float] = {}
        for item in candidate_results:
            q_id = item.get("query_id", "")
            ret = set(item.get("retrieved_ids", []))
            expected = golden_map.get(q_id, set())
            if expected:
                cand_recalls[q_id] = len(ret.intersection(expected)) / float(len(expected))

        common_queries = set(base_recalls.keys()).intersection(set(cand_recalls.keys()))
        if not common_queries:
            return {
                "is_promotion_approved": False,
                "baseline_recall": 0.0,
                "candidate_recall": 0.0,
                "delta_recall": 0.0,
                "regressed_queries": [],
                "improved_queries": [],
            }

        avg_base = sum(base_recalls[q] for q in common_queries) / float(len(common_queries))
        avg_cand = sum(cand_recalls[q] for q in common_queries) / float(len(common_queries))
        delta = avg_cand - avg_base

        regressed: List[str] = []
        improved: List[str] = []
        for q in sorted(common_queries):
            diff = cand_recalls[q] - base_recalls[q]
            if diff < -0.05:
                regressed.append(q)
            elif diff > 0.05:
                improved.append(q)

        approved = delta >= -abs(max_allowed_drop) and len(regressed) <= (len(common_queries) * 0.05)

        return {
            "is_promotion_approved": approved,
            "baseline_recall": round(avg_base, 4),
            "candidate_recall": round(avg_cand, 4),
            "delta_recall": round(delta, 4),
            "regressed_queries": regressed,
            "improved_queries": improved,
        }
