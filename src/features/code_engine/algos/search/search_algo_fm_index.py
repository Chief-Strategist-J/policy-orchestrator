"""
================================================================================
ALGORITHM BLUEPRINT: FM-INDEX (BURROWS-WHEELER COMPRESSED FULL-TEXT INDEX)
================================================================================

1. OVERVIEW:
   The FM-Index (Ferragina-Manzini Index) is an opportunistic compressed full-text
   data structure combining the Burrows-Wheeler Transform (BWT) with succinct
   auxiliary rank tables to enable exact substring counting and pattern location
   in sub-linear O(P) time where P is pattern length.

2. MATHEMATICAL & ALGORITHMIC FORMULATION:
   - Input Text: T of length N with sentinel '$' lexicographically smallest.
   - Suffix Array (SA): SA[i] is the starting index of the i-th lexicographically
     sorted suffix of T.
   - BWT: BWT[i] = T[(SA[i] - 1) mod N].
   - C-Table: C[c] = count of characters in T strictly smaller than c.
   - Occ(c, k): Number of occurrences of character c in BWT[0...k-1].
   - Backward Search:
       Given pattern P of length m:
       Initialize range [sp, ep] = [0, N - 1]
       For i = m - 1 down to 0:
           c = P[i]
           sp = C[c] + Occ(c, sp)
           ep = C[c] + Occ(c, ep + 1) - 1
           If sp > ep: pattern does not occur in T (count = 0).
   - Occurrence Count: count = (ep - sp + 1) if sp <= ep else 0.
   - Sampled Suffix Array / LF-Mapping for Locating:
       LF(i) = C[BWT[i]] + Occ(BWT[i], i)
       SA[i] = (SA[LF(i)] + 1) mod N.

3. COMPLEXITY ANALYSIS:
   - Index Build: O(N log N) time, O(N * |Sigma|) space.
   - Count Query: O(P) time where P is pattern length.
   - Locate Query: O(P + occ * step) where occ is number of occurrences.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Pure, deterministic execution with zero mid-function comments.
   - All state transitions documented in top-level specification.
================================================================================
"""

from typing import Dict, List, Any, Optional


class SearchEngineFmIndexAlgo:
    """
    --- contract:
      id: ALGO-SRCH-51
      name: SearchEngineFmIndexAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(|Pattern|)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - index.fm_index
      - bwt.backward_search
      - compressed.index
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self, text: str = "") -> None:
        self._text = ""
        self._bwt = ""
        self._sa: List[int] = []
        self._c_table: Dict[str, int] = {}
        self._occ_table: Dict[str, List[int]] = {}
        if text:
            self.build_index(text)

    def build_index(self, text: str) -> Dict[str, Any]:
        if not text.endswith("$"):
            processed_text = text + "$"
        else:
            processed_text = text
        self._text = processed_text
        n = len(processed_text)

        suffixes = sorted(range(n), key=lambda i: processed_text[i:])
        self._sa = suffixes

        bwt_chars = [processed_text[(idx - 1) % n] for idx in suffixes]
        self._bwt = "".join(bwt_chars)

        alphabet = sorted(list(set(processed_text)))
        char_counts: Dict[str, int] = {}
        for ch in processed_text:
            char_counts[ch] = char_counts.get(ch, 0) + 1

        c_accum = 0
        self._c_table = {}
        for ch in alphabet:
            self._c_table[ch] = c_accum
            c_accum += char_counts.get(ch, 0)

        self._occ_table = {ch: [0] * (n + 1) for ch in alphabet}
        for ch in alphabet:
            running = 0
            for i in range(n):
                if self._bwt[i] == ch:
                    running += 1
                self._occ_table[ch][i + 1] = running

        return {
            "text_length": n,
            "alphabet": alphabet,
            "bwt": self._bwt,
            "c_table": self._c_table,
            "unique_characters": len(alphabet)
        }

    def _occ(self, char: str, index: int) -> int:
        if char not in self._occ_table:
            return 0
        clamped = max(0, min(index, len(self._bwt)))
        return self._occ_table[char][clamped]

    def count(self, pattern: str) -> int:
        if not pattern or not self._bwt:
            return 0
        n = len(self._bwt)
        sp = 0
        ep = n - 1

        for i in range(len(pattern) - 1, -1, -1):
            ch = pattern[i]
            if ch not in self._c_table:
                return 0
            c_val = self._c_table[ch]
            sp = c_val + self._occ(ch, sp)
            ep = c_val + self._occ(ch, ep + 1) - 1
            if sp > ep:
                return 0
        return ep - sp + 1

    def locate(self, pattern: str, max_results: int = 100) -> List[int]:
        if not pattern or not self._bwt:
            return []
        n = len(self._bwt)
        sp = 0
        ep = n - 1

        for i in range(len(pattern) - 1, -1, -1):
            ch = pattern[i]
            if ch not in self._c_table:
                return []
            c_val = self._c_table[ch]
            sp = c_val + self._occ(ch, sp)
            ep = c_val + self._occ(ch, ep + 1) - 1
            if sp > ep:
                return []

        locations: List[int] = []
        for row in range(sp, min(ep + 1, sp + max_results)):
            locations.append(self._sa[row])
        return sorted(locations)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = str(payload.get("text", ""))
        pattern = str(payload.get("pattern", ""))
        max_matches = int(payload.get("max_matches", 100))

        if text:
            build_meta = self.build_index(text)
        else:
            build_meta = {
                "text_length": len(self._text),
                "alphabet": sorted(list(set(self._text))),
                "bwt": self._bwt,
                "c_table": self._c_table,
                "unique_characters": len(self._c_table)
            }

        match_count = self.count(pattern) if pattern else 0
        locations = self.locate(pattern, max_results=max_matches) if pattern and match_count > 0 else []

        return {
            "algorithm": "ALGO-SRCH-51",
            "pattern": pattern,
            "match_count": match_count,
            "locations": locations,
            "index_meta": build_meta
        }
