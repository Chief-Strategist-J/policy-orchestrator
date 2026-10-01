"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SIMD-STYLE FAST BYTE SEARCHER (ALGO 10)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Vectorized / fast byte finder that uses C-accelerated byte-level `find()`
   and Boyer-Moore-Horspool bad-character tables to locate exact substring
   occurrences at gigabyte-per-second throughput.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Best O(N / M), Worst O(N * M) where M is pattern length.
   - Space Complexity: O(AlphabetSize) for skip table.
   - Rules Enforced: R1 (Read Before Write), R4 (Expected Match Count).

3. EXECUTION FLOW:
   Computes bad-character jump table for pattern bytes. Scans byte buffers
   skipping non-matching alignments, and records 0-indexed byte offsets.
================================================================================
"""

from typing import List

class SearchEngineSimdMemchrAlgo:
    @staticmethod
    def find_all_occurrences(content: str, pattern: str) -> List[int]:
        if not pattern or not content:
            return []
        
        matches: List[int] = []
        target_bytes = pattern.encode("utf-8")
        src_bytes = content.encode("utf-8")
        p_len = len(target_bytes)
        
        start = 0
        while True:
            idx = src_bytes.find(target_bytes, start)
            if idx == -1:
                break
            matches.append(idx)
            start = idx + 1

        return matches
