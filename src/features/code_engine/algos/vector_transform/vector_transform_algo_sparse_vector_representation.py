"""
================================================================================
ALGORITHM BLUEPRINT: SPARSE VECTOR REPRESENTATION (ALGO-VEC-TRFM-49)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs compact sparse vectors (dictionary / inverted list postings representation)
   from lexical terms or sparse neural models (BM25 / SPLADE). Encodes non-zero
   dimension indices and floating point weights with pruning thresholding and unit L2 scaling.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Standard interchange format for hybrid sparse-dense
   pipelines (#86) and inverted index builders.

3. EXECUTION FLOW:
   a. Collect term weights or sparse feature coordinates.
   b. Prune entries below minimum weight threshold.
   c. Normalize non-zero vector entries by L2 norm or max-weight.
   d. Sort sparse entries by feature ID for efficient two-pointer dot products.
   e. Return sparse indices, values, and density statistics.
================================================================================
"""

from typing import Any, Dict, List, Optional, Tuple
import math


class VectorTransformAlgoSparseVectorRepresentation:
    """
    --- contract:
      id: ALGO-VEC-TRFM-49
      name: VectorTransformAlgoSparseVectorRepresentation
      category: transform
      complexity: O(V_terms log V_terms)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        term_weights: dict[str, float]
        min_weight: float
        normalize_l2: bool
      output_schema:
        total_input_terms: int
        non_zero_elements: int
        sparsity_ratio: float
        sparse_indices: list[str]
        sparse_values: list[float]
    ---
    """

    @staticmethod
    def pack_sparse(
        term_weights: Dict[str, float],
        min_weight: float = 0.01,
        normalize_l2: bool = True,
    ) -> Dict[str, Any]:
        if not term_weights:
            return {
                "total_input_terms": 0,
                "non_zero_elements": 0,
                "sparsity_ratio": 1.0,
                "sparse_indices": [],
                "sparse_values": [],
            }

        filtered = [
            (term, float(w))
            for term, w in term_weights.items()
            if abs(float(w)) >= min_weight
        ]
        filtered.sort(key=lambda x: x[0])

        if normalize_l2 and filtered:
            norm = math.sqrt(sum(w ** 2 for _, w in filtered))
            if norm > 1e-12:
                filtered = [(t, round(w / norm, 6)) for t, w in filtered]
            else:
                filtered = [(t, round(w, 6)) for t, w in filtered]
        else:
            filtered = [(t, round(w, 6)) for t, w in filtered]

        indices = [t for t, _ in filtered]
        values = [w for _, w in filtered]

        sparsity = 1.0 - (len(filtered) / max(1, len(term_weights)))

        return {
            "total_input_terms": len(term_weights),
            "non_zero_elements": len(filtered),
            "sparsity_ratio": round(sparsity, 4),
            "sparse_indices": indices,
            "sparse_values": values,
        }
