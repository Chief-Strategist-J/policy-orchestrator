"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: WU-MANBER MULTI-PATTERN SEARCH (ALGO 25)
================================================================================

1. OVERVIEW & OBJECTIVE:
   The Wu-Manber algorithm is a sub-linear multi-pattern keyword search engine
   designed to scan text simultaneously for thousands of patterns. It extends
   Boyer-Moore bad character skipping to multi-pattern dictionaries using
   multi-byte block hashing (B-grams, typically B=2 or B=3).

2. COMPLEXITY & INVARIANTS:
   - Preprocessing: Time O(Σ|P_i| + 256^B) | Space O(256^B + TotalPatterns).
   - Search: Average Time O(N / M_min), Worst-Case O(N * K).
   - Zero-Inline-Comment Doctrine: Function bodies are 100% pure and comment-free.

3. EXECUTION FLOW:
   - Determines minimum pattern length M_min across dictionary.
   - Builds SHIFT table mapping B-gram hashes to safe jump distances (M_min - B + 1).
   - Builds HASH table mapping tail B-grams to candidate pattern indices.
   - Builds PREFIX table storing prefix hashes for rapid false-candidate pruning.
   - Slides a window of size M_min across text:
     * Hashes trailing B-gram; if SHIFT > 0, skips forward.
     * If SHIFT == 0, verifies candidates via prefix hash and string equality.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class SearchEngineWuManberAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-25
      name: SearchEngineWuManberAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.multipattern
      - search.sublinear
      - search.wu_manber
      inputs:
        type: object
        required:
        - text
        properties:
          text:
            type: string
      outputs:
        type: array
        items:
          type: object
          required:
          - start_offset
          - end_offset
          - pattern
          - pattern_index
          properties:
            start_offset:
              type: integer
              minimum: 0
            end_offset:
              type: integer
              minimum: 0
            pattern:
              type: string
            pattern_index:
              type: integer
      parameters:
        type: object
        required:
        - patterns
        properties:
          patterns:
            type: array
            items:
              type: string
              minLength: 1
            minItems: 1
          block_size:
            type: integer
            default: 2
            minimum: 1
            maximum: 4
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N / M_min)
        space: O(256^B + K)
    ---
    """

    def __init__(self, patterns: List[str], block_size: int = 2) -> None:
        if not patterns or any(len(p) == 0 for p in patterns):
            raise ValueError("Patterns must be non-empty strings")
        self.patterns = patterns
        self.m_min = min(len(p) for p in patterns)
        self.b = min(block_size, self.m_min)
        self.shift_table: Dict[int, int] = {}
        self.hash_table: Dict[int, List[int]] = {}
        self.prefix_table: Dict[int, List[int]] = {}
        self._preprocess()

    def _hash_block(self, s: str, start: int) -> int:
        h = 0
        for i in range(self.b):
            h = (h << 8) | ord(s[start + i])
        return h

    def _hash_prefix(self, s: str) -> int:
        h = 0
        p_len = min(2, len(s))
        for i in range(p_len):
            h = (h << 8) | ord(s[i])
        return h

    def _preprocess(self) -> None:
        default_shift = self.m_min - self.b + 1
        for idx, pat in enumerate(self.patterns):
            for j in range(self.m_min - self.b + 1):
                h = self._hash_block(pat, j)
                shift = self.m_min - self.b - j
                current = self.shift_table.get(h, default_shift)
                self.shift_table[h] = min(current, shift)

            tail_h = self._hash_block(pat, self.m_min - self.b)
            if tail_h not in self.hash_table:
                self.hash_table[tail_h] = []
                self.prefix_table[tail_h] = []
            self.hash_table[tail_h].append(idx)
            self.prefix_table[tail_h].append(self._hash_prefix(pat))

    def search(self, text: str) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        n = len(text)
        if n < self.m_min:
            return matches

        i = self.m_min - 1
        default_shift = self.m_min - self.b + 1

        while i < n:
            block_start = i - self.b + 1
            h = self._hash_block(text, block_start)
            shift = self.shift_table.get(h, default_shift)

            if shift == 0:
                candidates = self.hash_table.get(h, [])
                prefixes = self.prefix_table.get(h, [])
                for c_idx, pref_h in zip(candidates, prefixes):
                    pat = self.patterns[c_idx]
                    p_len = len(pat)
                    pat_start = i - self.m_min + 1
                    pat_end = pat_start + p_len

                    if pat_end <= n:
                        text_pref = self._hash_prefix(text[pat_start:pat_start + min(2, p_len)])
                        if text_pref == pref_h:
                            if text[pat_start:pat_end] == pat:
                                matches.append({
                                    "start_offset": pat_start,
                                    "end_offset": pat_end,
                                    "pattern": pat,
                                    "pattern_index": c_idx,
                                })
                i += 1
            else:
                i += shift

        return matches

    @classmethod
    def execute(cls, text: str, patterns: List[str], block_size: int = 2) -> List[Dict[str, Any]]:
        engine = cls(patterns=patterns, block_size=block_size)
        return engine.search(text)
