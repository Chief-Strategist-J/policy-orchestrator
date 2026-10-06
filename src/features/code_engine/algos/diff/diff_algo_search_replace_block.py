"""
================================================================================
ALGORITHM BLUEPRINT: SEARCH/REPLACE BLOCK FORMAT PROCESSOR
================================================================================

1. OVERVIEW & OBJECTIVE:
   Processes and executes structured SEARCH/REPLACE edit blocks (the standard
   LLM code-modification protocol):
   ```
   <<<<<<< SEARCH
   original_code
   =======
   updated_code
   >>>>>>> REPLACE
   ```
   Validates uniqueness of search targets, performs exact or whitespace-tolerant
   matching, and applies replacement blocks cleanly without collateral damage.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Uniqueness Guard: SEARCH block must match EXACTLY ONE location in target text.
     If ambiguous (multiple matches), execution halts with an error unless
     disambiguating context is provided.
   - Marker Invariant: Markers must be well-formed and matched in sequence.

3. COMPLEXITY ANALYSIS:
   - Matching: O(N) where N is document size
   - Replacement: O(N)
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, Any, List, Optional, Tuple


class CodeEngineSearchReplaceBlockAlgo:
    """
    --- contract:
      id: ALGO-DIFF-125
      name: CodeEngineSearchReplaceBlockAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.search_replace_block
      - llm.edit_format
      - uniqueness_guard.exact_match
      input_schema:
        document_text: string
        blocks_text: string
      output_schema:
        algorithm: string
        updated_text: string
        applied_count: integer
        is_success: boolean
        errors: array
    ---
    """

    BLOCK_REGEX = re.compile(
        r"<<<<<<<\s*SEARCH\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>\s*REPLACE",
        re.DOTALL,
    )

    def parse_blocks(self, text: str) -> List[Tuple[str, str]]:
        matches = self.BLOCK_REGEX.findall(text)
        return [(m[0], m[1]) for m in matches]

    def apply_blocks(self, document: str, blocks: List[Tuple[str, str]]) -> Tuple[str, int, List[str]]:
        current_text = document
        applied = 0
        errors = []

        for i, (search_block, replace_block) in enumerate(blocks):
            occurrences = current_text.count(search_block)
            if occurrences == 0:
                stripped_search = "\n".join(line.strip() for line in search_block.splitlines())
                found_approx = False
                lines = current_text.splitlines()
                search_lines = search_block.splitlines()

                for j in range(len(lines) - len(search_lines) + 1):
                    sub = lines[j:j + len(search_lines)]
                    if "\n".join(l.strip() for l in sub) == stripped_search:
                        actual_search = "\n".join(sub)
                        current_text = current_text.replace(actual_search, replace_block, 1)
                        applied += 1
                        found_approx = True
                        break
                if not found_approx:
                    errors.append(f"Block {i+1}: Search target not found in document.")
            elif occurrences == 1:
                current_text = current_text.replace(search_block, replace_block, 1)
                applied += 1
            else:
                errors.append(f"Block {i+1}: Search target is ambiguous ({occurrences} matches).")

        return (current_text, applied, errors)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        document: str = str(payload.get("document_text", ""))
        blocks_text: str = str(payload.get("blocks_text", ""))

        parsed = self.parse_blocks(blocks_text)
        updated, count, errs = self.apply_blocks(document, parsed)

        return {
            "algorithm": "ALGO-DIFF-125",
            "updated_text": updated,
            "applied_count": count,
            "is_success": len(errs) == 0 and count == len(parsed),
            "errors": errs,
        }
