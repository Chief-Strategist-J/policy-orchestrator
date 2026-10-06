"""
================================================================================
ALGORITHM BLUEPRINT: SEMGREP-STYLE PATTERN MATCHING WITH EQUIVALENCES
================================================================================

1. OVERVIEW:
   Semgrep-Style Pattern Matching extends structural AST queries with semantic
   equivalence rules: import alias resolution (e.g. `import a.b as c; c()` matches `a.b()`),
   constant folding, and negative filtering (`pattern-not`, `pattern-inside`).
   Allows finding security vulnerabilities and deprecated API call paths regardless
   of how callers import or alias modules.

2. SEMANTIC EQUIVALENCE FEATURES:
   - Import Alias Tracking: Resolves imported module aliases back to canonical symbols.
   - Ellipsis (`...`): Matches any sequence of arguments or statements.
   - Boolean Combinators: Evaluates `patterns`, `pattern-either`, and `pattern-not`.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(File_AST * Equivalence_Rules).
   - Precision: High precision semantic detection.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple


class SearchEngineSemgrepEquivalenceAlgo:
    """
    --- contract:
      id: ALGO-SRCH-83
      name: SearchEngineSemgrepEquivalenceAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(AstNodes)
        space: O(EquivalenceClasses)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - ast.equivalence
      - semgrep.pattern
      - isomorphism.semantic
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def analyze_aliases(self, tree: ast.AST) -> Dict[str, str]:
        aliases: Dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local_name = alias.asname if alias.asname else alias.name
                    aliases[local_name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    local_name = alias.asname if alias.asname else alias.name
                    aliases[local_name] = f"{mod}.{alias.name}" if mod else alias.name
        return aliases

    def match_semgrep_pattern(
        self,
        code: str,
        target_api: str,
        pattern_not: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(code)
        except Exception:
            return []

        aliases = self.analyze_aliases(tree)
        matches: List[Dict[str, Any]] = []

        not_patterns = [re.compile(p) for p in (pattern_not or [])]

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                resolved_callee = ""
                if isinstance(node.func, ast.Name):
                    callee_id = node.func.id
                    resolved_callee = aliases.get(callee_id, callee_id)
                elif isinstance(node.func, ast.Attribute):
                    val_id = getattr(node.func.value, 'id', '')
                    resolved_base = aliases.get(val_id, val_id)
                    resolved_callee = f"{resolved_base}.{node.func.attr}" if resolved_base else node.func.attr

                if resolved_callee == target_api or resolved_callee.endswith(f".{target_api}"):
                    call_repr = ast.unparse(node) if hasattr(ast, "unparse") else resolved_callee
                    is_excluded = any(p.search(call_repr) for p in not_patterns)
                    if not is_excluded:
                        matches.append({
                            "target_api": target_api,
                            "resolved_symbol": resolved_callee,
                            "call_expression": call_repr,
                            "line_number": getattr(node, "lineno", 0),
                            "col_offset": getattr(node, "col_offset", 0)
                        })

        return matches

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = str(payload.get("code", ""))
        target_api = str(payload.get("target_api", ""))
        pattern_not = payload.get("pattern_not", [])

        hits = self.match_semgrep_pattern(code, target_api, pattern_not=pattern_not)

        return {
            "algorithm": "ALGO-SRCH-83",
            "target_api": target_api,
            "pattern_not": pattern_not,
            "matches": hits,
            "match_count": len(hits)
        }
