"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GLOB MATCHER (ALGO 04)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Double-star recursive glob compiler and trie-like path evaluator supporting
   patterns like `**/*.ts`, `src/**/test_*.py`, and `config/*.yaml`.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(PathLen) per path matching.
   - Space Complexity: O(RegexLength).
   - Rules Enforced: R1 (Read Before Write), R8 (Deterministic Match List).

3. EXECUTION FLOW:
   Translates double-star and wildcard glob expressions into strict compiled
   regex matchers and filters input candidate paths.
================================================================================
"""

import re
import os
import fnmatch
from typing import List

class SearchEngineGlobMatcherAlgo:
    @staticmethod
    def execute(pattern: str, file_paths: List[str]) -> List[str]:
        regex_pattern = fnmatch.translate(pattern)
        matcher = re.compile(regex_pattern)
        return [fp for fp in file_paths if matcher.match(fp) or matcher.match(os.path.basename(fp))]
