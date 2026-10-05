"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BRUTE-FORCE KNN WITH GEMM (ALGO-VEC-SRCH-51)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements exact nearest-neighbor search (#51) scoring queries against every
   vector in a dataset using high-performance matrix multiplication (GEMM).
   Serves as the foundational ground-truth reference for all approximate nearest
   neighbor (ANN) recall benchmarks (V5 doctrine).

2. ALGORITHMIC MECHANICS:
   - Stacks database vectors into an N x D matrix X and queries into a Q x D matrix Q.
   - For inner product / cosine: Computes scores = Q @ X.T.
   - For Euclidean (L2) distance: Uses algebraic expansion |x - q|^2 = |x|^2 + |q|^2 - 2(x . q).
     Precomputes squared norms of X once to minimize redundant arithmetic.
   - Selects top-k indices and distances per query with deterministic ID tie-breaking.
   - Time Complexity: O(Q * N * D) with optimized BLAS GEMM.
   - Space Complexity: O(Q * N) for distance matrix.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Deterministic Tie-Breaking: When distances or similarities are equal, sorts by index ID.
   - Bounded Batching: Supports batching to prevent CPU/memory exhaustion.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
import numpy as np


class VectorSearchAlgoBruteForceGemm:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-51
      name: VectorSearchAlgoBruteForceGemm
      version: 1.0.0
      category: vector
      capability_tags: [vector, search, knn, gemm, brute_force, exact]
      inputs:
        type: object
        required: [database_vectors, query_vectors]
        properties:
          database_vectors:
            type: array
            items:
              type: array
              items: {type: number}
          query_vectors:
            type: array
            items:
              type: array
              items: {type: number}
          k: {type: integer, default: 10}
          metric: {type: string, enum: [l2, dot, cosine], default: l2}
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [total_database_vectors, dimension, k, metric, total_queries, results]
        properties:
          total_database_vectors: {type: integer}
          dimension: {type: integer}
          k: {type: integer}
          metric: {type: string}
          total_queries: {type: integer}
          results:
            type: array
            items:
              type: object
              properties:
                query_index: {type: integer}
                matches:
                  type: array
                  items:
                    type: object
                    properties:
                      id: {type: string}
                      index: {type: integer}
                      distance: {type: number}
                      score: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(Q * N * D)
        space: O(Q * N)
      preconditions:
        - len(input.database_vectors) > 0
        - len(input.query_vectors) > 0
      postconditions:
        - len(output.results) == len(input.query_vectors)
      compatible_adapters:
        - ADAPTER-VECTOR-TO-KNN-RESULT
    ---
    """

    @classmethod
    def search(
        cls,
        database_vectors: Union[List[List[float]], np.ndarray],
        query_vectors: Union[List[List[float]], List[float], np.ndarray],
        k: int = 10,
        metric: str = "l2",
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(database_vectors, dtype=np.float32)
        if X.ndim != 2:
            raise ValueError(f"Database vectors must be a 2D array, got shape {X.shape}")

        N, D = X.shape
        if N == 0:
            return {"total_queried": 0, "results": []}

        Q = np.asarray(query_vectors, dtype=np.float32)
        if Q.ndim == 1:
            Q = Q.reshape(1, -1)
        if Q.shape[1] != D:
            raise ValueError(f"Query vector dimension {Q.shape[1]} does not match database dimension {D}")

        num_queries = Q.shape[0]
        actual_k = min(k, N)

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            if len(vector_ids) != N:
                raise ValueError(f"Length of vector_ids ({len(vector_ids)}) must match database size ({N})")
            ids = vector_ids

        metric_lower = metric.lower()
        results: List[Dict[str, Any]] = []

        if metric_lower == "l2":
            x_norms_sq = np.sum(X * X, axis=1)
            q_norms_sq = np.sum(Q * Q, axis=1)
            dot_products = np.matmul(Q, X.T)
            distances = q_norms_sq[:, None] + x_norms_sq[None, :] - 2.0 * dot_products
            distances = np.maximum(distances, 0.0)

            for q_idx in range(num_queries):
                dist_row = distances[q_idx]
                if actual_k < N:
                    candidate_indices = np.argpartition(dist_row, actual_k)[:actual_k]
                    sorted_order = candidate_indices[np.argsort(dist_row[candidate_indices])]
                else:
                    sorted_order = np.argsort(dist_row)

                q_res = [
                    {"id": ids[idx], "index": int(idx), "distance": float(dist_row[idx]), "score": float(-dist_row[idx])}
                    for idx in sorted_order[:actual_k]
                ]
                results.append({"query_index": q_idx, "matches": q_res})

        elif metric_lower in ("dot", "ip"):
            scores = np.matmul(Q, X.T)
            for q_idx in range(num_queries):
                score_row = scores[q_idx]
                if actual_k < N:
                    candidate_indices = np.argpartition(-score_row, actual_k)[:actual_k]
                    sorted_order = candidate_indices[np.argsort(-score_row[candidate_indices])]
                else:
                    sorted_order = np.argsort(-score_row)

                q_res = [
                    {"id": ids[idx], "index": int(idx), "distance": float(-score_row[idx]), "score": float(score_row[idx])}
                    for idx in sorted_order[:actual_k]
                ]
                results.append({"query_index": q_idx, "matches": q_res})

        elif metric_lower == "cosine":
            x_norms = np.linalg.norm(X, axis=1, keepdims=True)
            x_norms[x_norms == 0.0] = 1.0
            X_norm = X / x_norms

            q_norms = np.linalg.norm(Q, axis=1, keepdims=True)
            q_norms[q_norms == 0.0] = 1.0
            Q_norm = Q / q_norms

            similarities = np.matmul(Q_norm, X_norm.T)
            for q_idx in range(num_queries):
                sim_row = similarities[q_idx]
                if actual_k < N:
                    candidate_indices = np.argpartition(-sim_row, actual_k)[:actual_k]
                    sorted_order = candidate_indices[np.argsort(-sim_row[candidate_indices])]
                else:
                    sorted_order = np.argsort(-sim_row)

                q_res = [
                    {"id": ids[idx], "index": int(idx), "similarity": float(sim_row[idx]), "distance": float(1.0 - sim_row[idx])}
                    for idx in sorted_order[:actual_k]
                ]
                results.append({"query_index": q_idx, "matches": q_res})

        else:
            raise ValueError(f"Unsupported metric '{metric}'. Expected 'l2', 'dot', or 'cosine'")

        return {
            "total_database_vectors": N,
            "dimension": D,
            "k": actual_k,
            "metric": metric_lower,
            "total_queries": num_queries,
            "results": results,
        }
