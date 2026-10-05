"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PIVOT PRUNING VIA TRIANGLE INEQUALITY (#56)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Applies metric triangle inequality to prune distant candidate vectors (#56)
   without computing full query-to-candidate distances. Selects representative
   pivots and checks the lower bound |d(q, p) - d(x, p)| <= d(q, x). If the lower
   bound exceeds current best k-th distance, the candidate is discarded instantly.

2. ALGORITHMIC MECHANICS:
   - Offline Indexing: Precomputes and stores an N x P matrix of Euclidean distances
     from all database vectors X to P selected pivot points.
   - Query Phase: Computes distances from query q to all P pivots: d(q, p_j).
   - Candidate Filtering: For each candidate x_i, lower bound is max_j(|d(q, p_j) - d(x_i, p_j)|).
     If max lower bound > tau (k-th best so far), candidate is pruned without full evaluation.
   - Exact computation is only evaluated on unpruned survivors.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Metric Space Strictness: Applies to metric distance spaces (Euclidean, Angular).
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
import numpy as np


class VectorSearchAlgoPivotPruning:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-56
      name: VectorSearchAlgoPivotPruning
      version: 1.0.0
      category: vector
      capability_tags: [vector, pivot, pruning, triangle_inequality, metric_space]
      inputs:
        type: object
        required: [database_vectors, pivots, query_vector]
        properties:
          database_vectors:
            type: array
            items:
              type: array
              items: {type: number}
          pivots:
            type: array
            items:
              type: array
              items: {type: number}
          query_vector:
            type: array
            items: {type: number}
          precomputed_pivot_distances:
            type: array
            items:
              type: array
              items: {type: number}
          k: {type: integer, default: 5}
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [total_vectors, num_pivots, k, pruned_count, computed_count, pruning_ratio, matches]
        properties:
          total_vectors: {type: integer}
          num_pivots: {type: integer}
          k: {type: integer}
          pruned_count: {type: integer}
          computed_count: {type: integer}
          pruning_ratio: {type: number}
          matches:
            type: array
            items:
              type: object
              properties:
                id: {type: string}
                index: {type: integer}
                distance: {type: number}
                lower_bound: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N * P + Survivors * D)
        space: O(N * P)
      preconditions:
        - len(input.database_vectors) > 0
        - len(input.pivots) > 0
      postconditions:
        - output.pruned_count + output.computed_count == output.total_vectors
      compatible_adapters:
        - ADAPTER-PIVOT-PRUNED-MATCHES
    ---
    """

    @classmethod
    def search_with_pivots(
        cls,
        database_vectors: Union[List[List[float]], np.ndarray],
        pivots: Union[List[List[float]], np.ndarray],
        query_vector: Union[List[float], np.ndarray],
        precomputed_pivot_distances: Optional[Union[List[List[float]], np.ndarray]] = None,
        k: int = 5,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(database_vectors, dtype=np.float32)
        P = np.asarray(pivots, dtype=np.float32)
        q = np.asarray(query_vector, dtype=np.float32)

        N, D = X.shape
        num_pivots = P.shape[0]

        if precomputed_pivot_distances is None:
            diff = X[:, None, :] - P[None, :, :]
            dist_X_P = np.linalg.norm(diff, axis=2)
        else:
            dist_X_P = np.asarray(precomputed_pivot_distances, dtype=np.float32)

        dist_q_P = np.linalg.norm(P - q, axis=1)

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        lower_bounds = np.max(np.abs(dist_X_P - dist_q_P[None, :]), axis=1)

        order = np.argsort(lower_bounds)
        top_k: List[Dict[str, Any]] = []
        tau = float("inf")
        pruned_count = 0
        computed_count = 0

        for idx in order:
            lb = float(lower_bounds[idx])
            if lb >= tau and len(top_k) >= k:
                pruned_count += 1
                continue

            computed_count += 1
            actual_dist = float(np.linalg.norm(X[idx] - q))

            if actual_dist < tau or len(top_k) < k:
                top_k.append({
                    "id": ids[idx],
                    "index": int(idx),
                    "distance": actual_dist,
                    "lower_bound": lb,
                })
                top_k.sort(key=lambda item: item["distance"])
                if len(top_k) > k:
                    top_k.pop()
                if len(top_k) == k:
                    tau = top_k[-1]["distance"]

        return {
            "total_vectors": N,
            "num_pivots": num_pivots,
            "k": k,
            "pruned_count": pruned_count,
            "computed_count": computed_count,
            "pruning_ratio": float(pruned_count) / float(N) if N > 0 else 0.0,
            "matches": top_k,
        }
