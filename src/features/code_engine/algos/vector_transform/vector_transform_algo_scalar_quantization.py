"""
================================================================================
ALGORITHM BLUEPRINT: SCALAR QUANTIZATION (INT8) (ALGO-VEC-TRFM-33)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Quantizes continuous 32-bit floating point vector elements into discrete 8-bit
   signed integers (INT8 in [-128, 127]) using uniform affine or symmetric scaling:
   q_i = clamp(round((x_i - min_val) / scale) + zero_point, -128, 127).
   Reduces vector memory bandwidth by 4x while enabling SIMD integer dot products.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Core in-memory index compression method preserving
   99%+ recall on normalized embeddings.

3. EXECUTION FLOW:
   a. Compute min and max element values across vector or batch.
   b. Determine scaling factor and zero-point offset.
   c. Map continuous floats to discrete INT8 integers.
   d. Calculate dequantization reconstruction error (MSE).
   e. Return quantized bytes and reconstruction parameters.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorTransformAlgoScalarQuantization:
    """
    --- contract:
      id: ALGO-VEC-TRFM-33
      name: VectorTransformAlgoScalarQuantization
      category: transform
      complexity: O(D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        bits: int
        symmetric: bool
      output_schema:
        dimension: int
        bits: int
        scale: float
        zero_point: int
        quantized_values: list[int]
        reconstruction_error_mse: float
    ---
    """

    @staticmethod
    def quantize(
        vector: List[float],
        bits: int = 8,
        symmetric: bool = True,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "bits": bits,
                "scale": 1.0,
                "zero_point": 0,
                "quantized_values": [],
                "reconstruction_error_mse": 0.0,
            }

        dim = len(vector)
        q_min = -(2 ** (bits - 1))
        q_max = (2 ** (bits - 1)) - 1

        if symmetric:
            max_abs = max(abs(x) for x in vector)
            if max_abs < 1e-12:
                max_abs = 1.0
            scale = max_abs / q_max
            zero_point = 0
        else:
            v_min = min(vector)
            v_max = max(vector)
            rng = v_max - v_min if v_max > v_min else 1.0
            scale = rng / (q_max - q_min)
            zero_point = int(round(-v_min / scale + q_min))

        quantized: List[int] = []
        reconstructed: List[float] = []

        for x in vector:
            q_val = int(round(x / scale)) + zero_point
            q_clamped = max(q_min, min(q_max, q_val))
            quantized.append(q_clamped)

            recon = (q_clamped - zero_point) * scale
            reconstructed.append(recon)

        mse = sum((vector[i] - reconstructed[i]) ** 2 for i in range(dim)) / max(1, dim)

        return {
            "dimension": dim,
            "bits": bits,
            "scale": round(scale, 6),
            "zero_point": zero_point,
            "quantized_values": quantized,
            "reconstruction_error_mse": round(mse, 6),
        }
