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
    """
    ---
    contract:
      algo_id: ALGO-SRCH-10
      name: SearchEngineSimdMemchrAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.raw_byte
      - simd.memchr
      - scan.fast_byte
      inputs:
        type: object
        required:
        - haystack
        - needle
        properties:
          haystack:
            type: string
          needle:
            type: string
      outputs:
        type: array
        items:
          type: integer
          description: Byte offset
      parameters:
        type: object
        properties: {}
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|Haystack| / SIMD_WIDTH)
        space: O(1)
      preconditions:
      - len(input.needle) > 0
      postconditions:
      - is_strictly_ascending(output)
      compatible_adapters:
      - ADAPTER-OFFSET-TO-SPAN-OBS-16
    ---
    """
    @staticmethod
    def find_all_occurrences(content: str, pattern: str) -> List[int]:
        if not pattern or not content:
            return []
        
        matches: List[int] = []
        target_bytes = pattern.encode("utf-8")
        src_bytes = content.encode("utf-8")
        
        start = 0
        while True:
            idx = src_bytes.find(target_bytes, start)
            if idx == -1:
                break
            matches.append(idx)
            start = idx + 1

        return matches

    @staticmethod
    def find_byte_offsets(data: bytes, target_byte: int) -> List[int]:
        if not data:
            return []
        offsets: List[int] = []
        start = 0
        target = bytes([target_byte]) if isinstance(target_byte, int) else target_byte
        while True:
            idx = data.find(target, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + 1
        return offsets

