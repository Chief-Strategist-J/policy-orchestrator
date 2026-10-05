"""
================================================================================
ALGORITHM BLUEPRINT: SPARSE-DENSE HYBRID RETRIEVAL (ALGO-VEC-SRCH-86)
================================================================================

Sparse-dense hybrid retrieval blends lexical sparse keyword matching (BM25 or SPLADE)
with dense semantic vector similarity. Individual score channels are normalized
(min-max or rank-based) and combined via linear interpolation:
Score(d) = α · Score_dense(d) + (1 − α) · Score_sparse(d).
"""

from typing import Any, Dict, List, Optional


class VectorSearchAlgoSparseDenseHybrid:
    """
    --- contract:
      id: ALGO-VEC-SRCH-86
      name: SparseDenseHybridSearch
      category: vector
      complexity: O(|C_dense| + |C_sparse| + N log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        dense_results: list[dict[str, any]]
        sparse_results: list[dict[str, any]]
        alpha: float
        k: int
      output_schema:
        dense_count: int
        sparse_count: int
        alpha: float
        fused_results: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _normalize_scores(results: List[Dict[str, Any]], key: str = "score") -> Dict[Any, float]:
        if not results:
            return {}
        scores = [float(r.get(key, 0.0)) for r in results]
        min_s = min(scores)
        max_s = max(scores)
        denom = max_s - min_s if max_s > min_s else 1.0

        normalized: Dict[Any, float] = {}
        for r in results:
            doc_id = r.get("id")
            s = float(r.get(key, 0.0))
            normalized[doc_id] = (s - min_s) / denom
        return normalized

    @staticmethod
    def blend(
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        alpha: float = 0.5,
        k: int = 5,
    ) -> Dict[str, Any]:
        norm_dense = VectorSearchAlgoSparseDenseHybrid._normalize_scores(dense_results)
        norm_sparse = VectorSearchAlgoSparseDenseHybrid._normalize_scores(sparse_results)

        all_ids = set(norm_dense.keys()).union(norm_sparse.keys())
        meta_lookup: Dict[Any, Any] = {}
        for r in dense_results + sparse_results:
            doc_id = r.get("id")
            if "metadata" in r and doc_id not in meta_lookup:
                meta_lookup[doc_id] = r["metadata"]

        fused: List[Dict[str, Any]] = []
        for doc_id in all_ids:
            s_dense = norm_dense.get(doc_id, 0.0)
            s_sparse = norm_sparse.get(doc_id, 0.0)
            combined = alpha * s_dense + (1.0 - alpha) * s_sparse
            fused.append({
                "id": doc_id,
                "hybrid_score": round(combined, 6),
                "dense_score": round(s_dense, 6),
                "sparse_score": round(s_sparse, 6),
                "metadata": meta_lookup.get(doc_id, {}),
            })

        fused.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return {
            "dense_count": len(dense_results),
            "sparse_count": len(sparse_results),
            "alpha": alpha,
            "fused_results": fused[:k],
        }
