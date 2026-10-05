"""
================================================================================
ALGORITHM BLUEPRINT: SEARCH-PARAMETER AUTOTUNING (ALGO-VEC-SRCH-110)
================================================================================

Search-parameter autotuning automatically sweeps parameter grids (e.g. ef_search,
nprobe, re-score multiplier) on sampled benchmark queries evaluated against exact
GEMM brute-force ground truth. It constructs the empirical Recall-vs-Latency Pareto
curve and selects the lowest-latency parameter configuration that satisfies a target
recall threshold (e.g. Recall@10 >= 0.95).
"""

from typing import Any, Dict, List, Optional


class VectorSearchAlgoSearchAutotune:
    """
    --- contract:
      id: ALGO-VEC-SRCH-110
      name: VectorSearchAlgoSearchAutotune
      category: vector
      complexity: O(|grid| * Q_sample * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        ground_truth_topk: list[list[int]]
        parameter_evaluations: list[dict[str, any]]
        target_recall: float
      output_schema:
        total_configurations: int
        target_recall: float
        optimal_configuration: dict[str, any]
        pareto_curve: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _compute_recall(ground_truth: List[List[int]], retrieved: List[List[int]]) -> float:
        if not ground_truth or not retrieved:
            return 0.0
        recalls = []
        for gt, ret in zip(ground_truth, retrieved):
            gt_set = set(gt)
            ret_set = set(ret)
            overlap = len(gt_set.intersection(ret_set))
            recalls.append(overlap / max(1, len(gt_set)))
        return sum(recalls) / len(recalls)

    @staticmethod
    def autotune_parameters(
        ground_truth_topk: List[List[int]],
        parameter_evaluations: List[Dict[str, Any]],
        target_recall: float = 0.95,
    ) -> Dict[str, Any]:
        if not parameter_evaluations:
            return {
                "total_configurations": 0,
                "target_recall": target_recall,
                "optimal_configuration": {},
                "pareto_curve": [],
            }

        evaluated: List[Dict[str, Any]] = []

        for item in parameter_evaluations:
            params = item.get("parameters", {})
            retrieved = item.get("retrieved_topk", [])
            latency_ms = item.get("latency_ms", 10.0)

            rec = VectorSearchAlgoSearchAutotune._compute_recall(ground_truth_topk, retrieved)

            evaluated.append({
                "parameters": params,
                "recall_at_k": round(rec, 4),
                "latency_ms": round(latency_ms, 2),
                "meets_target": rec >= target_recall,
            })

        qualifying = [e for e in evaluated if e["meets_target"]]
        if qualifying:
            optimal = min(qualifying, key=lambda x: x["latency_ms"])
        else:
            optimal = max(evaluated, key=lambda x: x["recall_at_k"])

        evaluated.sort(key=lambda x: x["latency_ms"])

        return {
            "total_configurations": len(evaluated),
            "target_recall": target_recall,
            "optimal_configuration": optimal,
            "pareto_curve": evaluated,
        }
