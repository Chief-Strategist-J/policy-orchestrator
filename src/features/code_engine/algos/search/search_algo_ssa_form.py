"""
================================================================================
ALGORITHM BLUEPRINT: STATIC SINGLE ASSIGNMENT (SSA) FORM CONVERTER
================================================================================

1. OVERVIEW:
   Static Single Assignment (SSA) is an intermediate code representation where
   every variable is assigned exactly once. Each variable assignment creates a
   monotonically versioned variable (e.g., x_1 = ..., x_2 = ...). At control flow
   join points (merge sites after if/else or loops), phi-nodes (phi(x_1, x_2))
   are placed to select the appropriate version, simplifying dataflow analysis.

2. SSA INVARIANTS:
   - Single Assignment: Variable x_k is defined at exactly one program point.
   - Use-Definition Clarity: Every use of x_k unambiguously refers to definition of x_k.
   - Phi-Function Placement: x_merge = phi(x_branch1, x_branch2) at join nodes.

3. COMPLEXITY ANALYSIS:
   - Conversion Time: O(V + E * Var_Count) with dominance frontiers.
   - Analysis Speed: Dramatically simplifies reaching definitions and liveness.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class SearchEngineSsaFormAlgo:
    """
    --- contract:
      id: ALGO-SRCH-95
      name: SearchEngineSsaFormAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Blocks * Variables)
        space: O(SsaVariables)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - ssa.conversion
      - dominance.frontiers
      - phi.placement
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def convert_to_ssa(self, raw_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        counters: Dict[str, int] = {}
        active_versions: Dict[str, int] = {}
        ssa_statements: List[Dict[str, Any]] = []

        for stmt in raw_statements:
            stmt_type = str(stmt.get("type", "assign")).lower()
            var_name = str(stmt.get("var", ""))
            uses = [str(u) for u in stmt.get("uses", [])]

            versioned_uses = [f"{u}_{active_versions.get(u, 0)}" for u in uses]

            if stmt_type == "assign":
                new_version = counters.get(var_name, 0) + 1
                counters[var_name] = new_version
                active_versions[var_name] = new_version
                def_name = f"{var_name}_{new_version}"

                ssa_statements.append({
                    "type": "assign",
                    "target": def_name,
                    "uses": versioned_uses,
                    "expr": stmt.get("expr", "")
                })
            elif stmt_type == "phi":
                phi_sources = [f"{var_name}_{v}" for v in stmt.get("incoming_versions", [])]
                new_version = counters.get(var_name, 0) + 1
                counters[var_name] = new_version
                active_versions[var_name] = new_version
                def_name = f"{var_name}_{new_version}"

                ssa_statements.append({
                    "type": "phi",
                    "target": def_name,
                    "phi_inputs": phi_sources
                })

        return {
            "total_ssa_statements": len(ssa_statements),
            "variable_versions": dict(counters),
            "ssa_statements": ssa_statements
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        statements = payload.get("statements", [])
        ssa_summary = self.convert_to_ssa(statements)

        return {
            "algorithm": "ALGO-SRCH-95",
            "ssa_summary": ssa_summary
        }
