"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: Z-ALGORITHM PREFIX PREPROCESSOR (ALGO 26)
================================================================================

1. OVERVIEW & OBJECTIVE:
   The Z-algorithm is a linear-time string analysis algorithm that computes an
   array Z for a string S of length N, where Z[i] is the length of the longest
   substring starting at S[i] that is also a prefix of S. For pattern searching,
   it computes Z on the concatenated string P + "$" + T in strict O(|P| + |T|).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N) strict linear time (at most 2N character comparisons).
   - Space Complexity: O(N) for the Z-array storage.
   - Purity & Determinism: 100% pure, deterministic, and idempotent.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Maintains [L, R] interval representing the rightmost segment matching a prefix.
   - For index i > R: computes Z[i] from scratch by scalar comparison and expands [L, R].
   - For index i <= R: uses symmetry Z[k] where k = i - L. If match extends past R,
     expands from R onwards and updates [L, R].
   - Searches patterns by matching Z[i] == |P| for indices in text region.
================================================================================
"""

from typing import List, Dict, Any


class SearchEngineZAlgorithmAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-26
      name: SearchEngineZAlgorithmAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.exact
      - string.periodicity
      - string.z_algorithm
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
        - matches
        - z_array
        properties:
          matches:
            type: array
            items:
              type: object
              required:
              - start_offset
              - end_offset
              - pattern
              properties:
                start_offset:
                  type: integer
                end_offset:
                  type: integer
                pattern:
                  type: string
          z_array:
            type: array
            items:
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
        time: O(N + M)
        space: O(N + M)
    ---
    """

    @staticmethod
    def compute_z_array(s: str) -> List[int]:
        n = len(s)
        z = [0] * n
        if n == 0:
            return z
        z[0] = n
        l, r = 0, 0
        for i in range(1, n):
            if i <= r:
                k = i - l
                if z[k] < r - i + 1:
                    z[i] = z[k]
                else:
                    l = i
                    while r < n and s[r] == s[r - l]:
                        r += 1
                    z[i] = r - l
                    r -= 1
            else:
                l, r = i, i
                while r < n and s[r] == s[r - l]:
                    r += 1
                z[i] = r - l
                r -= 1
        return z

    @classmethod
    def search(cls, text: str, pattern: str, delimiter: str = "$") -> List[Dict[str, Any]]:
        if not pattern or not text:
            return []
        m = len(pattern)
        concat = f"{pattern}{delimiter}{text}"
        z = cls.compute_z_array(concat)
        matches: List[Dict[str, Any]] = []

        for i in range(m + 1, len(concat)):
            if z[i] == m:
                start_offset = i - (m + 1)
                matches.append({
                    "start_offset": start_offset,
                    "end_offset": start_offset + m,
                    "pattern": pattern,
                })

        return matches

    @classmethod
    def execute(cls, text: str, pattern: str, delimiter: str = "$") -> Dict[str, Any]:
        if not pattern:
            raise ValueError("Pattern cannot be empty")
        matches = cls.search(text, pattern, delimiter)
        z_array = cls.compute_z_array(f"{pattern}{delimiter}{text}")
        return {
            "matches": matches,
            "z_array": z_array,
        }
