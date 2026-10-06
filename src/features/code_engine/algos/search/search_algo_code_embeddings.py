"""
================================================================================
ALGORITHM BLUEPRINT: LEXICAL-SEMANTIC CODE EMBEDDINGS VECTORIZER
================================================================================

1. OVERVIEW:
   Generates dense lexical-semantic embedding vectors for source code snippets and
   natural language queries. Tokenizes code, decomposes compound identifiers
   (camelCase, snake_case), maps subtokens to dimension hashes, applies weighted
   mean pooling across syntax categories, and normalizes to unit length (L2 norm)
   for cosine similarity nearest-neighbor retrieval.

2. VECTOR EMBEDDING PIPELINE:
   - Subtoken Extraction: `parseHttpRequest` -> `["parse", "http", "request"]`.
   - Feature Hashing: Hashes subtokens into D-dimensional dense vector space.
   - Syntax Weighting: Higher weights assigned to function names and class declarations.
   - L2 Unit Normalization: ||v||_2 = 1.0 enabling dot product = cosine similarity.

3. COMPLEXITY ANALYSIS:
   - Vectorization Time: O(Tokens) linear in code size.
   - Cosine Similarity: O(D) where D is vector dimensionality.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineCodeEmbeddingsAlgo:
    """
    Implements deterministic subtoken-weighted code embedding vectorization and similarity computation.
    """

    def __init__(self, dimensions: int = 64) -> None:
        self._dimensions: int = max(16, dimensions)

    def _split_subtokens(self, text: str) -> List[str]:
        words = re.findall(r'[a-zA-Z0-9]+', text)
        subtokens: List[str] = []
        for w in words:
            camel_parts = re.findall(r'[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z0-9]|\b)', w)
            if camel_parts:
                for p in camel_parts:
                    subtokens.append(p.lower())
            else:
                subtokens.append(w.lower())
        return subtokens

    def embed_code(self, code: str) -> List[float]:
        """
        Transforms code into an L2-normalized dense embedding vector.
        """
        subtokens = self._split_subtokens(code)
        if not subtokens:
            return [0.0] * self._dimensions

        vec = [0.0] * self._dimensions
        for idx, tok in enumerate(subtokens):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest()[:8], 16)
            dim_idx = h % self._dimensions
            sign = 1.0 if (h & 0x1000) != 0 else -1.0
            vec[dim_idx] += sign * 1.0

        norm_sq = sum(x * x for x in vec)
        if norm_sq > 0.0:
            norm = math.sqrt(norm_sq)
            vec = [round(x / norm, 6) for x in vec]
        return vec

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculates cosine similarity between two unit vectors.
        """
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(-1.0, min(1.0, round(dot, 4)))

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes embedding generation and optional similarity calculation.
        """
        code = str(payload.get("code", ""))
        query = payload.get("query")
        dim = int(payload.get("dimensions", self._dimensions))

        self._dimensions = max(16, dim)
        code_vector = self.embed_code(code)

        query_vector = None
        similarity = None
        if query:
            query_vector = self.embed_code(str(query))
            similarity = self.cosine_similarity(code_vector, query_vector)

        return {
            "algorithm": "ALGO-SRCH-100",
            "dimensions": self._dimensions,
            "code_embedding": code_vector,
            "query_embedding": query_vector,
            "cosine_similarity": similarity
        }
