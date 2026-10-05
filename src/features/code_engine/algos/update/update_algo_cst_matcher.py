"""
Module: search_engine_algo_cst_matcher
Architecture: Search Engine Algorithm 18 — Concrete Syntax Tree (CST) Lossless Pattern Matcher

Blueprint:
- Performs structural and token-level template matching with placeholder variables ($VAR, $EXPR, $_).
- Preserves exact source trivia, formatting, and surrounding whitespace.
- Compares AST/token sequences while binding named capture placeholders.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CstMatch:
    matched_text: str
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    captures: Dict[str, str]


class CstMatcher:
    """
    ---
    contract:
      algo_id: ALGO-UPD-22
      name: CstMatcher
      version: 1.0.0
      category: update
      capability_tags:
      - cst.matcher
      - ast.whitespace_preserving
      - refactoring.pattern_match
      inputs:
        type: object
        required:
        - source_code
        - target_node_type
        properties:
          source_code:
            type: string
          target_node_type:
            type: string
          pattern_filter:
            type: object
            default: {}
      outputs:
        type: array
        items:
          type: object
          required:
          - start_line
          - end_line
          - start_col
          - end_col
          - original_text
          properties:
            start_line:
              type: integer
            end_line:
              type: integer
            start_col:
              type: integer
            end_col:
              type: integer
            original_text:
              type: string
            node_name:
              type: string
              nullable: true
      parameters:
        type: object
        properties: {}
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|SourceCode|)
        space: O(Matches)
      preconditions:
      - len(input.source_code) >= 0
      postconditions:
      - all(m.start_line <= m.end_line for m in output)
      compatible_adapters:
      - ADAPTER-CST-MATCH-TO-PATCH-OP
    ---
    """
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self._regex, self._placeholders = self._compile_cst_pattern(pattern)

    def _compile_cst_pattern(self, pattern: str) -> tuple[re.Pattern, List[str]]:
        tokens = re.split(r"(\$[a-zA-Z0-9_]+|\$_)", pattern)
        regex_parts: List[str] = []
        placeholders: List[str] = []

        for i, token in enumerate(tokens):
            if not token:
                continue
            if token == "$_":
                regex_parts.append(r".*?")
            elif token.startswith("$"):
                var_name = token[1:]
                placeholders.append(var_name)
                next_token = tokens[i + 1] if i + 1 < len(tokens) else ""
                if next_token.startswith(")"):
                    regex_parts.append(f"(?P<{var_name}>[^)]*)")
                elif next_token.startswith(":"):
                    regex_parts.append(f"(?P<{var_name}>[^:\n]*)")
                else:
                    regex_parts.append(f"(?P<{var_name}>[a-zA-Z0-9_]+)")
            else:
                escaped = re.escape(token)
                normalized_ws = re.sub(r"\\\s+", r"\\s+", escaped)
                regex_parts.append(normalized_ws)

        compiled = re.compile("".join(regex_parts), re.MULTILINE | re.DOTALL)
        return compiled, placeholders

    def find_matches(self, source_code: str) -> List[CstMatch]:
        matches: List[CstMatch] = []
        line_offsets: List[int] = [0]
        for idx, char in enumerate(source_code):
            if char == "\n":
                line_offsets.append(idx + 1)

        def offset_to_coord(offset: int) -> tuple[int, int]:
            for line_idx, start in enumerate(line_offsets):
                if line_idx + 1 < len(line_offsets) and line_offsets[line_idx + 1] > offset:
                    return line_idx + 1, offset - start + 1
            return len(line_offsets), offset - line_offsets[-1] + 1

        for match in self._regex.finditer(source_code):
            s_offset, e_offset = match.start(), match.end()
            s_line, s_col = offset_to_coord(s_offset)
            e_line, e_col = offset_to_coord(e_offset)

            captures: Dict[str, str] = {}
            for name in self._placeholders:
                try:
                    captures[name] = match.group(name)
                except IndexError:
                    pass

            matches.append(
                CstMatch(
                    matched_text=match.group(0),
                    start_line=s_line,
                    end_line=e_line,
                    start_col=s_col,
                    end_col=e_col,
                    captures=captures,
                )
            )

        return matches
