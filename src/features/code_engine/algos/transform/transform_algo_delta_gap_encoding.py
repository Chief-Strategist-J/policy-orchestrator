"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DELTA GAP ENCODING (ALGO-TRFM-02)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Delta (Gap) Encoding is a lossless integer compression transformation on sorted
   posting lists. Storing the difference between consecutive identifiers rather
   than raw magnitudes (e.g., [1000, 1003, 1010] -> [1000, 3, 7]) shifts values
   into small ranges, maximizing compression ratios for bit-packing and Varint codecs.

2. ARCHITECTURAL ROLE:
   Transform & Compression role (Layer 1). Transforms document identifier lists
   prior to disk persistence and network transmission.

3. COMPLEXITY & INVARIANTS:
   - Encoding Time: O(N) linear scan.
   - Decoding Time: O(N) linear cumulative sum.
   - Space Complexity: O(N) transformed array.
   - Zero-Inline-Comment Doctrine: Code body is 100% comment-free.

4. EXECUTION FLOW:
   a. Sort input integers ascending.
   b. Calculate consecutive differences: G[0] = S[0], G[i] = S[i] - S[i-1].
   c. Optionally partition into seekable blocks with base offset headers.
   d. Inverse reconstruction calculates running cumulative sums.
================================================================================
"""

from typing import Dict, List, Any, Optional


class TransformAlgoDeltaGapEncoding:
    """
    --- contract:
      id: ALGO-TRFM-02
      name: TransformAlgoDeltaGapEncoding
      version: 1.0.0
      category: transform
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
        - compression.delta_gap
        - encoding.integers
        - posting_list.optimization
      input_schema:
        sorted_integers: list[int]
        block_size: int
      output_schema:
        gaps: list[int]
        total_count: int
    ---
    """

    def encode(self, sorted_integers: List[int], block_size: Optional[int] = None) -> Dict[str, Any]:
        if not sorted_integers:
            return {"gaps": [], "blocks": [], "total_count": 0}

        sorted_list = sorted(sorted_integers)
        gaps: List[int] = [sorted_list[0]]
        for i in range(1, len(sorted_list)):
            gaps.append(sorted_list[i] - sorted_list[i - 1])

        blocks: List[Dict[str, Any]] = []
        if block_size and block_size > 0:
            for start_idx in range(0, len(sorted_list), block_size):
                chunk = sorted_list[start_idx : start_idx + block_size]
                chunk_gaps = [chunk[0]]
                for j in range(1, len(chunk)):
                    chunk_gaps.append(chunk[j] - chunk[j - 1])
                blocks.append({
                    "block_index": len(blocks),
                    "base_val": chunk[0],
                    "gaps": chunk_gaps,
                    "count": len(chunk),
                })

        return {
            "gaps": gaps,
            "blocks": blocks,
            "total_count": len(sorted_list),
            "min_gap": min(gaps[1:]) if len(gaps) > 1 else 0,
            "max_gap": max(gaps[1:]) if len(gaps) > 1 else 0,
        }

    def decode(self, gaps: List[int]) -> List[int]:
        if not gaps:
            return []
        reconstructed: List[int] = [gaps[0]]
        running_sum = gaps[0]
        for i in range(1, len(gaps)):
            running_sum += gaps[i]
            reconstructed.append(running_sum)
        return reconstructed

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw_integers = [int(x) for x in payload.get("integers", [])]
        raw_gaps = [int(x) for x in payload.get("gaps", [])]
        block_size = payload.get("block_size")

        encoded_data = None
        decoded_data = None

        if raw_integers:
            encoded_data = self.encode(raw_integers, block_size=block_size)
        if raw_gaps:
            decoded_data = self.decode(raw_gaps)

        return {
            "status": "success",
            "encoded": encoded_data,
            "decoded": decoded_data,
        }


SearchEngineDeltaGapEncodingAlgo = TransformAlgoDeltaGapEncoding
