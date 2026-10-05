"""
================================================================================
ALGORITHM BLUEPRINT: MULTI-VECTOR (MAXSIM) RETRIEVAL (ALGO-VEC-SRCH-91)
================================================================================

Multi-vector late-interaction retrieval (ColBERT style) represents queries and
documents as multi-token embedding matrices rather than single vectors. The score
is computed via token-level maximum similarity summation:
Score(Q, D) = Σ_{q ∈ Q} max_{d ∈ D} (q · d),
enabling fine-grained token-level cross-matching without requiring full cross-encoders.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoMaxSim:
    """
    --- contract:
      id: ALGO-VEC-SRCH-91
      name: ColBERTMaxSim
      category: vector
      complexity: O(N * |Q| * |D| * d_token)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        document_token_vectors: list[list[list[float]]]
        query_token_vectors: list[list[float]]
        k: int
      output_schema:
        total_documents: int
        query_tokens_count: int
        matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _dot(a: List[float], b: List[float]) -> float:
        return sum(a[i] * b[i] for i in range(min(len(a), len(b))))

    @staticmethod
    def compute_maxsim(
        document_token_vectors: List[List[List[float]]],
        query_token_vectors: List[List[float]],
        k: int = 5,
    ) -> Dict[str, Any]:
        if not document_token_vectors or not query_token_vectors:
            return {
                "total_documents": len(document_token_vectors),
                "query_tokens_count": len(query_token_vectors),
                "matches": [],
            }

        scores: List[Dict[str, Any]] = []

        for doc_idx, doc_tokens in enumerate(document_token_vectors):
            if not doc_tokens:
                continue

            doc_score = 0.0
            token_alignments: List[float] = []

            for q_vec in query_token_vectors:
                best_sim = max(
                    VectorSearchAlgoMaxSim._dot(q_vec, d_vec) for d_vec in doc_tokens
                )
                doc_score += best_sim
                token_alignments.append(round(best_sim, 4))

            scores.append({
                "id": doc_idx,
                "maxsim_score": round(doc_score, 6),
                "token_alignments": token_alignments,
            })

        scores.sort(key=lambda x: x["maxsim_score"], reverse=True)

        return {
            "total_documents": len(document_token_vectors),
            "query_tokens_count": len(query_token_vectors),
            "matches": scores[:k],
        }
