"""
================================================================================
ALGORITHM BLUEPRINT: CLS POOLING (ALGO-VEC-TRFM-04)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Extracts the vector representation of the leading classification token ([CLS]
   at index 0) from the transformer final hidden states, optionally applying a
   linear projection or normalization step.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Required pooling operation for BERT/RoBERTa-style
   classifiers and sentence models trained explicitly with CLS target objectives.

3. EXECUTION FLOW:
   a. Check non-emptiness of sequence representations.
   b. Extract token embedding at index 0.
   c. Optionally apply projection matrix multiplication.
   d. Return final pooled dense representation.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoCLSPooling:
    """
    --- contract:
      id: ALGO-VEC-TRFM-04
      name: VectorTransformAlgoCLSPooling
      category: transform
      complexity: O(hidden_dim)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_embeddings: list[list[float]]
        projection_weights: list[list[float]]
        normalize_l2: bool
      output_schema:
        dimension: int
        cls_vector: list[float]
    ---
    """

    @staticmethod
    def pool(
        token_embeddings: List[List[float]],
        projection_weights: Optional[List[List[float]]] = None,
        normalize_l2: bool = True,
    ) -> Dict[str, Any]:
        if not token_embeddings or not token_embeddings[0]:
            return {"dimension": 0, "cls_vector": []}

        cls_raw = list(token_embeddings[0])

        if projection_weights:
            out_dim = len(projection_weights)
            in_dim = len(projection_weights[0])
            projected = []
            for r in range(out_dim):
                val = sum(
                    projection_weights[r][c] * cls_raw[c]
                    for c in range(min(in_dim, len(cls_raw)))
                )
                projected.append(val)
            cls_raw = projected

        if normalize_l2:
            norm = math.sqrt(sum(x ** 2 for x in cls_raw))
            if norm > 1e-12:
                cls_raw = [round(x / norm, 6) for x in cls_raw]
            else:
                cls_raw = [round(x, 6) for x in cls_raw]
        else:
            cls_raw = [round(x, 6) for x in cls_raw]

        return {
            "dimension": len(cls_raw),
            "cls_vector": cls_raw,
        }
