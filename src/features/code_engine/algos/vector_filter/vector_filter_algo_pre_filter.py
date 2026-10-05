"""
================================================================================
ALGORITHM BLUEPRINT: VECTOR PRE-FILTERING (ALGO-VEC-FLTR-80)
================================================================================

Metadata pre-filtering restricts vector scoring strictly to candidates that satisfy
security, tenant, and categorical filter predicates prior to distance evaluation.
This guarantees zero unauthorized vector leakage and exact compliance with tenant
isolation policies (VG1). For highly selective filters, scoring is performed via
direct brute force over the filtered subset; for low selectivity, candidates are
intersected with index candidate generators.
"""

from typing import Any, Dict, List, Optional
import math


class VectorFilterAlgoPreFilter:
    """
    --- contract:
      id: ALGO-VEC-FLTR-80
      name: VectorFilterAlgoPreFilter
      category: filter
      complexity: O(N_filtered * D + |M|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        metadata: list[dict[str, any]]
        query: list[float]
        filters: dict[str, any]
        k: int
      output_schema:
        total_vectors: int
        passed_filter_count: int
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
    def search_filtered(
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        query: List[float],
        filters: Dict[str, Any],
        k: int = 5,
    ) -> Dict[str, Any]:
        if not vectors or not query:
            return {"total_vectors": len(vectors), "passed_filter_count": 0, "matches": []}

        if len(vectors) != len(metadata):
            raise ValueError("Vectors and metadata lists must have identical lengths")

        dim = len(query)
        passed_indices: List[int] = []
        for i, meta in enumerate(metadata):
            if VectorFilterAlgoPreFilter._matches_filters(meta, filters):
                passed_indices.append(i)

        if not passed_indices:
            return {
                "total_vectors": len(vectors),
                "passed_filter_count": 0,
                "matches": [],
            }

        scored: List[Dict[str, Any]] = []
        for idx in passed_indices:
            vec = vectors[idx]
            dist_sq = sum((vec[d] - query[d]) ** 2 for d in range(min(dim, len(vec))))
            scored.append({
                "id": idx,
                "distance": math.sqrt(dist_sq),
                "metadata": metadata[idx],
            })

        scored.sort(key=lambda item: item["distance"])
        return {
            "total_vectors": len(vectors),
            "passed_filter_count": len(passed_indices),
            "matches": scored[:k],
        }
