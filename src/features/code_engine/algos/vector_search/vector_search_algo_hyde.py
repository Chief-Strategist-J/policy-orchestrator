"""
================================================================================
ALGORITHM BLUEPRINT: HYDE (HYPOTHETICAL DOCUMENT EMBEDDINGS) (ALGO-VEC-SRCH-97)
================================================================================

HyDE (Hypothetical Document Embeddings) uses a generative model to synthesize one
or more hypothetical documents answering the user query. The hypothetical documents
are embedded, and their vector centroid is blended with the original query vector.
Because hypothetical documents live in the document embedding space rather than the
query space, semantic matching bypasses vocabulary mismatch and asymmetric length bias.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoHyDE:
    """
    --- contract:
      id: ALGO-VEC-SRCH-97
      name: VectorSearchAlgoHyDE
      category: vector
      complexity: O(H * D + N * D + N log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        corpus_vectors: list[list[float]]
        query_vector: list[float]
        hypothetical_vectors: list[list[float]]
        query_weight: float
        k: int
      output_schema:
        hypothetical_count: int
        query_weight: float
        blended_vector_norm: float
        matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _normalize(vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x ** 2 for x in vec))
        return [x / norm for x in vec] if norm > 1e-12 else vec

    @staticmethod
    def search_hyde(
        corpus_vectors: List[List[float]],
        query_vector: List[float],
        hypothetical_vectors: List[List[float]],
        query_weight: float = 0.3,
        k: int = 5,
    ) -> Dict[str, Any]:
        if not corpus_vectors or not query_vector:
            return {
                "hypothetical_count": len(hypothetical_vectors),
                "query_weight": query_weight,
                "blended_vector_norm": 0.0,
                "matches": [],
            }

        dim = len(query_vector)

        if hypothetical_vectors:
            hyp_centroid = [0.0] * dim
            for h_vec in hypothetical_vectors:
                for d in range(min(dim, len(h_vec))):
                    hyp_centroid[d] += h_vec[d]
            h_len = len(hypothetical_vectors)
            hyp_centroid = [x / h_len for x in hyp_centroid]

            blended = [
                query_weight * query_vector[d] + (1.0 - query_weight) * hyp_centroid[d]
                for d in range(dim)
            ]
        else:
            blended = list(query_vector)

        norm_blended = VectorSearchAlgoHyDE._normalize(blended)
        blended_norm_val = math.sqrt(sum(x ** 2 for x in blended))

        scores: List[Dict[str, Any]] = []
        for idx, doc_vec in enumerate(corpus_vectors):
            dot = sum(norm_blended[d] * doc_vec[d] for d in range(min(dim, len(doc_vec))))
            scores.append({"id": idx, "similarity": round(dot, 6)})

        scores.sort(key=lambda x: x["similarity"], reverse=True)

        return {
            "hypothetical_count": len(hypothetical_vectors),
            "query_weight": query_weight,
            "blended_vector_norm": round(blended_norm_val, 6),
            "matches": scores[:k],
        }
