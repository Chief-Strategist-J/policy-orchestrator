"""
================================================================================
ALGORITHM BLUEPRINT: CONCRETE SYNTAX TREE (CST & TRIVIA PRESERVING PARSER)
================================================================================

1. OVERVIEW:
   A Concrete Syntax Tree (CST / Lossless Parse Tree / Red-Green Tree) represents
   source code with 100% syntactic fidelity. In addition to grammatical nodes
   (expressions, statements), it preserves all whitespace, indentation, newlines,
   parentheses, and comments as 'trivia' attached to tokens. Modifying a CST node
   reproduces untouched surrounding code byte-for-byte, ensuring zero formatting drift.

2. CST COMPOSITION & NODES:
   - CstLeaf (Token): Exact text, leading trivia (spaces/comments before), trailing trivia.
   - CstInternalNode: Grammatical non-terminal grouping child nodes and leaves.
   - Round-trip Invariant: serialize(parse_cst(source)) == source.

3. COMPLEXITY ANALYSIS:
   - Construction Time: O(N) where N is source code length.
   - Serialization: O(N) linear string emit.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, List, Any, Optional, Union


class CstLeaf:
    def __init__(self, token_type: str, text: str, leading_trivia: str = "", trailing_trivia: str = "") -> None:
        self.token_type: str = token_type
        self.text: str = text
        self.leading_trivia: str = leading_trivia
        self.trailing_trivia: str = trailing_trivia

    def to_source(self) -> str:
        return self.leading_trivia + self.text + self.trailing_trivia


class CstNode:
    def __init__(self, node_type: str, children: Optional[List[Union["CstNode", CstLeaf]]] = None) -> None:
        self.node_type: str = node_type
        self.children: List[Union["CstNode", CstLeaf]] = children if children is not None else []

    def to_source(self) -> str:
        return "".join(child.to_source() for child in self.children)


class SearchEngineConcreteSyntaxTreeAlgo:
    """
    --- contract:
      id: ALGO-SRCH-78
      name: SearchEngineConcreteSyntaxTreeAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(N)
        space: O(CSTNodes)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - cst.matcher
      - syntax.lossless
      - code.refactor
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def parse_simple_cst(self, code: str) -> CstNode:
        root = CstNode("Module")
        lines = code.splitlines(keepends=True)

        for line in lines:
            line_node = CstNode("LineStatement")
            pattern = re.compile(r'(\s+)|(#[^\n]*)|([a-zA-Z_][a-zA-Z0-9_]*)|(\d+(\.\d+)?)|([\"\'][^\"\']*[\"\'])|([^\s\w#\"\']+)')
            current_leading = ""

            for match in pattern.finditer(line):
                ws, comment, ident, num, string_lit, op = match.groups()
                if ws:
                    current_leading += ws
                elif comment:
                    line_node.children.append(CstLeaf("Comment", comment, leading_trivia=current_leading))
                    current_leading = ""
                elif ident:
                    line_node.children.append(CstLeaf("Identifier", ident, leading_trivia=current_leading))
                    current_leading = ""
                elif num:
                    line_node.children.append(CstLeaf("Number", num, leading_trivia=current_leading))
                    current_leading = ""
                elif string_lit:
                    line_node.children.append(CstLeaf("String", string_lit, leading_trivia=current_leading))
                    current_leading = ""
                elif op:
                    line_node.children.append(CstLeaf("Operator", op, leading_trivia=current_leading))
                    current_leading = ""

            if current_leading:
                line_node.children.append(CstLeaf("Whitespace", "", leading_trivia=current_leading))

            root.children.append(line_node)

        return root

    def replace_identifier(self, root: CstNode, target_name: str, replacement: str) -> int:
        replacements = 0

        def _walk(node: Union[CstNode, CstLeaf]) -> None:
            nonlocal replacements
            if isinstance(node, CstLeaf):
                if node.token_type == "Identifier" and node.text == target_name:
                    node.text = replacement
                    replacements += 1
            elif isinstance(node, CstNode):
                for ch in node.children:
                    _walk(ch)

        _walk(root)
        return replacements

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = str(payload.get("code", ""))
        rename_from = payload.get("rename_from")
        rename_to = payload.get("rename_to")

        cst = self.parse_simple_cst(code)
        initial_roundtrip = cst.to_source()

        replacements = 0
        if rename_from and rename_to:
            replacements = self.replace_identifier(cst, str(rename_from), str(rename_to))

        final_source = cst.to_source()

        return {
            "algorithm": "ALGO-SRCH-78",
            "lossless_roundtrip_valid": (code == initial_roundtrip),
            "replacements_applied": replacements,
            "modified_source": final_source
        }
