"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BURROWS-WHEELER TRANSFORM (ALGO-TRFM-01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements the Burrows-Wheeler Transform (BWT), Last-to-First (LF) mapping,
   and inverse BWT reconstruction. Permutes a text into runs of repeated
   characters, enabling FM-index compression and sub-linear backward search counts
   without text decompression.

2. ARCHITECTURAL ROLE:
   Transform & Compression role (Layer 1). Reorganizes text strings into
   high-redundancy permutations for succinct index structures.

3. COMPLEXITY & INVARIANTS:
   - Forward BWT: O(N log N) / O(N) via suffix array rotation sorting.
   - Inverse BWT: O(N) linear time via LF-mapping property.
   - Backward Search Count: O(|Pattern|) exact occurrence count queries.
   - Zero-Inline-Comment Doctrine: Code body is 100% comment-free.

4. EXECUTION FLOW:
   a. Append sentinel marker "$" (lexicographically smallest character).
   b. Generate all cyclic rotations, sort them alphabetically, take last column -> BWT.
   c. Reconstruct original text using LF-mapping:
      * First column F is sorted BWT (L).
      * Character at L[i] corresponds to the same occurrence rank in F.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class TransformAlgoBurrowsWheeler:
    """
    --- contract:
      id: ALGO-TRFM-01
      name: TransformAlgoBurrowsWheeler
      version: 1.0.0
      category: transform
      complexity:
        time: O(N log N) transform, O(N) inverse
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
        - compression.bwt
        - fm_index.lf_mapping
        - string.block_sorting
      input_schema:
        text: string
        sentinel: string
      output_schema:
        bwt_string: string
        primary_index: int
    ---
    """

    @classmethod
    def transform(cls, text: str, sentinel: str = "$") -> Tuple[str, int]:
        s = text + sentinel
        n = len(s)
        rotations = sorted(range(n), key=lambda i: s[i:] + s[:i])
        bwt_chars = [s[(i + n - 1) % n] for i in rotations]
        primary_index = rotations.index(0)
        return "".join(bwt_chars), primary_index

    @classmethod
    def inverse_transform(cls, bwt_string: str, sentinel: str = "$") -> str:
        n = len(bwt_string)
        if n == 0:
            return ""

        table = [""] * n
        for _ in range(n):
            table = sorted([bwt_string[i] + table[i] for i in range(n)])

        for row in table:
            if row.endswith(sentinel):
                return row[:-len(sentinel)]
        return ""

    @classmethod
    def count_occurrences(cls, bwt_string: str, pattern: str) -> int:
        if not bwt_string or not pattern:
            return 0
        n = len(bwt_string)
        first_col = sorted(bwt_string)
        top = 0
        bottom = n - 1

        for char in reversed(pattern):
            if char not in bwt_string[top : bottom + 1]:
                return 0
            first_occurrence = first_col.index(char)
            top = first_occurrence + bwt_string[:top].count(char)
            bottom = first_occurrence + bwt_string[: bottom + 1].count(char) - 1
            if top > bottom:
                return 0

        return bottom - top + 1

    @classmethod
    def execute(cls, text: str, sentinel: str = "$") -> Dict[str, Any]:
        bwt_str, primary_idx = cls.transform(text, sentinel)
        reconstructed = cls.inverse_transform(bwt_str, sentinel)
        return {
            "bwt_string": bwt_str,
            "primary_index": primary_idx,
            "reconstructed_text": reconstructed,
        }


SearchEngineBurrowsWheelerTransformAlgo = TransformAlgoBurrowsWheeler

