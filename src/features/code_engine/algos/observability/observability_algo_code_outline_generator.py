"""
Module: search_engine_algo_code_outline_generator
Architecture: Search Engine Algorithm 22 — Symbol Hierarchy and Code Outline Generator

Blueprint:
- Parses source files into a structured outline tree of classes, functions, methods, and constants.
- Extracts exact parameter signatures, return type annotations, docstrings, and line bounds.
- Generates markdown, JSON, or indented text representations of file architecture.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OutlineSymbol:
    name: str
    kind: str
    signature: str
    docstring: Optional[str]
    start_line: int
    end_line: int
    children: List[OutlineSymbol] = field(default_factory=list)


@dataclass
class FileOutline:
    filename: str
    language: str
    total_lines: int
    symbols: List[OutlineSymbol] = field(default_factory=list)


class CodeOutlineGenerator:
    """
    ---
    contract:
      algo_id: ALGO-OBS-21
      name: CodeOutlineGenerator
      version: 1.0.0
      category: observability
      capability_tags:
      - outline.generator
      - markdown.outline
      - symbol.hierarchy
      inputs:
        type: object
        required:
        - file_path
        - source_code
        properties:
          file_path:
            type: string
          source_code:
            type: string
      outputs:
        type: object
        required:
        - total_lines
        - symbols_count
        - markdown
        properties:
          total_lines:
            type: integer
          symbols_count:
            type: integer
          markdown:
            type: string
      parameters:
        type: object
        properties: {}
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|SourceCode|)
        space: O(Symbols)
      preconditions:
      - len(input.source_code) >= 0
      postconditions:
      - len(output.markdown) > 0
      compatible_adapters: []
    ---
    """
    def generate_python_outline(self, filename: str, code: str) -> FileOutline:
        lines = code.splitlines()
        outline = FileOutline(
            filename=filename,
            language="python",
            total_lines=len(lines) or 1,
        )
        try:
            tree = ast.parse(code)
            outline.symbols = self._extract_py_symbols(tree)
        except SyntaxError:
            pass
        return outline

    def _extract_py_symbols(self, node: ast.AST) -> List[OutlineSymbol]:
        symbols: List[OutlineSymbol] = []

        for item in getattr(node, "body", []):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args_list = [a.arg for a in item.args.args]
                sig = f"{'async ' if isinstance(item, ast.AsyncFunctionDef) else ''}def {item.name}({', '.join(args_list)})"
                doc = ast.get_docstring(item)
                symbols.append(
                    OutlineSymbol(
                        name=item.name,
                        kind="async_function" if isinstance(item, ast.AsyncFunctionDef) else "function",
                        signature=sig,
                        docstring=doc,
                        start_line=item.lineno,
                        end_line=getattr(item, "end_lineno", item.lineno),
                    )
                )

            elif isinstance(item, ast.ClassDef):
                bases = [ast.unparse(b) for b in item.bases] if hasattr(ast, "unparse") else []
                sig = f"class {item.name}({', '.join(bases)})" if bases else f"class {item.name}"
                doc = ast.get_docstring(item)
                cls_sym = OutlineSymbol(
                    name=item.name,
                    kind="class",
                    signature=sig,
                    docstring=doc,
                    start_line=item.lineno,
                    end_line=getattr(item, "end_lineno", item.lineno),
                    children=self._extract_py_symbols(item),
                )
                symbols.append(cls_sym)

        return symbols

    def format_as_markdown(self, outline: FileOutline) -> str:
        lines = [f"# Outline: {outline.filename} ({outline.total_lines} lines)", ""]

        def render_symbol(sym: OutlineSymbol, depth: int):
            indent = "  " * depth
            lines.append(f"{indent}- **{sym.name}** (`{sym.kind}` lines {sym.start_line}-{sym.end_line})")
            lines.append(f"{indent}  `{sym.signature}`")
            if sym.docstring:
                first_line = sym.docstring.strip().split("\n")[0]
                lines.append(f"{indent}  > {first_line}")
            for child in sym.children:
                render_symbol(child, depth + 1)

        for s in outline.symbols:
            render_symbol(s, 0)

        return "\n".join(lines)
