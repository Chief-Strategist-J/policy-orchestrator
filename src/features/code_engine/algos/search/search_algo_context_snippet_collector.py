"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CONTEXT SNIPPET COLLECTOR (ALGO 14)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Collects surrounding source context lines (pre-context and post-context)
   around a target line number for human-readable audit and diff reporting.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(SurroundingLinesCount).
   - Space Complexity: O(ContextWindowLines).
   - Rules Enforced: R1 (Read Before Write), R8 (Formatting).

3. EXECUTION FLOW:
   Splits file into lines, calculates bounded window [line_no - before, line_no + after],
   and formats lines with 1-based line numbers and active marker indicator (`>`).
================================================================================
"""

from typing import List, Dict, Any

class SearchEngineContextSnippetCollectorAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-14
      name: SearchEngineContextSnippetCollectorAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - formatter.snippet
      - context.surrounding_lines
      - ui.code_view
      inputs:
        type: object
        required:
        - lines
        - target_line
        properties:
          lines:
            type: array
            items:
              type: string
          target_line:
            type: integer
            minimum: 1
      outputs:
        type: object
        required:
        - start_line
        - end_line
        - formatted_snippet
        properties:
          start_line:
            type: integer
          end_line:
            type: integer
          formatted_snippet:
            type: string
          raw_lines:
            type: array
            items:
              type: string
      parameters:
        type: object
        properties:
          before:
            type: integer
            default: 2
          after:
            type: integer
            default: 2
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(Before + After)
        space: O(Before + After)
      preconditions:
      - 1 <= input.target_line <= len(input.lines)
      postconditions:
      - output.start_line >= 1
      - output.end_line <= len(input.lines)
      compatible_adapters: []
    ---
    """
    @staticmethod
    def collect_snippet(
        lines: List[str],
        target_line_1_indexed: int,
        lines_before: int = 2,
        lines_after: int = 2,
    ) -> Dict[str, Any]:
        total_lines = len(lines)
        target_idx = target_line_1_indexed - 1
        start_idx = max(0, target_idx - lines_before)
        end_idx = min(total_lines, target_idx + lines_after + 1)

        snippet_lines = []
        for i in range(start_idx, end_idx):
            marker = ">" if i == target_idx else " "
            snippet_lines.append(f"{marker} {i + 1:4d} | {lines[i].rstrip()}")

        return {
            "target_line": target_line_1_indexed,
            "start_line": start_idx + 1,
            "end_line": end_idx,
            "formatted_snippet": "\n".join(snippet_lines),
        }
