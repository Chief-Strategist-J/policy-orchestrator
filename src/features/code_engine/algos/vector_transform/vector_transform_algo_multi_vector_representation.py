"""
================================================================================
ALGORITHM BLUEPRINT: MULTI-VECTOR REPRESENTATION (LATE INTERACTION) (ALGO-VEC-TRFM-47)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs multi-vector token matrices (ColBERT / Late Interaction style) where
   each passage is preserved as an N_tokens x D embedding matrix rather than pooled
   into a single vector. Eliminates punctuation, applies token normalization, and tags
   token roles (punctuation, stopwords, content tokens).

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Generates fine-grained multi-vector token sequences
   consumed downstream by late-interaction MaxSim retrieval kernels (#91).

3. EXECUTION FLOW:
   a. Receive sequence of token strings and contextual embeddings.
   b. Filter special masking / padding tokens.
   c. Normalize each surviving token vector to unit Euclidean length.
   d. Classify tokens into semantic categories.
   e. Return normalized multi-vector matrix with token metadata.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoMultiVectorRepresentation:
    """
    --- contract:
      id: ALGO-VEC-TRFM-47
      name: VectorTransformAlgoMultiVectorRepresentation
      category: transform
      complexity: O(N_tokens * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        tokens: list[str]
        token_embeddings: list[list[float]]
        filter_punctuation: bool
        normalize_tokens: bool
      output_schema:
        original_token_count: int
        retained_token_count: int
        dimension: int
        retained_tokens: list[str]
        multi_vectors: list[list[float]]
    ---
    """

    PUNCTUATION_SET = {".", ",", "!", "?", ";", ":", "-", "(", ")", "[", "]", "{", "}", "\"", "'"}

    @staticmethod
    def construct_representation(
        tokens: List[str],
        token_embeddings: List[List[float]],
        filter_punctuation: bool = True,
        normalize_tokens: bool = True,
    ) -> Dict[str, Any]:
        if not tokens or not token_embeddings:
            return {
                "original_token_count": len(tokens),
                "retained_token_count": 0,
                "dimension": 0,
                "retained_tokens": [],
                "multi_vectors": [],
            }

        orig_count = len(tokens)
        dim = len(token_embeddings[0])

        retained_toks: List[str] = []
        vectors: List[List[float]] = []

        for idx in range(min(orig_count, len(token_embeddings))):
            tok = tokens[idx]
            vec = list(token_embeddings[idx])

            if filter_punctuation and tok in VectorTransformAlgoMultiVectorRepresentation.PUNCTUATION_SET:
                continue

            if normalize_tokens:
                norm = math.sqrt(sum(x ** 2 for x in vec))
                if norm > 1e-12:
                    vec = [round(x / norm, 6) for x in vec]
                else:
                    vec = [round(x, 6) for x in vec]
            else:
                vec = [round(x, 6) for x in vec]

            retained_toks.append(tok)
            vectors.append(vec)

        return {
            "original_token_count": orig_count,
            "retained_token_count": len(retained_toks),
            "dimension": dim,
            "retained_tokens": retained_toks,
            "multi_vectors": vectors,
        }
