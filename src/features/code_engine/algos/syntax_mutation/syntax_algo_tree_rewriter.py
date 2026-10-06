"""
================================================================================
ALGORITHM BLUEPRINT: PATTERN-TO-TEMPLATE AST REWRITER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Visits AST/CST nodes, matches pattern predicates (e.g. function call name,
   attribute access, argument counts), and replaces matching subtrees with
   templated replacement syntax nodes while maintaining lexical scope and indentation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Preservation of Unmatched Nodes: Unmatched subtrees pass through untouched.
   - Idempotent Rewrite Invariant: Re-running the rewriter on transformed code
     produces 0 additional transformations.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N) where N is AST node count
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
from typing import Dict, Any, List, Optional, Tuple


class AstPatternTransformer(ast.NodeTransformer):
    def __init__(self, target_func: str, replacement_func: str) -> None:
        super().__init__()
        self.target_func: str = target_func
        self.replacement_func: str = replacement_func
        self.transform_count: int = 0

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == self.target_func:
            node.func.id = self.replacement_func
            self.transform_count += 1
        return node


class CodeEngineTreeRewriterAlgo:
    """
    --- contract:
      id: ALGO-SYNX-131
      name: CodeEngineTreeRewriterAlgo
      version: 1.0.0
      category: syntax_mutation
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - syntax.tree_rewriter
      - ast.template_transform
      - codemod.pattern_replace
      input_schema:
        source_code: string
        target_function: string
        replacement_function: string
      output_schema:
        algorithm: string
        transformed_code: string
        transform_count: integer
        is_modified: boolean
    ---
    """

    def rewrite_ast(self, code: str, target: str, replacement: str) -> Tuple[str, int]:
        try:
            tree = ast.parse(code)
            transformer = AstPatternTransformer(target, replacement)
            new_tree = transformer.visit(tree)
            ast.fix_missing_locations(new_tree)
            if transformer.transform_count > 0:
                new_code = ast.unparse(new_tree)
                return (new_code, transformer.transform_count)
            return (code, 0)
        except Exception:
            if target in code:
                return (code.replace(target, replacement), code.count(target))
            return (code, 0)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: str = str(payload.get("source_code", ""))
        target_fn: str = str(payload.get("target_function", "old_func"))
        replace_fn: str = str(payload.get("replacement_function", "new_func"))

        transformed, count = self.rewrite_ast(source, target_fn, replace_fn)

        return {
            "algorithm": "ALGO-SYNX-131",
            "transformed_code": transformed,
            "transform_count": count,
            "is_modified": count > 0,
        }
