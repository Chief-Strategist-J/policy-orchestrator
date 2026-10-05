"""
================================================================================
ALGORITHM BLUEPRINT: HUBNESS REDUCTION (CSLS) (ALGO-VEC-TRFM-21)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Mitigates the "hubness problem" in high-dimensional vector spaces (where certain
   popular points become nearest neighbors to unnaturally many queries) using
   Cross-Domain Similarity Local Scaling (CSLS):
   CSLS(q, x) = 2 · cos(q, x) - r_K(q) - r_K(x),
   where r_K(·) is the mean cosine similarity to the point's K nearest neighbors.

2. ARCHITECTURAL ROLE:
   Retriever & Transformer role (Layer 1). Penalizes hub vectors and boosts isolated
   points, yielding substantially higher cross-lingual and cross-modal retrieval recall.

3. EXECUTION FLOW:
   a. Compute pairwise cosine similarity matrix between query batch Q and candidate batch X.
   b. Compute r_K(q) = mean cosine similarity of q to its K nearest neighbors in X.
   c. Compute r_K(x) = mean cosine similarity of x to its K nearest neighbors in Q.
   d. Compute CSLS(q, x) = 2 · cos(q, x) - r_K(q) - r_K(x).
   e. Rank candidates by CSLS score.
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoCSLSHubnessReduction:
    """
    --- contract:
      id: ALGO-VEC-TRFM-21
      name: VectorTransformAlgoCSLSHubnessReduction
      category: transform
      complexity: O(|Q| * |X| * D + |Q| * |X| log K)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query_vectors: list[list[float]]
        candidate_vectors: list[list[float]]
        candidate_ids: list[any]
        k_neighbors: int
      output_schema:
        total_queries: int
        total_candidates: int
        k_neighbors: int
        csls_rankings: list[list[dict[str, any]]]
    ---
    """

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x ** 2 for x in a))
        norm_b = math.sqrt(sum(y ** 2 for y in b))
        denom = norm_a * norm_b
        return dot / denom if denom > 1e-12 else 0.0

    @staticmethod
    def compute_csls(
        query_vectors: List[List[float]],
        candidate_vectors: List[List[float]],
        candidate_ids: Optional[List[Any]] = None,
        k_neighbors: int = 4,
    ) -> Dict[str, Any]:
        if not query_vectors or not candidate_vectors:
            return {
                "total_queries": len(query_vectors),
                "total_candidates": len(candidate_vectors),
                "k_neighbors": k_neighbors,
                "csls_rankings": [],
            }

        n_q = len(query_vectors)
        n_c = len(candidate_vectors)
        c_ids = candidate_ids if candidate_ids and len(candidate_ids) == n_c else list(range(n_c))
        k = min(k_neighbors, n_c)

        sim_matrix: List[List[float]] = []
        for q in query_vectors:
            row = [VectorTransformAlgoCSLSHubnessReduction._cosine(q, c) for c in candidate_vectors]
            sim_matrix.append(row)

        r_q = []
        for i in range(n_q):
            top_k_sims = sorted(sim_matrix[i], reverse=True)[:k]
            r_q.append(sum(top_k_sims) / max(1, len(top_k_sims)))

        k_q = min(k_neighbors, n_q)
        r_c = []
        for j in range(n_c):
            col_sims = sorted([sim_matrix[i][j] for i in range(n_q)], reverse=True)[:k_q]
            r_c.append(sum(col_sims) / max(1, len(col_sims)))

        rankings: List[List[Dict[str, Any]]] = []
        for i in range(n_q):
            row_results = []
            for j in range(n_c):
                csls_val = 2.0 * sim_matrix[i][j] - r_q[i] - r_c[j]
                row_results.append({
                    "candidate_id": c_ids[j],
                    "csls_score": round(csls_val, 6),
                    "raw_cosine": round(sim_matrix[i][j], 6),
                })
            row_results.sort(key=lambda x: x["csls_score"], reverse=True)
            rankings.append(row_results)

        return {
            "total_queries": n_q,
            "total_candidates": n_c,
            "k_neighbors": k,
            "csls_rankings": rankings,
        }
