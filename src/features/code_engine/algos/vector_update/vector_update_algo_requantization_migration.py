"""
================================================================================
ALGORITHM BLUEPRINT: REQUANTIZATION MIGRATION (ALGO-VEC-UPD-149)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Converts full-precision vectors into updated quantization formats (FP32 -> INT8/Scalar),
   computes reconstruction MSE error, and reports storage compression ratios.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoRequantizationMigration:
    """
    --- contract:
      id: ALGO-VEC-UPD-149
      name: VectorUpdateAlgoRequantizationMigration
      category: update
      complexity: O(N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        full_precision_vectors: list[list[float]]
        target_format: str
      output_schema:
        quantized_vectors: list[list[int]]
        mean_squared_error: float
        compression_ratio: float
    ---
    """

    @classmethod
    def requantize(
        cls,
        full_precision_vectors: List[List[float]],
        target_format: str = "INT8",
    ) -> Dict[str, Any]:
        quantized: List[List[int]] = []
        total_sq_err = 0.0
        total_elements = 0

        for vec in full_precision_vectors:
            q_row = []
            for val in vec:
                q_val = max(-128, min(127, int(round(val * 127.0))))
                dequant = q_val / 127.0
                total_sq_err += (val - dequant) ** 2
                total_elements += 1
                q_row.append(q_val)
            quantized.append(q_row)

        mse = total_sq_err / total_elements if total_elements > 0 else 0.0
        comp_ratio = 4.0 if target_format == "INT8" else 1.0

        return {
            "quantized_vectors": quantized,
            "mean_squared_error": round(mse, 6),
            "compression_ratio": comp_ratio,
            "vector_count": len(quantized),
        }
