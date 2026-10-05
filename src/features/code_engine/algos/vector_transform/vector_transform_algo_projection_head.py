"""
================================================================================
ALGORITHM BLUEPRINT: LEARNED PROJECTION HEAD (ADAPTER) (ALGO-VEC-TRFM-29)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Projects embeddings through a lightweight learned adapter layer (e.g. 2-layer MLP
   with residual connection): y = LayerNorm(x + W_2 · GeLU(W_1 · x + b_1) + b_2).
   Adapts frozen foundation embeddings to specific downstream domains without
   modifying base model weights.

2. ARCHITECTURAL ROLE:
   Transformer & Operator role (Layer 1). Cost-effective domain adaptation preserving
   the global vector geometry while adjusting task-specific feature correlations.

3. EXECUTION FLOW:
   a. Check input vector and weight matrix dimensions.
   b. Apply layer 1 projection W_1 and non-linear GeLU activation.
   c. Apply layer 2 projection W_2.
   d. Add residual connection x (if dimensions match).
   e. Apply layer normalization and return adapted representation.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoProjectionHead:
    """
    --- contract:
      id: ALGO-VEC-TRFM-29
      name: VectorTransformAlgoProjectionHead
      category: transform
      complexity: O(D * H)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        w1: list[list[float]]
        b1: list[float]
        w2: list[list[float]]
        b2: list[float]
        use_residual: bool
      output_schema:
        input_dim: int
        output_dim: int
        projected_vector: list[float]
    ---
    """

    @staticmethod
    def _gelu(x: float) -> float:
        return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * (x ** 3))))

    @staticmethod
    def project(
        vector: List[float],
        w1: Optional[List[List[float]]] = None,
        b1: Optional[List[float]] = None,
        w2: Optional[List[List[float]]] = None,
        b2: Optional[List[float]] = None,
        use_residual: bool = True,
    ) -> Dict[str, Any]:
        if not vector:
            return {"input_dim": 0, "output_dim": 0, "projected_vector": []}

        d_in = len(vector)
        h_dim = d_in // 2 if d_in >= 4 else d_in
        d_out = d_in

        if w1 is None:
            w1 = [[math.sin((r + 1) * (c + 1) * 0.05) * 0.1 for c in range(d_in)] for r in range(h_dim)]
        if b1 is None:
            b1 = [0.0] * h_dim
        if w2 is None:
            w2 = [[math.cos((r + 1) * (c + 1) * 0.05) * 0.1 for c in range(h_dim)] for r in range(d_out)]
        if b2 is None:
            b2 = [0.0] * d_out

        h = []
        for r in range(len(w1)):
            linear = b1[r] + sum(w1[r][c] * vector[c] for c in range(min(d_in, len(w1[r]))))
            h.append(VectorTransformAlgoProjectionHead._gelu(linear))

        out = []
        for r in range(len(w2)):
            val = b2[r] + sum(w2[r][c] * h[c] for c in range(min(len(h), len(w2[r]))))
            if use_residual and r < d_in:
                val += vector[r]
            out.append(val)

        mean_v = sum(out) / len(out)
        var_v = sum((x - mean_v) ** 2 for x in out) / len(out)
        std_v = math.sqrt(var_v + 1e-5)
        normed = [round((x - mean_v) / std_v, 6) for x in out]

        return {
            "input_dim": d_in,
            "output_dim": len(normed),
            "projected_vector": normed,
        }
