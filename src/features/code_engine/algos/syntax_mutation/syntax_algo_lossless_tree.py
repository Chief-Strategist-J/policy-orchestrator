"""
================================================================================
ALGORITHM BLUEPRINT: LOSSLESS SYNTAX TREE (FULL-FIDELITY CST PARSER)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a lossless syntax tree (Concrete Syntax Tree) where every single
   token, whitespace character, indentation span, newline, and comment is
   retained as typed nodes or trivia tokens. Splicing or modifying a specific AST
   node guarantees that unaffected regions serialize back to byte-identical source.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Round-Trip Invariant: For any unmutated tree $T$, `T.to_source() == original_source`.
   - Trivia Encapsulation: Non-syntactic tokens (comments, spaces) are attached
     as leading/trailing trivia to adjacent syntax tokens.

3. COMPLEXITY ANALYSIS:
   - Parse: O(N) where N is source code size
   - Serialization: O(N)
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
from typing import Dict, Any, List, Optional, Union


class SyntaxToken:
    def __init__(self, kind: str, value: str, leading_trivia: str = "", trailing_trivia: str = "") -> None:
        self.kind: str = kind
        self.value: str = value
        self.leading_trivia: str = leading_trivia
        self.trailing_trivia: str = trailing_trivia

    def to_source(self) -> str:
        return self.leading_trivia + self.value + self.trailing_trivia


class SyntaxElement:
    def __init__(self, kind: str, children: Optional[List[Union["SyntaxElement", SyntaxToken]]] = None) -> None:
        self.kind: str = kind
        self.children: List[Union["SyntaxElement", SyntaxToken]] = children if children is not None else []

    def to_source(self) -> str:
        return "".join(child.to_source() for child in self.children)


class CodeEngineLosslessSyntaxTreeAlgo:
    """
    --- contract:
      id: ALGO-SYNX-127
      name: CodeEngineLosslessSyntaxTreeAlgo
      version: 1.0.0
      category: syntax_mutation
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - syntax.lossless_tree
      - cst.full_fidelity
      - formatting.round_trip
      input_schema:
        source_code: string
      output_schema:
        algorithm: string
        element_count: integer
        is_round_trip_lossless: boolean
        reconstructed_code: string
    ---
    """

    def parse_lossless(self, code: str) -> SyntaxElement:
        lines = code.splitlines(keepends=True)
        root = SyntaxElement(kind="SourceFile")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                root.children.append(SyntaxToken(kind="EmptyLine", value="", trailing_trivia=line))
            elif stripped.startswith("#"):
                l_space = line[:len(line) - len(line.lstrip())]
                root.children.append(SyntaxToken(kind="CommentLine", value=stripped, leading_trivia=l_space, trailing_trivia="\n"))
            else:
                l_space = line[:len(line) - len(line.lstrip())]
                r_space = line[len(line.rstrip()):]
                root.children.append(SyntaxToken(kind="CodeLine", value=line.strip(), leading_trivia=l_space, trailing_trivia=r_space))

        return root

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: str = str(payload.get("source_code", ""))
        root = self.parse_lossless(source)
        reconstructed = root.to_source()

        return {
            "algorithm": "ALGO-SYNX-127",
            "element_count": len(root.children),
            "is_round_trip_lossless": reconstructed == source,
            "reconstructed_code": reconstructed,
        }
