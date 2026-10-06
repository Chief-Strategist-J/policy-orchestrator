"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SUFFIX ARRAY & BINARY SEARCH (ALGO 47)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a Suffix Array (SA) storing the sorted starting positions of
   every suffix of a text buffer. Executes fast O(M * log N) binary search
   substring queries, locating all occurrences in contiguous ranges. Foundation
   of livegrep, FM-indices, and large-scale code navigation.

2. COMPLEXITY & INVARIANTS:
   - Suffix Array Construction: O(N * log N) / O(N).
   - Substring Query: O(|Pattern| * log N) binary search.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Builds sorted suffix array SA where S[SA[i]:] < S[SA[i+1]:].
   - Binary searches lower bound (first suffix where pattern is prefix).
   - Binary searches upper bound (last suffix where pattern is prefix).
   - Emits exact occurrence count and sorted text match positions.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class SearchEngineSuffixArraySaisAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-47
      name: SearchEngineSuffixArraySaisAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.suffix_array
      - livegrep.substring
      - index.suffix_index
      inputs:
        type: object
        required:
        - text
        properties:
          text:
            type: string
      outputs:
        type: object
        required:
        - suffix_array
        - matches
        - occurrence_count
        properties:
          suffix_array:
            type: array
            items:
              type: integer
          matches:
            type: array
            items:
              type: integer
          occurrence_count:
            type: integer
      parameters:
        type: object
        required:
        - pattern
        properties:
          pattern:
            type: string
            minLength: 1
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N log N + M log N)
        space: O(N)
    ---
    """

    @classmethod
    def build_suffix_array(cls, text: str) -> List[int]:
        n = len(text)
        suffixes = sorted(range(n), key=lambda i: text[i:])
        return suffixes

    @classmethod
    def query(cls, text: str, sa: List[int], pattern: str) -> List[int]:
        n = len(text)
        m = len(pattern)
        if m == 0 or n == 0:
            return []

        low, high = 0, n - 1
        first_match = -1
        while low <= high:
            mid = (low + high) // 2
            suffix_start = sa[mid]
            candidate = text[suffix_start:suffix_start + m]
            if candidate >= pattern:
                if candidate == pattern:
                    first_match = mid
                high = mid - 1
            else:
                low = mid + 1

        if first_match == -1:
            return []

        low, high = first_match, n - 1
        last_match = first_match
        while low <= high:
            mid = (low + high) // 2
            suffix_start = sa[mid]
            candidate = text[suffix_start:suffix_start + m]
            if candidate == pattern:
                last_match = mid
                low = mid + 1
            elif candidate > pattern:
                high = mid - 1
            else:
                low = mid + 1

        matches = [sa[i] for i in range(first_match, last_match + 1)]
        return sorted(matches)

    @classmethod
    def execute(cls, text: str, pattern: str) -> Dict[str, Any]:
        sa = cls.build_suffix_array(text)
        matches = cls.query(text, sa, pattern)
        return {
            "suffix_array": sa,
            "matches": matches,
            "occurrence_count": len(matches),
        }
