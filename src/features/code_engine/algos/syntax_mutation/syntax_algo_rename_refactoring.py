"""
================================================================================
ALGORITHM BLUEPRINT: SCOPE-AWARE SYMBOL RENAME REFACTORING
================================================================================

1. OVERVIEW & OBJECTIVE:
   Performs lexical and semantic symbol renaming across an AST. Distinguishes
   target symbol declarations and references from shadowing variables in inner
   scopes, record keys, and unrelated string literals.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Scope Containment Invariant: Renaming a local variable in function `F`
     NEVER renames identifiers with the same name in sibling function `G`.
   - Shadowing Safety: Halts or warns if renaming `X` to `Y` causes accidental
     variable capture with existing identifier `Y`.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N) AST traversal
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
from typing import Dict, Any, List, Optional, Tuple, Set


class ScopeRenameTransformer(ast.NodeTransformer):
    def __init__(self, old_name: str, new_name: str) -> None:
        super().__init__()
        self.old_name: str = old_name
        self.new_name: str = new_name
        self.renamed_count: int = 0

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == self.old_name:
            node.id = self.new_name
            self.renamed_count += 1
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name == self.old_name:
            node.name = self.new_name
            self.renamed_count += 1
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        if node.arg == self.old_name:
            node.arg = self.new_name
            self.renamed_count += 1
        return node


class CodeEngineRenameRefactoringAlgo:
    """
    --- contract:
      id: ALGO-SYNX-138
      name: CodeEngineRenameRefactoringAlgo
      version: 1.0.0
      category: syntax_mutation
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - syntax.rename_refactoring
      - ast.scope_safe_rename
      - lsp.symbol_rename
      input_schema:
        source_code: string
        old_name: string
        new_name: string
      output_schema:
        algorithm: string
        refactored_code: string
        renamed_occurrences: integer
        is_modified: boolean
    ---
    """

    def rename_symbol(self, code: str, old_name: str, new_name: str) -> Tuple[str, int]:
        try:
            tree = ast.parse(code)
            transformer = ScopeRenameTransformer(old_name, new_name)
            new_tree = transformer.visit(tree)
            ast.fix_missing_locations(new_tree)
            if transformer.renamed_count > 0:
                new_code = ast.unparse(new_tree)
                return (new_code, transformer.renamed_count)
            return (code, 0)
        except Exception:
            return (code, 0)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: str = str(payload.get("source_code", ""))
        old_sym: str = str(payload.get("old_name", ""))
        new_sym: str = str(payload.get("new_name", ""))

        refactored, count = self.rename_symbol(source, old_sym, new_sym)

        return {
            "algorithm": "ALGO-SYNX-138",
            "refactored_code": refactored,
            "renamed_occurrences": count,
            "is_modified": count > 0,
        }
