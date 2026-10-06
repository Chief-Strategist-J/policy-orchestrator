"""
================================================================================
ALGORITHM BLUEPRINT: TEXT EDIT APPLIER (RANGE + REPLACEMENT MUTATION)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standard atomic text edit model representing a mutation as `(start_offset,
   end_offset, new_text)`. Validates offset bounds, slices the original string,
   interpolates replacement text, and produces new text length and delta metrics.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Bounds Invariant: 0 <= start_offset <= end_offset <= len(original_text).
   - Range Length Delta: Delta = len(new_text) - (end_offset - start_offset).

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N) where N is document length
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional


class CodeEngineTextEditAlgo:
    """
    --- contract:
      id: ALGO-BUF-117
      name: CodeEngineTextEditAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.text_edit
      - mutation.range_replacement
      - text.offset_splice
      input_schema:
        text: string
        start_offset: integer
        end_offset: integer
        new_text: string
      output_schema:
        algorithm: string
        result_text: string
        original_length: integer
        new_length: integer
        delta: integer
    ---
    """

    def apply_edit(self, text: str, start: int, end: int, new_text: str) -> str:
        clamped_start = max(0, min(start, len(text)))
        clamped_end = max(clamped_start, min(end, len(text)))
        return text[:clamped_start] + new_text + text[clamped_end:]

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text: str = str(payload.get("text", ""))
        start: int = int(payload.get("start_offset", 0))
        end: int = int(payload.get("end_offset", 0))
        new_text: str = str(payload.get("new_text", ""))

        result = self.apply_edit(text, start, end, new_text)
        orig_len = len(text)
        new_len = len(result)

        return {
            "algorithm": "ALGO-BUF-117",
            "result_text": result,
            "original_length": orig_len,
            "new_length": new_len,
            "delta": new_len - orig_len,
        }
