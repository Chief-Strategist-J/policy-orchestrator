"""
================================================================================
ALGORITHM BLUEPRINT: EXACT STRING REPLACE WITH UNIQUENESS CHECK
================================================================================

1. OVERVIEW & OBJECTIVE:
   Replaces a target substring in a source document strictly if and only if
   the target occurs exactly once (count == 1). If the target occurs 0 times
   (not found) or >1 times (ambiguous match), it aborts execution without
   modifying the document, preventing erroneous multi-site replacements.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Uniqueness Invariant: `document.count(target_string) == 1`.
   - Rejection on Ambiguity: Fails with count and line positions if count > 1.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N) where N is document size
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class CodeEngineExactReplaceUniqueAlgo:
    """
    --- contract:
      id: ALGO-ATMC-195
      name: CodeEngineExactReplaceUniqueAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - atomic.exact_replace_unique
      - safety.uniqueness_check
      - mutation.exact_string_replace
      input_schema:
        document_text: string
        target_string: string
        replacement_string: string
      output_schema:
        algorithm: string
        is_success: boolean
        updated_text: string
        occurrences: integer
        error_message: string
    ---
    """

    def replace_unique(self, doc: str, target: str, replacement: str) -> Tuple[bool, str, int, str]:
        if not target:
            return (False, doc, 0, "Target string cannot be empty.")

        count = doc.count(target)
        if count == 0:
            return (False, doc, 0, "Target string not found in document.")
        elif count > 1:
            return (False, doc, count, f"Ambiguous target: found {count} occurrences in document.")

        updated = doc.replace(target, replacement, 1)
        return (True, updated, 1, "")

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        doc: str = str(payload.get("document_text", ""))
        tgt: str = str(payload.get("target_string", ""))
        rep: str = str(payload.get("replacement_string", ""))

        success, res_text, occ, err = self.replace_unique(doc, tgt, rep)

        return {
            "algorithm": "ALGO-ATMC-195",
            "is_success": success,
            "updated_text": res_text,
            "occurrences": occ,
            "error_message": err,
        }
