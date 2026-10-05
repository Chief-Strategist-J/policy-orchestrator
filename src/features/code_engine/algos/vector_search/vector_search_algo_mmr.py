"""
================================================================================
ALGORITHM BLUEPRINT: MAXIMAL MARGINAL RELEVANCE (MMR) (ALGO-VEC-SRCH-89)
================================================================================

Maximal Marginal Relevance (MMR) iteratively selects candidates to optimize the
trade-off between query relevance and result diversity. At each step:
d* = argmax_{d ∈ R \\ S} [ λ · Sim(d, q) − (1 − λ) · max_{s ∈ S} Sim(d, s) ],
where S is the set of already selected items, suppressing redundancy and near-duplicate
documents in retrieval results.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoMMR:
    """
    --- contract:
      id: ALGO-VEC-SRCH-89
      name: MaximalMarginalRelevance
      category: vector
      complexity: O(k * |candidates| * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        candidate_vectors: list[list[float]]
        candidate_ids: list[any]
        query_vector: list[float]
        lambda_mult: float
        k: int
      output_schema:
        requested_k: int
        lambda_mult: float
        selected: list[dict[str, any]]
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
    def rerank(
        candidate_vectors: List[List[float]],
        candidate_ids: List[Any],
        query_vector: List[float],
        lambda_mult: float = 0.5,
        k: int = 5,
    ) -> Dict[str, Any]:
        if not candidate_vectors or not query_vector:
            return {"requested_k": k, "lambda_mult": lambda_mult, "selected": []}

        n = len(candidate_vectors)
        if len(candidate_ids) != n:
            candidate_ids = list(range(n))

        query_sims = [
            VectorSearchAlgoMMR._cosine_similarity(candidate_vectors[i], query_vector)
            for i in range(n)
        ]

        selected_indices: List[int] = []
        unselected_indices = list(range(n))

        target_k = min(k, n)
        while len(selected_indices) < target_k:
            best_score = -float("inf")
            best_idx = -1

            for u in unselected_indices:
                q_sim = query_sims[u]
                if not selected_indices:
                    mmr_score = q_sim
                else:
                    max_inter_sim = max(
                        VectorSearchAlgoMMR._cosine_similarity(
                            candidate_vectors[u], candidate_vectors[s]
                        )
                        for s in selected_indices
                    )
                    mmr_score = lambda_mult * q_sim - (1.0 - lambda_mult) * max_inter_sim

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = u

            if best_idx == -1:
                break

            selected_indices.append(best_idx)
            unselected_indices.remove(best_idx)

        results = [
            {
                "id": candidate_ids[idx],
                "query_similarity": round(query_sims[idx], 6),
                "selection_order": step + 1,
            }
            for step, idx in enumerate(selected_indices)
        ]

        return {
            "requested_k": k,
            "lambda_mult": lambda_mult,
            "selected": results,
        }
