"""
Module: search_engine_algo_tree_sitter_ast
Architecture: Search Engine Algorithm 17 — Multi-Language AST and Syntax Node Extractor

Blueprint:
- Parses Python source files into Python AST nodes.
- Provides a universal syntax-tree node representation with node_type, span, children, and attributes.
- Implements a resilient regex/token-based fallback AST builder for non-Python languages (JS/TS, Go, Rust).
- Enables semantic code search, node filtering, and symbol extraction across AST trees.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AstNode:
    node_type: str
    name: Optional[str]
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List[AstNode] = field(default_factory=list)


class AstExtractor:
    """
    ---
    contract:
      algo_id: ALGO-OBS-17
      name: AstExtractor
      version: 1.0.0
      category: observability
      capability_tags:
      - parser.ast
      - ast.tree_extractor
      - cst.visitor
      inputs:
        type: object
        required:
        - source_code
        properties:
          source_code:
            type: string
          filename:
            type: string
            default: <source>
      outputs:
        type: array
        items:
          type: object
          required:
          - node_type
          - name
          - line_start
          - line_end
          properties:
            node_type:
              type: string
            name:
              type: string
            line_start:
              type: integer
            line_end:
              type: integer
            docstring:
              type: string
              nullable: true
            decorators:
              type: array
              items:
                type: string
      parameters:
        type: object
        properties: {}
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|SourceCode|)
        space: O(ASTNodes)
      preconditions:
      - len(input.source_code) >= 0
      postconditions:
      - all(n.line_start <= n.line_end for n in output)
      compatible_adapters:
      - ADAPTER-AST-TO-SCOPE-TREE
      - ADAPTER-AST-TO-OUTLINE
    ---
    """
    def parse_python(self, code: str) -> AstNode:
        try:
            tree = ast.parse(code)
            return self._convert_py_ast(tree, code)
        except SyntaxError as e:
            return AstNode(
                node_type="SyntaxError",
                name=None,
                start_line=e.lineno or 1,
                end_line=e.lineno or 1,
                start_col=e.offset or 0,
                end_col=e.offset or 0,
                attributes={"error": str(e)},
            )

    def _convert_py_ast(self, node: ast.AST, code: str) -> AstNode:
        node_type = type(node).__name__
        name = getattr(node, "name", None) or getattr(node, "id", None)
        start_line = getattr(node, "lineno", 1)
        end_line = getattr(node, "end_lineno", start_line)
        start_col = getattr(node, "col_offset", 0)
        end_col = getattr(node, "end_col_offset", start_col)

        attributes: Dict[str, Any] = {}
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            attributes["args"] = [arg.arg for arg in node.args.args]
            attributes["is_async"] = isinstance(node, ast.AsyncFunctionDef)
        elif isinstance(node, ast.ClassDef):
            attributes["bases"] = [ast.unparse(b) for b in node.bases] if hasattr(ast, "unparse") else []
        elif isinstance(node, ast.Import):
            attributes["names"] = [n.name for n in node.names]
        elif isinstance(node, ast.ImportFrom):
            attributes["module"] = node.module
            attributes["names"] = [n.name for n in node.names]

        children: List[AstNode] = []
        for child in ast.iter_child_nodes(node):
            children.append(self._convert_py_ast(child, code))

        return AstNode(
            node_type=node_type,
            name=name,
            start_line=start_line,
            end_line=end_line,
            start_col=start_col,
            end_col=end_col,
            attributes=attributes,
            children=children,
        )

    def parse_generic(self, code: str, language: str = "generic") -> AstNode:
        root = AstNode(
            node_type="Root",
            name=language,
            start_line=1,
            end_line=len(code.splitlines()) or 1,
            start_col=0,
            end_col=0,
        )

        patterns = [
            (r"(?:function\s+([a-zA-Z0-9_$]+)|(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)", "FunctionDeclaration"),
            (r"(?:class|interface|struct|type)\s+([a-zA-Z0-9_$]+)", "TypeDeclaration"),
            (r"(?:import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]|const\s+.*?\s*=\s*require\(['\"]([^'\"]+)['\"]\))", "ImportDeclaration"),
            (r"def\s+([a-zA-Z0-9_]+)\s*\(", "FunctionDeclaration"),
            (r"fn\s+([a-zA-Z0-9_]+)\s*\(", "FunctionDeclaration"),
            (r"func\s+([a-zA-Z0-9_]+)\s*\(", "FunctionDeclaration"),
        ]

        lines = code.splitlines()
        for idx, line in enumerate(lines, start=1):
            for regex, kind in patterns:
                for match in re.finditer(regex, line):
                    symbol = next((g for g in match.groups() if g is not None), match.group(0))
                    root.children.append(
                        AstNode(
                            node_type=kind,
                            name=symbol,
                            start_line=idx,
                            end_line=idx,
                            start_col=match.start(),
                            end_col=match.end(),
                        )
                    )

        return root

    def find_nodes(self, root: AstNode, node_type: str) -> List[AstNode]:
        results: List[AstNode] = []
        if root.node_type == node_type:
            results.append(root)
        for child in root.children:
            results.extend(self.find_nodes(child, node_type))
        return results
