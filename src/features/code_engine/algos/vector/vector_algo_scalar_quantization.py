"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SCALAR QUANTIZATION SQ8 & SQ4 (ALGO-VEC-06)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Quantizes 32-bit floating point vector elements into discrete 8-bit signed/unsigned
   integers (SQ8, 4x memory reduction) or 4-bit nibbles (SQ4, 8x memory reduction),
   enabling ultra-compact cache representations with minimal cosine recall loss.

2. MATHEMATICAL FORMULA:
   Given min_val, max_val of vector x:
   scale = (max_val - min_val) / (2^bits - 1)
   q_i = round((x_i - min_val) / scale)
   dequantized_x_i = min_val + q_i * scale

3. ARCHITECTURAL INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Method bodies are 100% comment-free and pure.
   - Provides asymmetric scalar quantization with exact reconstruction scaling.
================================================================================
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class QuantizedVector:
    quantized_values: List[int]
    min_val: float
    max_val: float
    bits: int


class VectorAlgoScalarQuantization:
    """
    ---
    contract:
      algo_id: ALGO-VEC-06
      name: VectorAlgoScalarQuantization
      version: 1.0.0
      category: vector
      capability_tags: [vector, quantization, sq8, sq4, compression]
      inputs:
        type: object
        required: [vector]
        properties:
          vector:
            type: array
            items: {type: number}
      outputs:
        type: object
        required: [quantized_values, min_val, max_val, bits]
        properties:
          quantized_values:
            type: array
            items: {type: integer}
          min_val: {type: number}
          max_val: {type: number}
          bits: {type: integer}
      parameters:
        bits: {type: integer, default: 8}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: reversible
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(D)
        space: O(D)
      preconditions:
        - len(vector) > 0
        - bits in [4, 8]
      postconditions:
        - len(quantized_values) == len(vector)
    ---
    """

    @staticmethod
    def quantize_sq8(vector: List[float]) -> QuantizedVector:
        return VectorAlgoScalarQuantization.quantize(vector, bits=8)

    @staticmethod
    def quantize_sq4(vector: List[float]) -> QuantizedVector:
        return VectorAlgoScalarQuantization.quantize(vector, bits=4)

    @staticmethod
    def quantize(vector: List[float], bits: int = 8) -> QuantizedVector:
        if not vector:
            return QuantizedVector(quantized_values=[], min_val=0.0, max_val=0.0, bits=bits)
        if bits not in {4, 8}:
            raise ValueError(f"Scalar quantization currently supports bits in [4, 8], got {bits}")

        v_min = min(vector)
        v_max = max(vector)
        max_level = (1 << bits) - 1

        span = v_max - v_min
        if span < 1e-12:
            return QuantizedVector(
                quantized_values=[0] * len(vector),
                min_val=v_min,
                max_val=v_max,
                bits=bits,
            )

        inv_scale = max_level / span
        quantized = [
            max(0, min(max_level, int(round((x - v_min) * inv_scale))))
            for x in vector
        ]

        return QuantizedVector(
            quantized_values=quantized,
            min_val=v_min,
            max_val=v_max,
            bits=bits,
        )

    @staticmethod
    def dequantize(q_vec: QuantizedVector) -> List[float]:
        if not q_vec.quantized_values:
            return []
        max_level = (1 << q_vec.bits) - 1
        span = q_vec.max_val - q_vec.min_val
        if span < 1e-12 or max_level == 0:
            return [q_vec.min_val] * len(q_vec.quantized_values)

        scale = span / max_level
        return [q_vec.min_val + q * scale for q in q_vec.quantized_values]

    @staticmethod
    def to_qdrant_quantization_config(
        quantile: Optional[float] = 0.99,
        always_ram: bool = True,
    ) -> dict:
        config: dict = {
            "scalar": {
                "type": "int8",
                "always_ram": always_ram,
            }
        }
        if quantile is not None:
            config["scalar"]["quantile"] = quantile
        return config

    @staticmethod
    def to_qdrant_search_params(rescore: bool = True, oversampling: float = 2.0) -> dict:
        return {
            "quantization": {
                "ignore": False,
                "rescore": rescore,
                "oversampling": oversampling,
            }
        }

    @staticmethod
    def to_qdrant_point(
        point_id: Any,
        vector: List[float],
        payload: Optional[dict] = None,
    ) -> dict:
        return {
            "id": point_id,
            "vector": vector,
            "payload": payload or {},
        }
