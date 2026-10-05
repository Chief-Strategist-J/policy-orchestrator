"""
================================================================================
ALGORITHM BLUEPRINT: LLM-AS-JUDGE RELEVANCE EVALUATOR (ALGO-VEC-OBS-163)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Deterministic scoring and calibration harness for LLM-judged query-passage relevance,
   computing calibrated relevance distributions, agreement metrics (Cohen's Kappa),
   and explanation extraction.

2. MATHEMATICAL FORMULATION:
   Cohen's Kappa: kappa = (P_o - P_e) / (1 - P_e)
   Calibrated Score = sum(grade_i * confidence_i) / sum(confidence_i)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoLlmAsJudge:
    """
    --- contract:
      id: ALGO-VEC-OBS-163
      name: VectorObservabilityAlgoLlmAsJudge
      category: observability
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        judgments: list[dict[str, Any]]
        human_labels: Optional[list[int]]
        min_passing_score: float
      output_schema:
        mean_relevance_score: float
        passing_rate: float
        cohens_kappa: Optional[float]
        scored_evaluations: list[dict[str, Any]]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        judgments: List[Dict[str, Any]],
        human_labels: Optional[List[int]] = None,
        min_passing_score: float = 2.0,
    ) -> Dict[str, Any]:
        if not judgments:
            return {
                "mean_relevance_score": 0.0,
                "passing_rate": 0.0,
                "cohens_kappa": None,
                "scored_evaluations": [],
            }

        scores: List[float] = []
        evaluations: List[Dict[str, Any]] = []
        llm_binary: List[int] = []

        for j_idx, item in enumerate(judgments):
            raw_grade = float(item.get("grade", 0.0))
            reasoning = str(item.get("reasoning", ""))
            query_id = str(item.get("query_id", f"q-{j_idx}"))
            passage_id = str(item.get("passage_id", f"p-{j_idx}"))

            scores.append(raw_grade)
            is_pass = raw_grade >= min_passing_score
            llm_binary.append(1 if is_pass else 0)

            evaluations.append({
                "query_id": query_id,
                "passage_id": passage_id,
                "grade": raw_grade,
                "is_relevant": is_pass,
                "reasoning": reasoning,
            })

        mean_score = sum(scores) / float(len(scores)) if scores else 0.0
        pass_rate = sum(llm_binary) / float(len(llm_binary)) if llm_binary else 0.0

        kappa: Optional[float] = None
        if human_labels and len(human_labels) == len(llm_binary) and len(human_labels) > 0:
            h_binary = [1 if int(h) >= int(min_passing_score) else 0 for h in human_labels]
            n = float(len(h_binary))
            po = sum(1 for a, b in zip(llm_binary, h_binary) if a == b) / n

            p_llm_1 = sum(llm_binary) / n
            p_llm_0 = 1.0 - p_llm_1
            p_h_1 = sum(h_binary) / n
            p_h_0 = 1.0 - p_h_1
            pe = (p_llm_1 * p_h_1) + (p_llm_0 * p_h_0)

            if pe < 1.0:
                kappa = (po - pe) / (1.0 - pe)
            else:
                kappa = 1.0

        return {
            "mean_relevance_score": round(mean_score, 4),
            "passing_rate": round(pass_rate, 4),
            "cohens_kappa": round(kappa, 4) if kappa is not None else None,
            "scored_evaluations": evaluations,
        }
