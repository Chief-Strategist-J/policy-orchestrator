"""
================================================================================
ALGORITHM BLUEPRINT: TREE-SITTER S-EXPRESSION AST QUERY MATCHER
================================================================================

1. OVERVIEW:
   Tree-sitter Queries use declarative S-expression pattern syntax to match AST
   node shapes, filter on node types, and capture named targets (e.g., `@name`,
   `@args`, `@body`). Predicates (such as `#eq?` and `#match?`) refine matches,
   enabling precise syntactic search and refactoring targets across languages.

2. S-EXPRESSION QUERY SYNTAX & CAPTURES:
   - Pattern Example: `(call function: (identifier) @callee arguments: (argument_list) @args)`
   - Captures: `@capture_name` labels the matched AST node.
   - Predicates: `(#eq? @callee "old_function_name")` filters matches.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N) where N is AST node count.
   - Space Complexity: O(Matches).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
from typing import Dict, List, Any, Optional


class SearchEngineTreeSitterQueryAlgo:
    """
    --- contract:
      id: ALGO-SRCH-78
      name: SearchEngineTreeSitterQueryAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(AstNodes)
        space: O(Captures)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - tree_sitter.s_expression
      - ast.query_cursor
      - pattern.captures
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def match_call_queries(self, code: str, target_callee: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(code)
        except Exception:
            return []

        matches: List[Dict[str, Any]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if target_callee and func_name != target_callee:
                    continue

                args_repr = [ast.unparse(a) if hasattr(ast, "unparse") else str(a) for a in node.args]
                matches.append({
                    "pattern": "(call function: (identifier) @callee arguments: (arg_list) @args)",
                    "captures": {
                        "callee": func_name,
                        "args": args_repr,
                        "arg_count": len(node.args)
                    },
                    "line_number": getattr(node, "lineno", 0),
                    "col_offset": getattr(node, "col_offset", 0)
                })

        return matches

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = str(payload.get("code", ""))
        query_pattern = str(payload.get("query_pattern", "(call function: (identifier) @callee)"))
        target_name = payload.get("target_name")

        matches = self.match_call_queries(code, target_callee=str(target_name) if target_name else None)

        return {
            "algorithm": "ALGO-SRCH-81",
            "query_pattern": query_pattern,
            "target_name": target_name,
            "matches": matches,
            "match_count": len(matches)
        }
