r"""
================================================================================
ALGORITHM BLUEPRINT: GRAPH FAIRNESS, EQUALIZED ODDS & DYADIC BIAS EVALUATOR
================================================================================

1. OVERVIEW & OBJECTIVE:
   Algorithmic bias and fairness auditing engine for Graph Neural Networks and
   Knowledge Graph representations (FairGNN / NIFTY / EDITS protocols). Evaluates
   Statistical Demographic Parity ($\Delta_{DP}$), Equal Opportunity ($\Delta_{EO}$),
   Equalized Odds, and Dyadic Intra/Inter-group Link Prediction Parity across
   sensitive demographic sub-populations.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Metric Boundedness: All disparity metrics strictly bounded in $[0, 1]$ where 0 is perfect parity.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|Nodes| + |Edges|) for node group partitioning and confusion matrices.
   - Space Complexity: O(|Groups| * |Classes|) for demographic contingency tables.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoGraphFairnessEvaluator:
    """
    --- contract:
      id: ALGO-KG-150
      name: KgAlgoGraphFairnessEvaluator
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Nodes + Edges)
        space: O(Groups)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graph_fairness
      - demographic_parity
      - equal_opportunity
      - equalized_odds
      - dyadic_fairness
      input_schema:
        predictions: object
        sensitive_attribute: object
        ground_truth: optional object
      output_schema:
        algorithm: string
        demographic_parity_difference: number
        equal_opportunity_difference: optional number
        equalized_odds_gap: optional number
        group_positive_rates: object
    ---
    """

    def evaluate_demographic_parity(
        self,
        predictions: Dict[str, int],
        sensitive_attrs: Dict[str, str],
    ) -> Dict[str, Any]:
        group_pos: Dict[str, int] = defaultdict(int)
        group_total: Dict[str, int] = defaultdict(int)

        for n, pred in predictions.items():
            g = sensitive_attrs.get(n, "unknown")
            group_total[g] += 1
            if pred == 1:
                group_pos[g] += 1

        rates = {g: group_pos[g] / max(1, group_total[g]) for g in group_total}
        diff = (max(rates.values()) - min(rates.values())) if len(rates) > 1 else 0.0

        return {
            "algorithm": "ALGO-KG-150",
            "demographic_parity_difference": round(diff, 5),
            "group_positive_rates": {k: round(v, 5) for k, v in rates.items()},
            "group_sample_counts": dict(group_total),
        }

    def evaluate_comprehensive_fairness(
        self,
        predictions: Dict[str, int],
        ground_truth: Dict[str, int],
        sensitive_attrs: Dict[str, str],
        edges: Optional[List[Tuple[str, str]]] = None,
    ) -> Dict[str, Any]:
        dp_res = self.evaluate_demographic_parity(predictions, sensitive_attrs)

        group_tpr: Dict[str, float] = {}
        group_fpr: Dict[str, float] = {}

        group_pos_truth: Dict[str, int] = defaultdict(int)
        group_tp: Dict[str, int] = defaultdict(int)
        group_neg_truth: Dict[str, int] = defaultdict(int)
        group_fp: Dict[str, int] = defaultdict(int)

        for n, y_true in ground_truth.items():
            y_pred = predictions.get(n, 0)
            g = sensitive_attrs.get(n, "unknown")

            if y_true == 1:
                group_pos_truth[g] += 1
                if y_pred == 1:
                    group_tp[g] += 1
            else:
                group_neg_truth[g] += 1
                if y_pred == 1:
                    group_fp[g] += 1

        groups = set(sensitive_attrs.values())
        for g in groups:
            group_tpr[g] = (group_tp[g] / max(1, group_pos_truth[g])) if group_pos_truth[g] > 0 else 0.0
            group_fpr[g] = (group_fp[g] / max(1, group_neg_truth[g])) if group_neg_truth[g] > 0 else 0.0

        valid_tprs = [v for k, v in group_tpr.items() if group_pos_truth[k] > 0]
        valid_fprs = [v for k, v in group_fpr.items() if group_neg_truth[k] > 0]

        delta_eo = (max(valid_tprs) - min(valid_tprs)) if len(valid_tprs) > 1 else 0.0
        delta_fpr = (max(valid_fprs) - min(valid_fprs)) if len(valid_fprs) > 1 else 0.0
        equalized_odds_gap = (delta_eo + delta_fpr) / 2.0

        dyadic_parity = None
        if edges:
            intra_group_edges = 0
            inter_group_edges = 0
            for u, v in edges:
                g_u = sensitive_attrs.get(u)
                g_v = sensitive_attrs.get(v)
                if g_u and g_v:
                    if g_u == g_v:
                        intra_group_edges += 1
                    else:
                        inter_group_edges += 1
            total_edges = max(1, intra_group_edges + inter_group_edges)
            dyadic_parity = {
                "intra_group_ratio": round(intra_group_edges / total_edges, 4),
                "inter_group_ratio": round(inter_group_edges / total_edges, 4),
                "homophily_disparity": round(abs(intra_group_edges - inter_group_edges) / total_edges, 4),
            }

        return {
            "algorithm": "ALGO-KG-150",
            "demographic_parity_difference": dp_res["demographic_parity_difference"],
            "equal_opportunity_difference": round(delta_eo, 5),
            "equalized_odds_gap": round(equalized_odds_gap, 5),
            "group_tpr": {k: round(v, 4) for k, v in group_tpr.items()},
            "group_fpr": {k: round(v, 4) for k, v in group_fpr.items()},
            "dyadic_fairness": dyadic_parity,
        }
