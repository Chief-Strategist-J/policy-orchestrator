"""
================================================================================
ALGORITHM BLUEPRINT: MULTI-QUERY EXPANSION (ALGO-VEC-SRCH-92)
================================================================================

Multi-query expansion generates multiple diverse semantic reformulations of an
initial query (e.g. sub-questions, hyponyms, step decompositions) and retrieves
candidates across each query vector. Scores from individual query searches are
aggregated via max-pooling or average fusion to cover distinct facets of ambiguous
or multi-intent user prompts.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoMultiQueryExpansion:
    """
    --- contract:
      id: ALGO-VEC-SRCH-92
      name: VectorSearchAlgoMultiQueryExpansion
      category: vector
      complexity: O(Q_exp * N * D + N log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        expanded_queries: list[list[float]]
        aggregation: str
        k: int
      output_schema:
        total_vectors: int
        query_variants_count: int
        aggregation: str
        matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dim = min(len(a), len(b))
        if dim == 0:
            return 0.0
        dot = sum(a[i] * b[i] for i in range(dim))
        norm_a = math.sqrt(sum(a[i] ** 2 for i in range(dim)))
        norm_b = math.sqrt(sum(b[i] ** 2 for i in range(dim)))
        denom = norm_a * norm_b
        return dot / denom if denom > 1e-12 else 0.0

    @staticmethod
    def search_expanded(
        vectors: List[List[float]],
        expanded_queries: List[List[float]],
        aggregation: str = "max",
        k: int = 5,
    ) -> Dict[str, Any]:
        if not vectors or not expanded_queries:
            return {
                "total_vectors": len(vectors),
                "query_variants_count": len(expanded_queries),
                "aggregation": aggregation,
                "matches": [],
            }

        scores_by_doc: Dict[int, List[float]] = {i: [] for i in range(len(vectors))}

        for q_vec in expanded_queries:
            for doc_idx, doc_vec in enumerate(vectors):
                sim = VectorSearchAlgoMultiQueryExpansion._cosine_similarity(q_vec, doc_vec)
                scores_by_doc[doc_idx].append(sim)

        aggregated: List[Dict[str, Any]] = []
        for doc_idx, sim_list in scores_by_doc.items():
            if aggregation == "mean":
                agg_score = sum(sim_list) / len(sim_list)
            else:
                agg_score = max(sim_list)

            aggregated.append({
                "id": doc_idx,
                "aggregated_score": round(agg_score, 6),
                "per_query_scores": [round(s, 4) for s in sim_list],
            })

        aggregated.sort(key=lambda x: x["aggregated_score"], reverse=True)

        return {
            "total_vectors": len(vectors),
            "query_variants_count": len(expanded_queries),
            "aggregation": aggregation,
            "matches": aggregated[:k],
        }
