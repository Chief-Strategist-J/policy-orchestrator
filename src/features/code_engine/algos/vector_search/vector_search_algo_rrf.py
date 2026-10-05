"""
================================================================================
ALGORITHM BLUEPRINT: RECIPROCAL RANK FUSION (RRF) (ALGO-VEC-SRCH-87)
================================================================================

Reciprocal Rank Fusion (RRF) combines ranked lists from disparate retrieval systems
(e.g., dense vector search, BM25, graph search) based purely on relative rank order
rather than raw scores. For document d across retrieval methods m:
RRF_score(d) = Σ [ 1 / (60 + rank_m(d)) ].
This eliminates the need for score calibration across heterogeneous retrieval algorithms.
"""

from typing import Any, Dict, List, Optional


class VectorSearchAlgoRRF:
    """
    --- contract:
      id: ALGO-VEC-SRCH-87
      name: ReciprocalRankFusion
      category: vector
      complexity: O(M * L + N log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        rankings: list[list[any]]
        k_rrf: int
        top_k: int
      output_schema:
        num_rankings: int
        total_unique_items: int
        fused_ranking: list[dict[str, any]]
    ---
    """

    @staticmethod
    def fuse(
        rankings: List[List[Any]],
        k_rrf: int = 60,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        if not rankings:
            return {"num_rankings": 0, "total_unique_items": 0, "fused_ranking": []}

        rrf_scores: Dict[Any, float] = {}
        appearances: Dict[Any, int] = {}
        best_ranks: Dict[Any, int] = {}

        for rank_list in rankings:
            for rank_idx, item in enumerate(rank_list):
                item_id = item.get("id") if isinstance(item, dict) else item
                rrf_increment = 1.0 / (k_rrf + (rank_idx + 1))
                rrf_scores[item_id] = rrf_scores.get(item_id, 0.0) + rrf_increment
                appearances[item_id] = appearances.get(item_id, 0) + 1
                current_best = best_ranks.get(item_id, 999999)
                best_ranks[item_id] = min(current_best, rank_idx + 1)

        fused = [
            {
                "id": item_id,
                "rrf_score": round(score, 6),
                "list_appearances": appearances[item_id],
                "best_rank": best_ranks[item_id],
            }
            for item_id, score in rrf_scores.items()
        ]

        fused.sort(key=lambda x: x["rrf_score"], reverse=True)

        return {
            "num_rankings": len(rankings),
            "total_unique_items": len(rrf_scores),
            "fused_ranking": fused[:top_k],
        }
