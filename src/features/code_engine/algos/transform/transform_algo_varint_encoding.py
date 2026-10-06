"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VARINT & LEB128 ENCODING (ALGO-TRFM-03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Variable-Byte (Varint / LEB128) encoding is a binary serialization transformation
   that encodes 64-bit integers using 1 to 10 bytes depending on numerical magnitude.
   Includes ZigZag mapping to efficiently compress signed integers.

2. ARCHITECTURAL ROLE:
   Transform & Serialization role (Layer 1). Compacts posting list integers
   and frequency counters into minimal byte payloads.

3. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) per integer (max 10 loop iterations).
   - Space Complexity: O(N) encoded byte array.
   - Zero-Inline-Comment Doctrine: Code body is 100% comment-free.

4. EXECUTION FLOW:
   a. ZigZag encode signed integers to preserve small magnitudes.
   b. Emit 7-bit chunks with MSB continuation flag set until value < 128.
   c. Inverse decoding shifts 7-bit chunks into reconstructed integer.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class TransformAlgoVarintEncoding:
    """
    --- contract:
      id: ALGO-TRFM-03
      name: TransformAlgoVarintEncoding
      version: 1.0.0
      category: transform
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
        - compression.varint
        - encoding.leb128
        - zigzag.mapping
      input_schema:
        integers: list[int]
        signed: bool
      output_schema:
        encoded_bytes: list[int]
        total_bytes: int
    ---
    """

    def zigzag_encode(self, n: int) -> int:
        return (n << 1) ^ (n >> 63)

    def zigzag_decode(self, z: int) -> int:
        return (z >> 1) ^ -(z & 1)

    def encode_unsigned(self, value: int) -> List[int]:
        val = max(0, value)
        bytes_out: List[int] = []
        while val >= 0x80:
            bytes_out.append((val & 0x7F) | 0x80)
            val >>= 7
        bytes_out.append(val & 0x7F)
        return bytes_out

    def decode_unsigned(self, byte_stream: List[int]) -> Tuple[int, int]:
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
        encoded_stream: List[int] = []
        for val in integers:
            target = self.zigzag_encode(val) if signed else val
            encoded_stream.extend(self.encode_unsigned(target))
        return encoded_stream

    def decode_list(self, byte_stream: List[int], signed: bool = False) -> List[int]:
        decoded: List[int] = []
        cursor = 0
        stream_len = len(byte_stream)
        while cursor < stream_len:
            val, consumed = self.decode_unsigned(byte_stream[cursor:])
            cursor += consumed
            decoded.append(self.zigzag_decode(val) if signed else val)
        return decoded

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        integers = [int(x) for x in payload.get("integers", [])]
        raw_bytes = [int(x) for x in payload.get("bytes", [])]
        signed = bool(payload.get("signed", False))

        encoded = None
        decoded = None

        if integers:
            encoded = self.encode_list(integers, signed=signed)
        if raw_bytes:
            decoded = self.decode_list(raw_bytes, signed=signed)

        return {
            "status": "success",
            "encoded_bytes": encoded,
            "decoded_integers": decoded,
            "byte_count": len(encoded) if encoded else 0,
        }


SearchEngineVarintEncodingAlgo = TransformAlgoVarintEncoding
