"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ROBUST PRUNE ALPHA DIVERSITY (ALGO-VEC-SRCH-70)
================================================================================

1. OVERVIEW & OBJECTIVE:
   RobustPrune neighbor-selection heuristic with alpha parameter diversity filter (#70).
   Given candidate neighbors for a base point p, iteratively selects the nearest
   remaining candidate c and eliminates candidates x where alpha * d(c, x) <= d(p, x).
   When alpha > 1.0, suppresses redundant parallel paths while deliberately preserving
   crucial long-range shortcut edges that span metric clusters.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|Candidates|^2 * D) metric pruning pass.
   - Space Complexity: O(R) output neighbor set.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoRobustPrune:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-70
      name: VectorSearchAlgoRobustPrune
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, robust_prune, diskann, vamana]
      inputs:
        type: object
        required: [point, candidate_vectors]
        properties:
          point:
            type: array
            items: {type: number}
          candidate_vectors:
            type: array
            items: {type: array, items: {type: number}}
          candidate_ids:
            type: array
            items: {type: integer}
          alpha: {type: number, default: 1.2}
          r_max_degree: {type: integer, default: 64}
      outputs:
        type: object
        required: [selected_ids, total_selected, pruned_count]
        properties:
          selected_ids:
            type: array
            items: {type: integer}
          total_selected: {type: integer}
          pruned_count: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(C^2)
        space: O(R)
      preconditions:
        - len(point) > 0
        - alpha >= 1.0
      postconditions:
        - output.total_selected <= input.r_max_degree
      compatible_adapters:
        - ADAPTER-PRUNED-NEIGHBORS
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def prune(
        cls,
        point: List[float],
        candidate_vectors: List[List[float]],
        candidate_ids: Optional[List[int]] = None,
        alpha: float = 1.2,
        r_max_degree: int = 64,
    ) -> Dict[str, Any]:
        if not candidate_vectors:
            return {"selected_ids": [], "total_selected": 0, "pruned_count": 0}

        n = len(candidate_vectors)
        ids = candidate_ids if candidate_ids is not None and len(candidate_ids) == n else list(range(n))

        candidates: List[Tuple[float, int, List[float]]] = []
        for i in range(n):
            d = cls._euclidean_distance(point, candidate_vectors[i])
            candidates.append((d, ids[i], candidate_vectors[i]))

        candidates.sort(key=lambda x: x[0])

        selected: List[Tuple[int, List[float]]] = []
        pruned_count = 0

        while candidates and len(selected) < r_max_degree:
            c_dist, c_id, c_vec = candidates.pop(0)
            selected.append((c_id, c_vec))

            survivors: List[Tuple[float, int, List[float]]] = []
            for x_dist, x_id, x_vec in candidates:
                d_c_x = cls._euclidean_distance(c_vec, x_vec)
                if alpha * d_c_x <= x_dist:
                    pruned_count += 1
                else:
                    survivors.append((x_dist, x_id, x_vec))
            candidates = survivors

        selected_ids = [item[0] for item in selected]
        return {
            "selected_ids": selected_ids,
            "total_selected": len(selected_ids),
            "pruned_count": pruned_count,
        }
