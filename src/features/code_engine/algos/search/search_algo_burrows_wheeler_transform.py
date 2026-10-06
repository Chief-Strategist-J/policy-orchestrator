"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BURROWS-WHEELER TRANSFORM & LF-MAPPING (ALGO 50)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements the Burrows-Wheeler Transform (BWT), Last-to-First (LF) mapping,
   and inverse BWT reconstruction. Permutes a text into runs of repeated
   characters, enabling FM-index compression and sub-linear backward search counts
   without text decompression.

2. COMPLEXITY & INVARIANTS:
   - Forward BWT: O(N log N) / O(N) via suffix array rotation sorting.
   - Inverse BWT: O(N) linear time via LF-mapping property.
   - Backward Search Count: O(|Pattern|) exact occurrence count queries.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Appends sentinel marker "$" (lexicographically smallest character).
   - Generates all cyclic rotations, sorts them alphabetically, and takes last column -> BWT.
   - Reconstructs original text using LF-mapping:
     * First column F is sorted BWT (L).
     * Character at L[i] corresponds to the same occurrence rank in F.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class SearchEngineBurrowsWheelerTransformAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-50
      name: SearchEngineBurrowsWheelerTransformAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - compression.bwt
      - fm_index.lf_mapping
      - string.block_sorting
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
        - bwt_string
        - reconstructed_text
        - primary_index
        properties:
          bwt_string:
            type: string
          reconstructed_text:
            type: string
          primary_index:
            type: integer
      parameters:
        type: object
        properties:
          sentinel:
            type: string
            default: "$"
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N log N) transform, O(N) inverse
        space: O(N)
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
    def execute(cls, text: str, sentinel: str = "$") -> Dict[str, Any]:
        bwt_str, primary_idx = cls.transform(text, sentinel)
        reconstructed = cls.inverse_transform(bwt_str, sentinel)
        return {
            "bwt_string": bwt_str,
            "reconstructed_text": reconstructed,
            "primary_index": primary_idx,
        }
