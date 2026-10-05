"""
================================================================================
ALGORITHM BLUEPRINT: INCREMENTAL IVF ASSIGNMENT (ALGO-VEC-UPD-119)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Assigns new vectors to nearest existing IVF centroids without triggering expensive
   clustering retraining. Tracks cluster balance and assigns vector IDs to postings.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoIncrementalIvf:
    """
    --- contract:
      id: ALGO-VEC-UPD-119
      name: VectorUpdateAlgoIncrementalIvf
      category: update
      complexity: O(N * K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        centroids: list[list[float]]
        vectors_to_insert: list[dict[str, Any]]
        inverted_lists: dict[int, list[str]]
      output_schema:
        updated_inverted_lists: dict[int, list[str]]
        assigned_centroids: list[dict[str, Any]]
        cluster_balance_variance: float
    ---
    """

    @staticmethod
    def _l2_sq(a: List[float], b: List[float]) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b))

    @classmethod
    def assign(
        cls,
        centroids: List[List[float]],
        vectors_to_insert: List[Dict[str, Any]],
        inverted_lists: Optional[Dict[int, List[str]]] = None,
    ) -> Dict[str, Any]:
        inv_lists: Dict[int, List[str]] = {i: list(inverted_lists.get(i, [])) if inverted_lists else [] for i in range(len(centroids))}
        assignments = []

        for item in vectors_to_insert:
            vid = item.get("id", "")
            v = item.get("vector", [])
            best_c = 0
            best_d = float("inf")
            for c_idx, c in enumerate(centroids):
                d = cls._l2_sq(v, c)
                if d < best_d:
                    best_d = d
                    best_c = c_idx
            inv_lists[best_c].append(vid)
            assignments.append({"id": vid, "centroid_id": best_c, "distance": math.sqrt(best_d)})

        lengths = [len(l) for l in inv_lists.values()]
        mean_len = sum(lengths) / len(lengths) if lengths else 0.0
        var = sum((x - mean_len) ** 2 for x in lengths) / len(lengths) if lengths else 0.0

        return {
            "updated_inverted_lists": inv_lists,
            "assigned_centroids": assignments,
            "cluster_balance_variance": round(var, 4),
        }
