"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KASAI LINEAR LCP ARRAY BUILDER (ALGO 48)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs the Longest Common Prefix (LCP) array from text and its Suffix
   Array in strict linear O(N) time using Kasai's algorithm. For each adjacent
   pair of suffixes in sorted order, computes their common prefix length. High
   LCP values locate the longest duplicated code blocks for clone consolidation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Strict O(N) linear time (LCP value decreases by <= 1 per step).
   - Space Complexity: O(N) array storage.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Computes rank array (inverse of Suffix Array: rank[SA[i]] = i).
   - Iterates through text positions i = 0 to N-1:
     * If rank[i] == 0, LCP[0] = 0.
     * Otherwise, compares suffix at i with preceding suffix at SA[rank[i] - 1].
     * Advances prefix match counter h from previous step (h = max(0, h - 1)).
     * Sets LCP[rank[i]] = h.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional
from ..search.search_algo_suffix_array_sais import SearchEngineSuffixArraySaisAlgo


class TransformAlgoLcpArrayKasai:
    """
    --- contract:
      id: ALGO-TRFM-06
      name: TransformAlgoLcpArrayKasai
      version: 1.0.0
      category: transform
      capability_tags:
      - search.lcp_array
      - kasai.linear_lcp
      - duplicate.longest_repeated_substring
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
        - lcp_array
        - max_lcp
        - longest_repeated_substring
        properties:
          lcp_array:
            type: array
            items:
              type: integer
          max_lcp:
            type: integer
          longest_repeated_substring:
            type: string
      parameters:
        type: object
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N)
        space: O(N)
    ---
    """

    @classmethod
    def build_lcp(cls, text: str, sa: List[int]) -> List[int]:
        n = len(text)
        if n == 0:
            return []

        rank = [0] * n
        for i, pos in enumerate(sa):
            rank[pos] = i

        lcp = [0] * n
        h = 0

        for i in range(n):
            if rank[i] > 0:
                j = sa[rank[i] - 1]
                while (i + h < n) and (j + h < n) and (text[i + h] == text[j + h]):
                    h += 1
                lcp[rank[i]] = h
                if h > 0:
                    h -= 1

        return lcp

    @classmethod
    def find_longest_repeated(cls, text: str, sa: List[int], lcp: List[int]) -> Tuple[int, str]:
        if not lcp:
            return 0, ""
        max_val = 0
        best_pos = 0
        for i in range(len(lcp)):
            if lcp[i] > max_val:
                max_val = lcp[i]
                best_pos = sa[i]

        repeated_str = text[best_pos:best_pos + max_val] if max_val > 0 else ""
        return max_val, repeated_str

    @classmethod
    def execute(cls, text: str) -> Dict[str, Any]:
        sa = SearchEngineSuffixArraySaisAlgo.build_suffix_array(text)
        lcp = cls.build_lcp(text, sa)
        max_lcp, longest_rep = cls.find_longest_repeated(text, sa, lcp)
        return {
            "lcp_array": lcp,
            "max_lcp": max_lcp,
            "longest_repeated_substring": longest_rep,
        }


SearchEngineLcpArrayKasaiAlgo = TransformAlgoLcpArrayKasai
