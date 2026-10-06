"""
================================================================================
ALGORITHM BLUEPRINT: VARIABLE-BYTE (VARINT / LEB128 & ZIGZAG) ENCODING
================================================================================

1. OVERVIEW:
   Variable-Byte (Varint / LEB128) encoding is a binary serialization codec that
   stores integers using 1 to 10 bytes depending on magnitude. Each byte dedicates
   7 bits to numeric data and the most significant bit (MSB, bit 7) as a continuation
   flag (1 = more bytes follow, 0 = terminal byte). ZigZag mapping is used to compress
   signed integers efficiently.

2. MATHEMATICAL & BITWISE FORMULATION:
   - ZigZag Mapping:
       Signed n -> Unsigned z: z = (n << 1) ^ (n >> 63)
       Inverse: n = (z >> 1) ^ -(z & 1)
   - LEB128 Serialization:
       While z >= 0x80 (128):
           emit (z & 0x7F) | 0x80
           z >>= 7
       emit z & 0x7F
   - LEB128 Deserialization:
       shift = 0, result = 0
       for each byte b:
           result |= (b & 0x7F) << shift
           if (b & 0x80) == 0: break
           shift += 7

3. COMPLEXITY ANALYSIS:
   - Encode/Decode Time: O(1) per integer (max 10 iterations for 64-bit int).
   - Space Complexity:
       [0, 127] -> 1 byte (75% savings over 32-bit int)
       [128, 16383] -> 2 bytes (50% savings)
       [16384, 2097151] -> 3 bytes (25% savings).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments in function bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class SearchEngineVarintEncodingAlgo:
    """
    Implements LEB128 variable-length integer encoding and ZigZag signed transformation.
    """

    def zigzag_encode(self, n: int) -> int:
        """
        Maps signed integer to unsigned integer preserving small magnitude.
        """
        return (n << 1) ^ (n >> 63)

    def zigzag_decode(self, z: int) -> int:
        """
        Inverts unsigned ZigZag integer back to signed integer.
        """
        return (z >> 1) ^ -(z & 1)

    def encode_unsigned(self, value: int) -> List[int]:
        """
        Encodes a single unsigned non-negative integer into LEB128 byte sequence.
        """
        val = max(0, value)
        bytes_out: List[int] = []
        while val >= 0x80:
            bytes_out.append((val & 0x7F) | 0x80)
            val >>= 7
        bytes_out.append(val & 0x7F)
        return bytes_out

    def decode_unsigned(self, byte_stream: List[int]) -> Tuple[int, int]:
        """
        Decodes one LEB128 unsigned integer, returning (value, bytes_consumed).
        """
        result = 0
        shift = 0
        consumed = 0
        for b in byte_stream:
            consumed += 1
            result |= (b & 0x7F) << shift
            if (b & 0x80) == 0:
                break
            shift += 7
            if shift > 64:
                raise ValueError("Varint byte sequence overflow (exceeded 64-bit boundary)")
        return result, consumed

    def encode_list(self, integers: List[int], signed: bool = False) -> List[int]:
        """
        Encodes a list of integers into a continuous byte array.
        """
        encoded_stream: List[int] = []
        for val in integers:
            target = self.zigzag_encode(val) if signed else val
            encoded_stream.extend(self.encode_unsigned(target))
        return encoded_stream

    def decode_list(self, byte_stream: List[int], signed: bool = False) -> List[int]:
        """
        Decodes a continuous byte array into a list of integers.
        """
        results: List[int] = []
        idx = 0
        while idx < len(byte_stream):
            val, consumed = self.decode_unsigned(byte_stream[idx:])
            idx += consumed
            results.append(self.zigzag_decode(val) if signed else val)
        return results

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes Varint encoding, decoding, or stream validation.
        """
        integers = [int(x) for x in payload.get("integers", [])]
        raw_bytes = [int(b) for b in payload.get("bytes", [])]
        signed = bool(payload.get("signed", False))

        encoded_bytes: List[int] = []
        decoded_integers: List[int] = []

        if integers:
            encoded_bytes = self.encode_list(integers, signed=signed)
            decoded_integers = self.decode_list(encoded_bytes, signed=signed)
        elif raw_bytes:
            decoded_integers = self.decode_list(raw_bytes, signed=signed)

        original_size_bytes = len(integers) * 4 if integers else 0
        compressed_size_bytes = len(encoded_bytes) if encoded_bytes else len(raw_bytes)
        savings = round((1.0 - compressed_size_bytes / max(1, original_size_bytes)) * 100, 2) if original_size_bytes > 0 else 0.0

        return {
            "algorithm": "ALGO-SRCH-61",
            "signed_mode": signed,
            "encoded_bytes": encoded_bytes,
            "byte_count": compressed_size_bytes,
            "raw_32bit_bytes": original_size_bytes,
            "compression_savings_pct": savings,
            "decoded_integers": decoded_integers,
            "round_trip_valid": (integers == decoded_integers) if integers else None
        }
