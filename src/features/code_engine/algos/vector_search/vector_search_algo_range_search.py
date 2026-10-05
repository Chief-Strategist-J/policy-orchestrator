"""
================================================================================
ALGORITHM BLUEPRINT: RANGE (RADIUS) SEARCH (ALGO-VEC-SRCH-90)
================================================================================

Range (radius) search retrieves all vectors within a geometric distance threshold r
from the query point: {x ∈ X : d(x, q) ≤ r}. Unlike kNN which returns a fixed number
of candidates regardless of quality, range search returns variable-sized result sets
guaranteed to satisfy minimum similarity criteria, with an optional safety cap.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoRangeSearch:
    """
    --- contract:
      id: ALGO-VEC-SRCH-90
      name: RangeRadiusSearch
      category: vector
      complexity: O(N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        query: list[float]
        radius: float
        max_results: int
        metric: str
      output_schema:
        radius: float
        metric: str
        total_in_range: int
        returned_count: int
        matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def search_range(
        vectors: List[List[float]],
        query: List[float],
        radius: float,
        max_results: int = 100,
        metric: str = "l2",
    ) -> Dict[str, Any]:
        if not vectors or not query:
            return {
                "radius": radius,
                "metric": metric,
                "total_in_range": 0,
                "returned_count": 0,
                "matches": [],
            }

        dim = len(query)
        in_range: List[Dict[str, Any]] = []

        for i, vec in enumerate(vectors):
            if metric == "cosine":
                dot = sum(vec[d] * query[d] for d in range(min(dim, len(vec))))
                norm_v = math.sqrt(sum(v ** 2 for v in vec))
                norm_q = math.sqrt(sum(q ** 2 for q in query))
                sim = dot / (norm_v * norm_q) if norm_v * norm_q > 1e-12 else 0.0
                dist = 1.0 - sim
            else:
                dist_sq = sum((vec[d] - query[d]) ** 2 for d in range(min(dim, len(vec))))
                dist = math.sqrt(dist_sq)

            if dist <= radius:
                in_range.append({"id": i, "distance": round(dist, 6)})

        in_range.sort(key=lambda x: x["distance"])

        return {
            "radius": radius,
            "metric": metric,
            "total_in_range": len(in_range),
            "returned_count": min(len(in_range), max_results),
            "matches": in_range[:max_results],
        }
