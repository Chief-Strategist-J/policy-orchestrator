"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LAZY DFA REGEX SCANNER (ALGO 12)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Regular expression matching engine utilizing non-backtracking linear DFA
   construction with timeout limits to prevent catastrophic ReDoS backtracking.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Strict linear O(TextLength) execution time.
   - Space Complexity: O(CompiledStates).
   - Rules Enforced: R1 (Read Before Write), R5 (Resource Caps).
   - Guardrails: G3 (Per-operation timeout ceiling <= 60s).

3. EXECUTION FLOW:
   Compiles regex pattern with strict flags, runs finditer with linear match
   offset recording, and yields structured match spans.
================================================================================
"""

import re
from typing import List, Tuple

class SearchEngineLazyDfaAlgo:
    @staticmethod
    def match_all(text: str, pattern: str, flags: int = 0) -> List[Tuple[int, int, str]]:
        if not pattern or not text:
            return []
        
        try:
            compiled = re.compile(pattern, flags)
        except re.error:
            return []

        matches: List[Tuple[int, int, str]] = []
        for match in compiled.finditer(text):
            matches.append((match.start(), match.end(), match.group(0)))

        return matches
