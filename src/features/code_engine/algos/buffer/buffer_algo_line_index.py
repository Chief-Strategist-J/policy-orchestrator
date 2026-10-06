"""
================================================================================
ALGORITHM BLUEPRINT: LINE INDEX & OFFSET CACHE
================================================================================

1. OVERVIEW & OBJECTIVE:
   The Line Index precomputes and maintains an array of byte/character offsets
   marking the exact start of every line in a text document. It provides
   bidirectional conversions:
   - Line + Column (1-based or 0-based) -> Absolute Byte Offset in O(1).
   - Absolute Byte Offset -> Line + Column in O(log L) via binary search.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Monotonic Offset Invariant: line_starts[i] < line_starts[i+1] for all lines.
   - Zero Offset Root: line_starts[0] == 0 always.
   - Universal EOL Handling: Accurately parses Unix (\n), Windows (\r\n), and
     legacy Mac (\r) line terminators.

3. COMPLEXITY ANALYSIS:
   - Build Line Index: O(N) where N is text length
   - Offset to Position (Line, Col): O(log L) where L is total line count
   - Position to Offset: O(1)
   - Space Complexity: O(L)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import bisect
from typing import Dict, Any, List, Optional, Tuple


class CodeEngineLineIndexAlgo:
    """
    --- contract:
      id: ALGO-BUF-142
      name: CodeEngineLineIndexAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(N) build, O(log L) lookup
        space: O(L)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.line_index
      - text.offset_mapping
      - position.line_col
      input_schema:
        text: string
        queries: array
      output_schema:
        algorithm: string
        total_lines: integer
        line_starts: array
        query_results: array
    ---
    """

    def __init__(self, text: str = "") -> None:
        self.text: str = text
        self.line_starts: List[int] = [0]
        self._build_index()

    def _build_index(self) -> None:
        text_len: int = len(self.text)
        i: int = 0
        while i < text_len:
            ch: str = self.text[i]
            if ch == "\r":
                if i + 1 < text_len and self.text[i + 1] == "\n":
                    i += 1
                self.line_starts.append(i + 1)
            elif ch == "\n":
                self.line_starts.append(i + 1)
            i += 1

    def offset_to_position(self, offset: int) -> Tuple[int, int]:
        clamped_offset: int = max(0, min(offset, len(self.text)))
        line_idx: int = bisect.bisect_right(self.line_starts, clamped_offset) - 1
        line_number: int = line_idx + 1
        col_number: int = clamped_offset - self.line_starts[line_idx] + 1
        return (line_number, col_number)

    def position_to_offset(self, line: int, col: int) -> int:
        if line < 1:
            return 0
        if line > len(self.line_starts):
            return len(self.text)
        line_start: int = self.line_starts[line - 1]
        next_line_start: int = (
            self.line_starts[line] if line < len(self.line_starts) else len(self.text)
        )
        max_col_offset: int = max(0, next_line_start - line_start)
        clamped_col: int = max(1, min(col, max_col_offset + 1))
        return line_start + (clamped_col - 1)

    def get_line_content(self, line: int) -> str:
        if line < 1 or line > len(self.line_starts):
            return ""
        start: int = self.line_starts[line - 1]
        end: int = (
            self.line_starts[line] if line < len(self.line_starts) else len(self.text)
        )
        return self.text[start:end].rstrip("\r\n")

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text: str = str(payload.get("text", ""))
        queries: List[Dict[str, Any]] = payload.get("queries", [])

        idx = CodeEngineLineIndexAlgo(text)
        results: List[Dict[str, Any]] = []

        for q in queries:
            if "offset" in q:
                offset_val = int(q["offset"])
                line, col = idx.offset_to_position(offset_val)
                results.append({
                    "query_type": "offset_to_pos",
                    "offset": offset_val,
                    "line": line,
                    "column": col,
                    "line_text": idx.get_line_content(line),
                })
            elif "line" in q and "column" in q:
                l_val = int(q["line"])
                c_val = int(q["column"])
                computed_offset = idx.position_to_offset(l_val, c_val)
                results.append({
                    "query_type": "pos_to_offset",
                    "line": l_val,
                    "column": c_val,
                    "offset": computed_offset,
                })

        return {
            "algorithm": "ALGO-BUF-142",
            "total_lines": len(idx.line_starts),
            "line_starts": idx.line_starts,
            "query_results": results,
        }
