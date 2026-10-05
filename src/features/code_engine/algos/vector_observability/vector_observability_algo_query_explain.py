"""
================================================================================
ALGORITHM BLUEPRINT: QUERY EXPLAIN PER-STAGE EXECUTION BREAKDOWN (ALGO-VEC-OBS-191)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Generates a structured per-stage execution trace report for a query: inputs in,
   candidates pruned, distance operations evaluated, and rank mutations at each stage
   (Routing -> Filter Plan -> ANN Lookup -> Reranking -> ACL Cut).

2. MATHEMATICAL FORMULATION:
   Stage Selectivity = OutputCandidates / InputCandidates
   CumulativePruningRatio = 1.0 - (FinalCandidates / InitialCandidates)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoQueryExplain:
    """
    --- contract:
      id: ALGO-VEC-OBS-191
      name: VectorObservabilityAlgoQueryExplain
      category: observability
      complexity: O(S)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query_id: str
        stages: list[dict[str, Any]]
        target_document_id: Optional[str]
      output_schema:
        query_id: str
        total_latency_ms: float
        total_distance_evaluations: int
        cumulative_pruning_ratio: float
        stage_breakdown: list[dict[str, Any]]
        target_document_trace: Optional[dict[str, Any]]
    ---
    """

    @classmethod
    def explain(
        cls,
        query_id: str,
        stages: List[Dict[str, Any]],
        target_document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not stages:
            return {
                "query_id": query_id,
                "total_latency_ms": 0.0,
                "total_distance_evaluations": 0,
                "cumulative_pruning_ratio": 0.0,
                "stage_breakdown": [],
                "target_document_trace": None,
            }

        total_lat = 0.0
        total_dist_ops = 0
        breakdown = []
        initial_count = int(stages[0].get("input_count", 0))
        final_count = int(stages[-1].get("output_count", 0))

        doc_trace: Optional[Dict[str, Any]] = None
        if target_document_id:
            doc_trace = {"target_id": target_document_id, "survival_stages": [], "dropped_at_stage": None}

        for stg in stages:
            s_name = stg.get("stage_name", "stage")
            inp = int(stg.get("input_count", 0))
            out = int(stg.get("output_count", 0))
            lat = float(stg.get("duration_ms", 0.0))
            d_ops = int(stg.get("distance_evaluations", 0))
            cand_ids = stg.get("candidate_ids", [])

            total_lat += lat
            total_dist_ops += d_ops
            sel = out / float(inp) if inp > 0 else 0.0

            breakdown.append({
                "stage_name": s_name,
                "input_count": inp,
                "output_count": out,
                "selectivity": round(sel, 4),
                "duration_ms": round(lat, 2),
                "distance_evaluations": d_ops,
            })

            if target_document_id and doc_trace is not None:
                if target_document_id in cand_ids:
                    doc_trace["survival_stages"].append(s_name)
                elif doc_trace["dropped_at_stage"] is None:
                    doc_trace["dropped_at_stage"] = s_name

        pruning_ratio = 1.0 - (final_count / float(initial_count)) if initial_count > 0 else 0.0

        return {
            "query_id": query_id,
            "total_latency_ms": round(total_lat, 2),
            "total_distance_evaluations": total_dist_ops,
            "cumulative_pruning_ratio": round(max(0.0, pruning_ratio), 4),
            "stage_breakdown": breakdown,
            "target_document_trace": doc_trace,
        }
