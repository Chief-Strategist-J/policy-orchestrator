"""
================================================================================
ALGORITHM BLUEPRINT: PForDelta (PATCHED FRAME-OF-REFERENCE BIT PACKING)
================================================================================

1. OVERVIEW:
   PForDelta (Patched Frame-of-Reference / Patched FastPFOR) is a high-throughput
   SIMD-friendly compression codec for integer lists. For each block of numbers
   (e.g., 64 or 128 elements), it determines the optimal bit-width B that covers
   the vast majority (e.g. >= 90%) of values. Values fitting in B bits are packed
   contiguously, while rare outlier values (exceptions) are stored in an auxiliary
   exception buffer with their relative positions.

2. ALGORITHMIC STEPS:
   - Bit-Width Selection:
       Find minimal B in [1..32] such that at least (1.0 - exception_threshold) of
       values satisfy x < 2^B.
   - Bit Packing:
       Pack the low B bits of each integer into a continuous bitstream.
   - Exception Patching:
       For values >= 2^B, write 0 (or masked value) into the packed block, and append
       (block_index, original_value) to the exception list.
   - Decoding / Unpacking:
       1. Unpack all N values using B bits per entry.
       2. Iterate over the exception list and patch the original values back at their
          exact block indices.

3. COMPLEXITY ANALYSIS:
   - Encoding Time: O(N) where N is block size.
   - Decoding Time: O(N) with vectorized word unpacking.
   - Compression Ratio: High throughput (> 1-2 GB/s decompression) with high density.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside function bodies.
================================================================================
"""

import math
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineBitPackingPforDeltaAlgo:
    """
    Implements PForDelta patched bit packing and unpacking over integer blocks.
    """

    def __init__(self, block_size: int = 64, exception_ratio: float = 0.10) -> None:
        self._block_size: int = max(8, block_size)
        self._exception_ratio: float = exception_ratio

    def _choose_best_bit_width(self, values: List[int]) -> int:
        if not values:
            return 1
        sorted_vals = sorted(values)
        cutoff_idx = int(len(values) * (1.0 - self._exception_ratio))
        cutoff_idx = max(0, min(len(values) - 1, cutoff_idx))
        target_max = sorted_vals[cutoff_idx]

        if target_max <= 0:
            return 1
        return max(1, math.ceil(math.log2(target_max + 1)))

    def compress_block(self, values: List[int]) -> Dict[str, Any]:
        """
        Compresses a single block using PForDelta bit-packing and exception list.
        """
        if not values:
            return {"bit_width": 0, "packed_words": [], "exceptions": [], "count": 0}

        b = self._choose_best_bit_width(values)
        max_regular_val = (1 << b) - 1

        exceptions: List[Dict[str, Any]] = []
        regular_values: List[int] = []

        for i, val in enumerate(values):
            if val <= max_regular_val:
                regular_values.append(val)
            else:
                regular_values.append(val & max_regular_val)
                exceptions.append({"index": i, "value": val})

        packed_bits: int = 0
        bit_pos: int = 0
        words: List[int] = []
        for val in regular_values:
            packed_bits |= (val << bit_pos)
            bit_pos += b
            while bit_pos >= 32:
                words.append(packed_bits & 0xFFFFFFFF)
                packed_bits >>= 32
                bit_pos -= 32

        if bit_pos > 0:
            words.append(packed_bits & 0xFFFFFFFF)

        return {
            "bit_width": b,
            "packed_words": words,
            "exceptions": exceptions,
            "count": len(values)
        }

    def decompress_block(self, block: Dict[str, Any]) -> List[int]:
        """
        Decompresses a PForDelta block by unpacking bits and patching exceptions.
        """
        b = int(block.get("bit_width", 0))
        words = block.get("packed_words", [])
        exceptions = block.get("exceptions", [])
        count = int(block.get("count", 0))

        if count == 0:
            return []

        mask = (1 << b) - 1
        unpacked: List[int] = []

        bit_stream = 0
        bits_available = 0
        word_idx = 0

        for _ in range(count):
            while bits_available < b and word_idx < len(words):
                bit_stream |= (words[word_idx] << bits_available)
                bits_available += 32
                word_idx += 1

            unpacked.append(bit_stream & mask)
            bit_stream >>= b
            bits_available -= b

        for exc in exceptions:
            idx = int(exc["index"])
            val = int(exc["value"])
            if 0 <= idx < len(unpacked):
                unpacked[idx] = val

        return unpacked

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes PForDelta block compression, decompression, and efficiency metrics.
        """
        values = [int(x) for x in payload.get("values", [])]
        block_size = int(payload.get("block_size", self._block_size))

        self._block_size = max(8, block_size)
        compressed_blocks: List[Dict[str, Any]] = []
        decompressed_all: List[int] = []

        for i in range(0, len(values), self._block_size):
            chunk = values[i:i + self._block_size]
            blk = self.compress_block(chunk)
            compressed_blocks.append(blk)
            decompressed_all.extend(self.decompress_block(blk))

        raw_bytes = len(values) * 4
        compressed_bytes = sum(len(b["packed_words"]) * 4 + len(b["exceptions"]) * 8 + 4 for b in compressed_blocks)
        savings = round((1.0 - compressed_bytes / max(1, raw_bytes)) * 100, 2) if raw_bytes > 0 else 0.0

        return {
            "algorithm": "ALGO-SRCH-62",
            "total_integers": len(values),
            "block_size": self._block_size,
            "block_count": len(compressed_blocks),
            "compressed_bytes": compressed_bytes,
            "raw_32bit_bytes": raw_bytes,
            "compression_savings_pct": savings,
            "compressed_blocks": compressed_blocks,
            "decompressed_values": decompressed_all,
            "round_trip_valid": (values == decompressed_all)
        }
