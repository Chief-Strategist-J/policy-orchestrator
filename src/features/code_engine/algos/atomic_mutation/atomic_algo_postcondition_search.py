"""
================================================================================
ALGORITHM BLUEPRINT: POST-CONDITION SEARCH (ZERO REMAINING VERIFIER)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Executes an exhaustive post-condition audit across the repository to verify
   that zero instances of a deprecated symbol, antipattern, or temporary marker
   remain after a refactoring campaign. If any match is discovered, execution
   fails with exact file and line locations.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Tolerance Invariant: `remaining_count == 0` for campaign sign-off.
   - Exact & Regex Matching: Evaluates literal strings or AST queries.

3. COMPLEXITY ANALYSIS:
   - Search: O(Total_Files * File_Size)
   - Space Complexity: O(Discovered_Violations)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, Any, List, Optional, Tuple


class CodeEnginePostConditionSearchAlgo:
    """
    --- contract:
      id: ALGO-ATMC-184
      name: CodeEnginePostConditionSearchAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(Files * Size)
        space: O(Violations)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - atomic.postcondition_search
      - verification.zero_remaining
      - audit.refactor_validation
      input_schema:
        files: object
        deprecated_pattern: string
        is_regex: boolean
      output_schema:
        algorithm: string
        zero_remaining: boolean
        remaining_count: integer
        violations: array
    ---
    """

    def scan_files(
        self, files: Dict[str, str], pattern: str, is_regex: bool = False
    ) -> List[Dict[str, Any]]:
        violations = []
        regex = re.compile(pattern) if is_regex else None

        for path, content in files.items():
            for line_idx, line in enumerate(content.splitlines(), start=1):
                if is_regex and regex:
                    if regex.search(line):
                        violations.append({"file": path, "line": line_idx, "content": line.strip()})
                else:
                    if pattern in line:
                        violations.append({"file": path, "line": line_idx, "content": line.strip()})

        return violations

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        files: Dict[str, str] = payload.get("files", {})
        pat: str = str(payload.get("deprecated_pattern", ""))
        is_reg: bool = bool(payload.get("is_regex", False))

        violations = self.scan_files(files, pat, is_reg)

        return {
            "algorithm": "ALGO-ATMC-184",
            "zero_remaining": len(violations) == 0,
            "remaining_count": len(violations),
            "violations": violations,
        }
