"""
================================================================================
ALGORITHM BLUEPRINT: ABSTRACT SYNTAX TREE (AST & SEMANTIC NODE ANALYZER)
================================================================================

1. OVERVIEW:
   An Abstract Syntax Tree (AST) captures the hierarchical semantic structure
   of source code (declarations, expressions, control flow, functions, classes)
   while omitting surface syntactic details like whitespace and comments.
   Enables structural query matching, function signature inspections, and semantic
   symbol extraction.

2. AST NODE TYPES & SCHEMAS:
   - FunctionDef: Name, parameters, return type annotation, body statements.
   - ClassDef: Class name, base classes, method members.
   - Call: Callee function/method name, positional arguments, keyword arguments.
   - Assign: Target identifiers, value expression.
   - If / For / While: Control flow branch predicates and statement bodies.

3. COMPLEXITY ANALYSIS:
   - Parsing: O(N) where N is source code length.
   - AST Traversal: O(M) where M is total AST node count.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments in function bodies.
================================================================================
"""

import ast
from typing import Dict, List, Any, Optional


class SearchEngineAbstractSyntaxTreeAlgo:
    """
    Implements AST parsing, semantic node extraction, and structural inspection.
    """

    def parse_ast_summary(self, code: str) -> Dict[str, Any]:
        """
        Parses code into AST and extracts summary of functions, classes, and call expressions.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "parse_error": str(e),
                "is_valid_syntax": False,
                "functions": [],
                "classes": [],
                "calls": []
            }

        functions: List[Dict[str, Any]] = []
        classes: List[Dict[str, Any]] = []
        calls: List[Dict[str, Any]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                params = [arg.arg for arg in node.args.args]
                functions.append({
                    "name": node.name,
                    "line_number": getattr(node, "lineno", 0),
                    "parameters": params,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) if hasattr(ast, "unparse") else str(b) for b in node.bases]
                classes.append({
                    "name": node.name,
                    "line_number": getattr(node, "lineno", 0),
                    "bases": bases,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.Call):
                func_name = "unknown"
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = f"{getattr(node.func.value, 'id', 'obj')}.{node.func.attr}"
                calls.append({
                    "callee": func_name,
                    "line_number": getattr(node, "lineno", 0),
                    "arg_count": len(node.args)
                })

        return {
            "is_valid_syntax": True,
            "functions": functions,
            "classes": classes,
            "calls": calls,
            "function_count": len(functions),
            "class_count": len(classes),
            "call_count": len(calls)
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes AST structural analysis over code payload.
        """
        code = str(payload.get("code", ""))
        summary = self.parse_ast_summary(code)

        return {
            "algorithm": "ALGO-SRCH-79",
            "ast_summary": summary
        }
