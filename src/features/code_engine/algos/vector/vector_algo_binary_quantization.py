"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: 1-BIT BINARY QUANTIZATION (ALGO-VEC-07)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Converts float32 embedding vectors into compact bit vectors (1 bit per dimension,
   32x memory reduction). Distance comparison between binary vectors is computed
   via fast bitwise XOR + POPCNT (Hamming Distance), delivering 10x-50x speedups.

2. MATHEMATICAL FORMULA:
   Given centered/zero-mean vector v in R^D:
   bit_i = 1 if v_i > 0 else 0
   HammingDistance(b1, b2) = popcount(b1 XOR b2)
   CosineEstimate(b1, b2) = cos(pi * HammingDistance / D)

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Converts vectors to packed integer bit-arrays (bytes).
================================================================================
"""

from __future__ import annotations
import math
from typing import List, Tuple


class VectorAlgoBinaryQuantization:
    """
    ---
    contract:
      algo_id: ALGO-VEC-07
      name: VectorAlgoBinaryQuantization
      version: 1.0.0
      category: vector
      capability_tags: [vector, quantization, 1bit, binary_quantization, hamming_distance]
      inputs:
        type: object
        required: [vector]
        properties:
          vector:
            type: array
            items: {type: number}
      outputs:
        type: object
        required: [packed_bytes, bit_length]
        properties:
          packed_bytes:
            type: array
            items: {type: integer}
          bit_length: {type: integer}
      parameters:
        threshold: {type: number, default: 0.0}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: simd_vector
      complexity:
        time: O(D / 64)
        space: O(D / 8)
      preconditions:
        - len(vector) > 0
      postconditions:
        - bit_length == len(vector)
    ---
    """

    @staticmethod
    def quantize_to_bits(vector: List[float], threshold: float = 0.0) -> List[int]:
        return [1 if x > threshold else 0 for x in vector]

    @staticmethod
    def quantize_to_packed_bytes(vector: List[float], threshold: float = 0.0) -> bytes:
        bits = [1 if x > threshold else 0 for x in vector]
        byte_arr = bytearray((len(bits) + 7) // 8)
        for i, bit in enumerate(bits):
            if bit:
                byte_arr[i // 8] |= 1 << (i % 8)
        return bytes(byte_arr)

    @staticmethod
    def compute_hamming_distance(b1: bytes, b2: bytes) -> int:
        distance = 0
        min_len = min(len(b1), len(b2))
        for i in range(min_len):
            xor_byte = b1[i] ^ b2[i]
            distance += bin(xor_byte).count("1")
        if len(b1) != len(b2):
            distance += abs(len(b1) - len(b2)) * 8
        return distance

    @staticmethod
    def estimate_cosine_similarity(hamming_distance: int, total_bits: int) -> float:
        if total_bits <= 0:
            return 0.0
        ratio = min(1.0, max(0.0, hamming_distance / total_bits))
        return math.cos(math.pi * ratio)
