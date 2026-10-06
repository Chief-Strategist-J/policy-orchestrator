"""
================================================================================
ALGORITHM BLUEPRINT: DELTA (GAP) ENCODING & DECODING
================================================================================

1. OVERVIEW:
   Delta (Gap) Encoding is a lossless integer compression technique used on sorted
   posting lists. By storing the difference between consecutive identifiers rather
   than the raw magnitudes (e.g., [1000, 1003, 1010] -> [1000, 3, 7]), the values
   are shifted into much smaller ranges, drastically improving compression ratios
   under Varint, Elias-Fano, or Bit-Packing codecs.

2. MATHEMATICAL FORMULATION:
   - Forward Delta:
       D[0] = S[0]
       D[i] = S[i] - S[i - 1] for i >= 1
   - Inverse Running Sum:
       S[0] = D[0]
       S[i] = S[i - 1] + D[i] for i >= 1
   - Block Chunking:
       Lists are chunked into blocks of size B with an absolute base ID at the
       head of each block, allowing O(1) random block seeking.

3. COMPLEXITY ANALYSIS:
   - Encoding Time: O(N) linear scan.
   - Decoding Time: O(N) linear cumulative sum.
   - Space Reduction: 50%-85% reduction in entropy before bit-level serialization.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - 0 inline comments inside function bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional


class SearchEngineDeltaGapEncodingAlgo:
    """
    Implements Delta/Gap encoding and prefix-sum decoding over integer lists
    with block-level reset boundaries.
    """

    def encode(self, sorted_integers: List[int], block_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Encodes a sorted list of integers into delta differences.
        """
        if not sorted_integers:
            return {"gaps": [], "blocks": [], "total_count": 0}

        sorted_list = sorted(sorted_integers)
        gaps: List[int] = [sorted_list[0]]
        for i in range(1, len(sorted_list)):
            gaps.append(sorted_list[i] - sorted_list[i - 1])

        blocks: List[Dict[str, Any]] = []
        if block_size and block_size > 0:
            for start_idx in range(0, len(sorted_list), block_size):
                chunk = sorted_list[start_idx:start_idx + block_size]
                chunk_gaps = [chunk[0]]
                for j in range(1, len(chunk)):
                    chunk_gaps.append(chunk[j] - chunk[j - 1])
                blocks.append({
                    "block_index": len(blocks),
                    "base_val": chunk[0],
                    "gaps": chunk_gaps,
                    "count": len(chunk)
                })

        return {
            "gaps": gaps,
            "blocks": blocks,
            "total_count": len(sorted_list),
            "min_gap": min(gaps[1:]) if len(gaps) > 1 else 0,
            "max_gap": max(gaps[1:]) if len(gaps) > 1 else 0
        }

    def decode(self, gaps: List[int]) -> List[int]:
        """
        Decodes a delta-encoded list back into its original sorted integer sequence.
        """
        if not gaps:
            return []
        reconstructed: List[int] = [gaps[0]]
        running_sum = gaps[0]
        for i in range(1, len(gaps)):
            running_sum += gaps[i]
            reconstructed.append(running_sum)
        return reconstructed

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes encoding, decoding, or round-trip validation over input integers.
        """
        raw_integers = [int(x) for x in payload.get("integers", [])]
        raw_gaps = [int(x) for x in payload.get("gaps", [])]
        block_size = payload.get("block_size")

        encoded_data = None
        decoded_data = None

        if raw_integers:
            encoded_data = self.encode(raw_integers, block_size=int(block_size) if block_size else None)
            decoded_data = self.decode(encoded_data["gaps"])
        elif raw_gaps:
            decoded_data = self.decode(raw_gaps)

        return {
            "algorithm": "ALGO-SRCH-60",
            "encoded": encoded_data,
            "decoded": decoded_data,
            "round_trip_valid": (raw_integers == decoded_data) if raw_integers and decoded_data else None
        }
