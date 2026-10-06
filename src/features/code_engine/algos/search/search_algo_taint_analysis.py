"""
================================================================================
ALGORITHM BLUEPRINT: TAINT ANALYSIS (SOURCE-TO-SINK PROPAGATION ENGINE)
================================================================================

1. OVERVIEW:
   Taint Analysis tracks whether untrusted input data (Sources: HTTP parameters,
   environment variables, external files) can propagate along dataflow edges into
   dangerous execution sinks (SQL execution, shell commands, deserialization)
   without passing through verified Sanitizer functions (escaping, typing, hashing).

2. TAINT PROPAGATION MODEL:
   - Sources: Variables originating untrusted data.
   - Sinks: Operations requiring sanitized inputs.
   - Sanitizers: Functions that remove taint (e.g. `int()`, `escape()`, `validate()`).
   - Taint State: Propagated across assignments `y = x` and function calls `foo(x)`.

3. COMPLEXITY ANALYSIS:
   - Time: O(Statements + Call_Edges).
   - Security Audit: Isolates unvalidated injection paths with 100% path traces.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Set, Tuple


class SearchEngineTaintAnalysisAlgo:
    """
    --- contract:
      id: ALGO-SRCH-94
      name: SearchEngineTaintAnalysisAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(DataflowEdges)
        space: O(TaintedPaths)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - security.taint_analysis
      - vulnerability.source_sink
      - dataflow.tracking
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def analyze_taint_flow(
        self,
        statements: List[Dict[str, Any]],
        sources: Set[str],
        sinks: Set[str],
        sanitizers: Set[str]
    ) -> Dict[str, Any]:
        tainted_vars: Set[str] = set(sources)
        taint_origins: Dict[str, str] = {s: s for s in sources}
        vulnerabilities: List[Dict[str, Any]] = []

        for stmt in statements:
            stmt_type = str(stmt.get("type", "assign")).lower()
            target = str(stmt.get("target", ""))
            inputs = [str(i) for i in stmt.get("inputs", [])]
            called_func = str(stmt.get("func", ""))

            if stmt_type == "assign":
                is_input_tainted = any(i in tainted_vars for i in inputs)
                if is_input_tainted:
                    if called_func in sanitizers:
                        tainted_vars.discard(target)
                    else:
                        tainted_vars.add(target)
                        origin = next(taint_origins[i] for i in inputs if i in tainted_vars)
                        taint_origins[target] = origin
                else:
                    tainted_vars.discard(target)

            elif stmt_type in ["sink", "call"]:
                if called_func in sinks:
                    for arg in inputs:
                        if arg in tainted_vars:
                            vulnerabilities.append({
                                "vulnerability": "UNSANITIZED_TAINT_SINK_FLOW",
                                "sink": called_func,
                                "tainted_argument": arg,
                                "origin_source": taint_origins.get(arg, "unknown_source"),
                                "line_number": stmt.get("lineno", 1)
                            })

        return {
            "total_statements_analyzed": len(statements),
            "vulnerabilities_detected": vulnerabilities,
            "vulnerability_count": len(vulnerabilities),
            "is_secure": len(vulnerabilities) == 0,
            "final_tainted_variables": sorted(list(tainted_vars))
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        statements = payload.get("statements", [])
        sources = set(payload.get("sources", ["user_input", "request_param"]))
        sinks = set(payload.get("sinks", ["sql_execute", "os_system", "eval"]))
        sanitizers = set(payload.get("sanitizers", ["sanitize_sql", "int", "escape"]))

        analysis = self.analyze_taint_flow(statements, sources, sinks, sanitizers)

        return {
            "algorithm": "ALGO-SRCH-97",
            "sources": sorted(list(sources)),
            "sinks": sorted(list(sinks)),
            "sanitizers": sorted(list(sanitizers)),
            "taint_report": analysis
        }
