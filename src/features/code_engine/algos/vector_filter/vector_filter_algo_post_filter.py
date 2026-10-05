"""
================================================================================
ALGORITHM BLUEPRINT: VECTOR POST-FILTERING WITH OVERSAMPLING (ALGO-VEC-FLTR-81)
================================================================================

Post-filtering executes an unconstrained nearest-neighbor search with an oversampling
multiplier (k * f), followed by metadata predicate rejection. It is suited only for
soft filters (such as language preference or non-security attributes) where selectivity
is high (most records pass). In accordance with policy rule VG1, post-filtering is
never permitted for tenant isolation or security ACLs.
"""

from typing import Any, Dict, List, Optional
import math


class VectorFilterAlgoPostFilter:
    """
    --- contract:
      id: ALGO-VEC-FLTR-81
      name: VectorFilterAlgoPostFilter
      category: filter
      complexity: O(N * D + k * f)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        metadata: list[dict[str, any]]
        query: list[float]
        filters: dict[str, any]
        k: int
        oversample_factor: float
      output_schema:
        requested_k: int
        oversampled_count: int
        surviving_count: int
        fallback_required: bool
        matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _matches_filters(item_meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if key not in item_meta:
                return False
            val = item_meta[key]
            if isinstance(expected, list):
                if val not in expected:
                    return False
            elif val != expected:
                return False
        return True

    @staticmethod
    def search_with_oversampling(
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        query: List[float],
        filters: Dict[str, Any],
        k: int = 5,
        oversample_factor: float = 4.0,
    ) -> Dict[str, Any]:
        if not vectors or not query:
            return {
                "requested_k": k,
                "oversampled_count": 0,
                "surviving_count": 0,
                "fallback_required": False,
                "matches": [],
            }

        if len(vectors) != len(metadata):
            raise ValueError("Vectors and metadata lists must have identical lengths")

        dim = len(query)
        target_candidates = min(len(vectors), max(k, int(math.ceil(k * oversample_factor))))

        all_scored: List[Dict[str, Any]] = []
        for i, vec in enumerate(vectors):
            dist_sq = sum((vec[d] - query[d]) ** 2 for d in range(min(dim, len(vec))))
            all_scored.append({
                "id": i,
                "distance": math.sqrt(dist_sq),
                "metadata": metadata[i],
            })

        all_scored.sort(key=lambda item: item["distance"])
        top_candidates = all_scored[:target_candidates]

        surviving: List[Dict[str, Any]] = []
        for item in top_candidates:
            if VectorFilterAlgoPostFilter._matches_filters(item["metadata"], filters):
                surviving.append(item)
                if len(surviving) == k:
                    break

        fallback_required = len(surviving) < k and len(vectors) > target_candidates

        return {
            "requested_k": k,
            "oversampled_count": len(top_candidates),
            "surviving_count": len(surviving),
            "fallback_required": fallback_required,
            "matches": surviving,
        }
