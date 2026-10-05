"""
================================================================================
ALGORITHM BLUEPRINT: AUTOENCODER COMPRESSION (ALGO-VEC-TRFM-26)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Compresses continuous vector embeddings through a non-linear bottleneck autoencoder:
   Encoder: z = GeLU(W_enc · x + b_enc).
   Decoder: x_hat = W_dec · z + b_dec.
   Measures mean squared reconstruction error and produces non-linear compressed codes.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Captures non-linear manifold correlations beyond linear
   PCA capabilities for dense vector corpus compression.

3. EXECUTION FLOW:
   a. Check input vector dimensions and bottleneck configuration.
   b. Apply encoder matrix multiplication and non-linear activation (GeLU/ReLU).
   c. Apply decoder reconstruction.
   d. Compute MSE reconstruction error per vector.
   e. Return bottleneck codes z and reconstruction fidelity statistics.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoAutoencoderCompression:
    """
    --- contract:
      id: ALGO-VEC-TRFM-26
      name: VectorTransformAlgoAutoencoderCompression
      category: transform
      complexity: O(N * D * bottleneck_dim)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        bottleneck_dim: int
        encoder_weights: list[list[float]]
        decoder_weights: list[list[float]]
      output_schema:
        total_vectors: int
        input_dim: int
        bottleneck_dim: int
        mean_reconstruction_error: float
        compressed_codes: list[list[float]]
    ---
    """

    @staticmethod
    def _gelu(x: float) -> float:
        return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * (x ** 3))))

    @staticmethod
    def encode_decode(
        vectors: List[List[float]],
        bottleneck_dim: int = 8,
        encoder_weights: Optional[List[List[float]]] = None,
        decoder_weights: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "input_dim": 0,
                "bottleneck_dim": bottleneck_dim,
                "mean_reconstruction_error": 0.0,
                "compressed_codes": [],
            }

        n = len(vectors)
        d = len(vectors[0])
        b_dim = bottleneck_dim

        if encoder_weights is None:
            encoder_weights = [
                [math.sin((r + 1) * (c + 1) * 0.1) * 0.1 for c in range(d)]
                for r in range(b_dim)
            ]
        if decoder_weights is None:
            decoder_weights = [
                [math.cos((r + 1) * (c + 1) * 0.1) * 0.1 for c in range(b_dim)]
                for r in range(d)
            ]

        codes: List[List[float]] = []
        errors: List[float] = []

        for v in vectors:
            z: List[float] = []
            for r in range(b_dim):
                linear = sum(encoder_weights[r][c] * v[c] for c in range(min(d, len(encoder_weights[r]))))
                z.append(VectorTransformAlgoAutoencoderCompression._gelu(linear))
            codes.append([round(x, 6) for x in z])

            recon: List[float] = []
            for r in range(d):
                val = sum(decoder_weights[r][c] * z[c] for c in range(min(b_dim, len(decoder_weights[r]))))
                recon.append(val)

            mse = sum((v[i] - recon[i]) ** 2 for i in range(d)) / max(1, d)
            errors.append(mse)

        avg_error = sum(errors) / max(1, len(errors))

        return {
            "total_vectors": n,
            "input_dim": d,
            "bottleneck_dim": b_dim,
            "mean_reconstruction_error": round(avg_error, 6),
            "compressed_codes": codes,
        }
