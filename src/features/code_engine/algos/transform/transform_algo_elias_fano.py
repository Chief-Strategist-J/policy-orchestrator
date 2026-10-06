"""
================================================================================
ALGORITHM BLUEPRINT: ELIAS-FANO QUASI-SUCCINCT ENCODING
================================================================================

1. OVERVIEW:
   Elias-Fano is a quasi-succinct representation of sorted non-decreasing integer
   sequences. Given N integers bounded by universe U, it encodes the sequence in
   N * (2 + ceil(log2(U / N))) bits, approaching the information-theoretic lower bound.
   Crucially, it supports O(1) random access by rank (`access(i)`) and sub-linear
   successor queries (`next_geq(x)`) without decompressing the list.

2. MATHEMATICAL FORMULATION:
   - Parameters:
       N = number of elements, U = upper bound universe (max(S) + 1).
       Low-bit width: L = max(0, int(floor(log2(U / N)))) if N > 0 else 0.
   - Low-Bits Array:
       For each x in S: low = x & ((1 << L) - 1). Packed into N * L bits.
   - High-Bits Unary Bitvector:
       For each x in S: high = x >> L.
       In bitvector H, write '0' high_delta times followed by a '1' bit.
       Total '1' bits = N, total '0' bits = floor(U / 2^L).
   - Access(i):
       high = select1(H, i) - i
       low = read_low_bits(i, L)
       return (high << L) | low
   - Next-GEQ(x):
       Target high = x >> L. Jump to unary bucket, scan to find first element >= x.

3. COMPLEXITY ANALYSIS:
   - Space: N * (2 + ceil(log2(U / N))) bits.
   - Access(i): O(1) with select support.
   - Next-GEQ(x): O(log(U/N) + bucket_size) with galloping / binary skip.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method/function bodies.
================================================================================
"""

import math
from typing import Dict, List, Any, Optional, Tuple


class TransformAlgoEliasFano:
    """
    --- contract:
      id: ALGO-TRFM-05
      name: TransformAlgoEliasFano
      version: 1.0.0
      category: transform
      complexity:
        time: O(N) encode, O(1) access
        space: O(N * (2 + ceil(log2(U / N)))) bits
      pure_function: true
      zero_inline_comments: true
      capability_tags:
        - compression.elias_fano
        - quasi_succinct.representation
        - posting_list.random_access
      input_schema:
        sorted_integers: list[int]
      output_schema:
        encoding_meta: dict
        decoded_values: list[int]
    ---
    """

    def __init__(self) -> None:
        self._n: int = 0
        self._u: int = 0
        self._l: int = 0
        self._low_bits: List[int] = []
        self._high_bits: List[int] = []
        self._ones_positions: List[int] = []

    def encode(self, sorted_integers: List[int]) -> Dict[str, Any]:
        if not sorted_integers:
            self._n = 0
            self._u = 0
            self._l = 0
            self._low_bits = []
            self._high_bits = []
            self._ones_positions = []
            return {"n": 0, "u": 0, "l": 0, "total_bits": 0}

        sorted_vals = sorted([max(0, int(x)) for x in sorted_integers])
        self._n = len(sorted_vals)
        self._u = max(sorted_vals) + 1

        self._l = max(0, int(math.floor(math.log2(self._u / self._n)))) if self._n > 0 else 0
        low_mask = (1 << self._l) - 1 if self._l > 0 else 0

        self._low_bits = []
        self._high_bits = []
        self._ones_positions = []

        last_high = 0
        curr_bit_pos = 0

        for idx, val in enumerate(sorted_vals):
            low_val = val & low_mask if self._l > 0 else 0
            self._low_bits.append(low_val)

            high_val = val >> self._l if self._l > 0 else val
            zeros_to_add = high_val - last_high
            for _ in range(zeros_to_add):
                self._high_bits.append(0)
                curr_bit_pos += 1

            self._high_bits.append(1)
            self._ones_positions.append(curr_bit_pos)
            curr_bit_pos += 1
            last_high = high_val

        total_bits = (self._n * self._l) + len(self._high_bits)
        return {
            "n": self._n,
            "u": self._u,
            "l_bits": self._l,
            "high_bits_len": len(self._high_bits),
            "total_bits": total_bits,
            "bits_per_int": round(total_bits / self._n, 2)
        }

    def access(self, index: int) -> int:
        if index < 0 or index >= self._n:
            raise IndexError("Index out of bounds in Elias-Fano sequence")

        bit_pos = self._ones_positions[index]
        high_val = bit_pos - index
        low_val = self._low_bits[index] if self._l > 0 else 0

        return (high_val << self._l) | low_val

    def decode_all(self) -> List[int]:
        return [self.access(i) for i in range(self._n)]

    def next_geq(self, target: int) -> Optional[Tuple[int, int]]:
        if self._n == 0:
            return None
        low = 0
        high = self._n - 1
        ans_idx = -1

        while low <= high:
            mid = (low + high) // 2
            val = self.access(mid)
            if val >= target:
                ans_idx = mid
                high = mid - 1
            else:
                low = mid + 1

        if ans_idx != -1:
            return ans_idx, self.access(ans_idx)
        return None

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        integers = [int(x) for x in payload.get("integers", [])]
        access_index = payload.get("access_index")
        target_geq = payload.get("next_geq")

        meta = self.encode(integers)
        decoded = self.decode_all() if self._n > 0 else []

        access_val = None
        if access_index is not None and 0 <= int(access_index) < self._n:
            access_val = self.access(int(access_index))

        next_val = None
        if target_geq is not None:
            next_val = self.next_geq(int(target_geq))

        return {
            "algorithm": "ALGO-SRCH-63",
            "encoding_meta": meta,
            "decoded_values": decoded,
            "access_result": {"index": access_index, "value": access_val} if access_index is not None else None,
            "next_geq_result": {"target": target_geq, "found": next_val} if target_geq is not None else None,
            "round_trip_valid": (sorted(integers) == decoded) if integers else True
        }


SearchEngineEliasFanoAlgo = TransformAlgoEliasFano
