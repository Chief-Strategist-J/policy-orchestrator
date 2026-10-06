"""
================================================================================
ALGORITHM BLUEPRINT: REVERSE-ORDER EDIT APPLICATION
================================================================================

1. OVERVIEW & OBJECTIVE:
   Applies a collection of disjoint text edits to a document in reverse offset
   order (descending start_offset). Applying edits from bottom-to-top guarantees
   that earlier offsets in the file remain static and unshifted, eliminating the
   need for complex index rebasing across non-overlapping edits.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Descending Sort Invariant: Edits are sorted by `start_offset` descending:
     $E_1.start \ge E_2.start \ge \dots \ge E_k.start$.
   - Non-Overlap Invariant: Overlapping ranges must be validated and rejected
     prior to reverse application.

3. COMPLEXITY ANALYSIS:
   - Sort Edits: O(K log K) where K is number of edits
   - Application: O(K * N) where N is document size
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class CodeEngineReverseOrderEditAlgo:
    """
    --- contract:
      id: ALGO-BUF-120
      name: CodeEngineReverseOrderEditAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(K log K + K * N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.reverse_order_application
      - mutation.stable_offsets
      - batch_edit.bottom_to_top
      input_schema:
        text: string
        edits: array
      output_schema:
        algorithm: string
        result_text: string
        applied_count: integer
        is_valid: boolean
        error: string
    ---
    """

    def apply_reverse_edits(self, text: str, edits: List[Dict[str, Any]]) -> Tuple[str, int, bool, str]:
        normalized_edits = []
        for e in edits:
            s = int(e.get("start_offset", 0))
            end = int(e.get("end_offset", s))
            nt = str(e.get("new_text", ""))
            if s > end or s < 0 or end > len(text):
                return (text, 0, False, f"Invalid edit bounds: [{s}, {end}] for len {len(text)}")
            normalized_edits.append((s, end, nt))

        normalized_edits.sort(key=lambda x: (x[0], x[1]))

        for i in range(len(normalized_edits) - 1):
            curr = normalized_edits[i]
            nxt = normalized_edits[i + 1]
            if curr[1] > nxt[0]:
                return (text, 0, False, f"Overlapping edits detected: [{curr[0]}, {curr[1]}] and [{nxt[0]}, {nxt[1]}]")

        current_doc = text
        applied = 0
        for s, end, nt in reversed(normalized_edits):
            current_doc = current_doc[:s] + nt + current_doc[end:]
            applied += 1

        return (current_doc, applied, True, "")

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text: str = str(payload.get("text", ""))
        edits: List[Dict[str, Any]] = payload.get("edits", [])

        res_text, count, valid, err = self.apply_reverse_edits(text, edits)

        return {
            "algorithm": "ALGO-BUF-120",
            "result_text": res_text,
            "applied_count": count,
            "is_valid": valid,
            "error": err,
        }
