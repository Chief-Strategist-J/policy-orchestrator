"""
GRAPH QUERY EXECUTION PLAN EXPLAINER AND BOTTLENECK FINDER
Implementation Module for KgAlgoQueryExplainer (ALGO-KG-193).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoQueryExplainer:
    """
    --- contract:
      id: ALGO-KG-193
      name: KgAlgoQueryExplainer
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Plan_Nodes)
        space: O(Bottlenecks)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - query_explain
      - execution_plan
      - bottleneck_detector
      input_schema:
        execution_plan: array
      output_schema:
        algorithm: string
        bottlenecks: array
        optimization_hints: array
    ---
    """
    def explain_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        bottlenecks: List[Dict[str, Any]] = []
        hints: List[str] = []
        for step in plan:
            op = step.get("operator", "")
            rows = step.get("estimated_rows", 0)
            if op == "AllNodesScan":
                bottlenecks.append({"operator": op, "severity": "HIGH", "detail": "Full graph scan detected"})
                hints.append("Add index on scanned labels/properties")
            elif op == "CartesianProduct":
                bottlenecks.append({"operator": op, "severity": "CRITICAL", "detail": "Cartesian join product detected"})
                hints.append("Ensure query patterns share joined variables")
            elif rows > 10000 and "Scan" in op:
                bottlenecks.append({"operator": op, "severity": "MEDIUM", "detail": f"Large row scan: {rows}"})
        return {
            "algorithm": "ALGO-KG-193",
            "bottlenecks": bottlenecks,
            "optimization_hints": hints,
        }
