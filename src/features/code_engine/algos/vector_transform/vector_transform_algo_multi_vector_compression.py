"""
================================================================================
ALGORITHM BLUEPRINT: MULTI-VECTOR COMPRESSION (PLAID RESIDUALS) (ALGO-VEC-TRFM-48)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Compresses multi-vector token embedding matrices (ColBERT style) using PLAID-style
   centroid clustering and low-bit residual quantization (Santhanam et al., 2022).
   Assigns each token vector to its nearest cluster centroid and quantizes the residual
   offset to 1 or 2 bits, slashing multi-vector memory footprints by 8x-16x.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Makes multi-vector late-interaction retrieval feasible
   on billion-scale corpora without gigabytes of RAM overhead per million tokens.

3. EXECUTION FLOW:
   a. For each token vector in the multi-vector matrix, identify the closest centroid.
   b. Compute residual offset r = x - centroid.
   c. Quantize residual components to signed 1-bit or 2-bit codes.
   d. Pack centroid IDs and residual bitmasks.
   e. Return compressed representation with compression ratio metrics.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoMultiVectorCompression:
    """
    --- contract:
      id: ALGO-VEC-TRFM-48
      name: VectorTransformAlgoMultiVectorCompression
      category: transform
      complexity: O(N_tokens * K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_vectors: list[list[float]]
        centroids: list[list[float]]
        bits_per_dim: int
      output_schema:
        total_tokens: int
        dimension: int
        centroid_indices: list[int]
        compressed_residuals: list[list[int]]
        compression_ratio: float
    ---
    """

    @staticmethod
    def compress_multi_vector(
        token_vectors: List[List[float]],
        centroids: Optional[List[List[float]]] = None,
        bits_per_dim: int = 1,
    ) -> Dict[str, Any]:
        if not token_vectors:
            return {
                "total_tokens": 0,
                "dimension": 0,
                "centroid_indices": [],
                "compressed_residuals": [],
                "compression_ratio": 1.0,
            }

        n_toks = len(token_vectors)
        dim = len(token_vectors[0])

        if centroids is None:
            centroids = [
                [math.sin((k + 1) * (d + 1) * 0.1) * 0.5 for d in range(dim)]
                for k in range(8)
            ]

        centroid_ids: List[int] = []
        quantized_residuals: List[List[int]] = []

        for vec in token_vectors:
            best_idx = 0
            best_dist = float("inf")

            for c_idx, c in enumerate(centroids):
                dist = sum((vec[j] - c[j]) ** 2 for j in range(min(dim, len(c))))
                if dist < best_dist:
                    best_dist = dist
                    best_idx = c_idx

            centroid_ids.append(best_idx)
            chosen_c = centroids[best_idx]
            res = [vec[j] - chosen_c[j] for j in range(dim)]

            if bits_per_dim == 1:
                q_res = [1 if r >= 0 else 0 for r in res]
            else:
                q_res = [max(-2, min(1, int(round(r * 4.0)))) for r in res]

            quantized_residuals.append(q_res)

        uncompressed_bytes = n_toks * dim * 4
        compressed_bytes = n_toks * (1 + (dim * bits_per_dim // 8))
        ratio = round(uncompressed_bytes / max(1, compressed_bytes), 2)

        return {
            "total_tokens": n_toks,
            "dimension": dim,
            "centroid_indices": centroid_ids,
            "compressed_residuals": quantized_residuals,
            "compression_ratio": ratio,
        }
