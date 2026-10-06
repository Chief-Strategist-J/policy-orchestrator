"""
================================================================================
ALGORITHM BLUEPRINT: OPERATIONAL TRANSFORMATION EDIT REBASING
================================================================================

1. OVERVIEW & OBJECTIVE:
   Rebases text edit offsets across concurrent or sequential code mutations
   (Operational Transformation paradigm). Given Edit A $[s_a, e_a] \to text_a$
   and Edit B $[s_b, e_b] \to text_b$, transforms Edit B's coordinates into
   rebased bounds $[s'_b, e'_b]$ that correctly apply against the document state
   after Edit A has already been executed.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Offset Shift Invariant:
     If $e_a \le s_b$: $s'_b = s_b + \Delta_a$, $e'_b = e_b + \Delta_a$ where $\Delta_a = len(text_a) - (e_a - s_a)$.
     If $e_b \le s_a$: $s'_b = s_b$, $e'_b = e_b$ (unaffected).
   - Collision Flagging: Intersecting/overlapping edits produce explicit conflict alerts.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(1) per rebased pair, O(K) for a sequence of edits
   - Space Complexity: O(K)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class CodeEngineEditRebasingAlgo:
    """
    --- contract:
      id: ALGO-BUF-123
      name: CodeEngineEditRebasingAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(1) per rebase operation
        space: O(1)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.edit_rebasing
      - operational_transformation.offsets
      - concurrent_edits.rebase
      input_schema:
        prior_edit: object
        target_edit: object
      output_schema:
        algorithm: string
        rebased_start: integer
        rebased_end: integer
        has_conflict: boolean
    ---
    """

    def rebase_edit(
        self, s_a: int, e_a: int, new_text_a: str, s_b: int, e_b: int
    ) -> Tuple[int, int, bool]:
        delta_a: int = len(new_text_a) - (e_a - s_a)

        if e_a <= s_b:
            return (s_b + delta_a, e_b + delta_a, False)
        elif e_b <= s_a:
            return (s_b, e_b, False)
        else:
            return (s_b + delta_a, max(s_b + delta_a, e_b + delta_a), True)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prior = payload.get("prior_edit", {})
        target = payload.get("target_edit", {})

        s_a = int(prior.get("start_offset", 0))
        e_a = int(prior.get("end_offset", s_a))
        nt_a = str(prior.get("new_text", ""))

        s_b = int(target.get("start_offset", 0))
        e_b = int(target.get("end_offset", s_b))

        r_start, r_end, conflict = self.rebase_edit(s_a, e_a, nt_a, s_b, e_b)

        return {
            "algorithm": "ALGO-BUF-123",
            "rebased_start": r_start,
            "rebased_end": r_end,
            "has_conflict": conflict,
        }
