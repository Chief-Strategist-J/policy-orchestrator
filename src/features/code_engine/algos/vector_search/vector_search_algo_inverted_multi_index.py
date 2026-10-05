"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: INVERTED MULTI-INDEX (IMI) (ALGO-VEC-SRCH-64)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Partitions the vector space into K1 x K2 fine Voronoi cells (#64) using the
   Cartesian product of two independent codebooks. Provides the granularity of
   millions of inverted lists using only 2 * K centroid vectors in memory,
   dramatically improving index resolution over standard single-codebook IVF.

2. ALGORITHMIC MECHANICS:
   - Indexing: Splits each vector x into two halves: x = [x_1, x_2].
     Quantizes x_1 against codebook C_1 (size K1) and x_2 against codebook C_2 (size K2).
     Stores point x into inverted list cell (i, j) = i * K2 + j.
   - Querying: Splits query q = [q_1, q_2]. Computes distances to all centroids in C_1
     and C_2. Orders pairs (i, j) by sum of distances d(q_1, C_1[i])^2 + d(q_2, C_2[j])^2
     using a priority queue (multi-sequence algorithm).
   - Scans candidates from the closest multi-index posting lists.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Multi-Sequence Exploration: Traverses cells in exact non-decreasing distance order.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class VectorSearchAlgoInvertedMultiIndex:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-64
      name: VectorSearchAlgoInvertedMultiIndex
      version: 1.0.0
      category: vector
      capability_tags: [vector, imi, inverted_multi_index, fine_quantization, ann]
      inputs:
        type: object
        required: [vectors, query]
        properties:
          vectors:
            type: array
            items:
              type: array
              items: {type: number}
          query:
            type: array
            items: {type: number}
          k: {type: integer, default: 5}
          codebook_k1: {type: integer, default: 4}
          codebook_k2: {type: integer, default: 4}
          max_cells_to_probe: {type: integer, default: 4}
          seed: {type: integer, default: 42}
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [k, dimension, total_cells, probed_cells, total_candidates, matches]
        properties:
          k: {type: integer}
          dimension: {type: integer}
          total_cells: {type: integer}
          probed_cells: {type: integer}
          total_candidates: {type: integer}
          matches:
            type: array
            items:
              type: object
              properties:
                id: {type: string}
                index: {type: integer}
                distance: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N * (K1 + K2)) build, O(K1 + K2 + |probed| * cand) search
        space: O(N + (K1 + K2) * (D / 2))
      preconditions:
        - len(input.vectors) > 0
        - len(input.query) > 0
      postconditions:
        - len(output.matches) <= input.k
      compatible_adapters:
        - ADAPTER-IMI-SEARCH-MATCHES
    ---
    """

    @classmethod
    def _train_centroids(cls, data: np.ndarray, k: int, rng: np.random.RandomState, max_iter: int = 10) -> np.ndarray:
        N = data.shape[0]
        actual_k = min(k, N)
        init_idx = rng.choice(N, size=actual_k, replace=False)
        centroids = data[init_idx].copy()

        for _ in range(max_iter):
            dists = np.linalg.norm(data[:, None, :] - centroids[None, :, :], axis=2)
            assigns = np.argmin(dists, axis=1)
            new_c = np.zeros_like(centroids)
            counts = np.zeros(actual_k, dtype=np.int32)
            for i in range(N):
                c = assigns[i]
                new_c[c] += data[i]
                counts[c] += 1
            for c in range(actual_k):
                if counts[c] > 0:
                    centroids[c] = new_c[c] / counts[c]
        return centroids

    @classmethod
    def search(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
        query: Union[List[float], np.ndarray],
        k: int = 5,
        codebook_k1: int = 4,
        codebook_k2: int = 4,
        max_cells_to_probe: int = 4,
        seed: int = 42,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(vectors, dtype=np.float32)
        q = np.asarray(query, dtype=np.float32)
        N, D = X.shape

        if N == 0 or k <= 0:
            return {"k": k, "dimension": D, "total_cells": 0, "probed_cells": 0, "total_candidates": 0, "matches": []}

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        rng = np.random.RandomState(seed)
        half_d = D // 2

        X1 = X[:, :half_d]
        X2 = X[:, half_d:]
        q1 = q[:half_d]
        q2 = q[half_d:]

        c1 = cls._train_centroids(X1, codebook_k1, rng=rng)
        c2 = cls._train_centroids(X2, codebook_k2, rng=rng)
        K1 = c1.shape[0]
        K2 = c2.shape[0]

        dists1 = np.linalg.norm(X1[:, None, :] - c1[None, :, :], axis=2)
        assigns1 = np.argmin(dists1, axis=1)

        dists2 = np.linalg.norm(X2[:, None, :] - c2[None, :, :], axis=2)
        assigns2 = np.argmin(dists2, axis=1)

        multi_lists: Dict[Tuple[int, int], List[int]] = {}
        for idx in range(N):
            cell = (int(assigns1[idx]), int(assigns2[idx]))
            if cell not in multi_lists:
                multi_lists[cell] = []
            multi_lists[cell].append(idx)

        q_dist1 = np.sum((c1 - q1[None, :]) ** 2, axis=1)
        q_dist2 = np.sum((c2 - q2[None, :]) ** 2, axis=1)

        order1 = np.argsort(q_dist1)
        order2 = np.argsort(q_dist2)

        pq: List[Tuple[float, int, int]] = []
        visited = set()

        init_dist = float(q_dist1[order1[0]] + q_dist2[order2[0]])
        heapq.heappush(pq, (init_dist, 0, 0))
        visited.add((0, 0))

        candidate_indices: List[int] = []
        cells_probed = 0
        limit_cells = min(max_cells_to_probe, K1 * K2)

        while pq and cells_probed < limit_cells:
            cell_dist, u, v = heapq.heappop(pq)
            c_idx1 = int(order1[u])
            c_idx2 = int(order2[v])
            cell_key = (c_idx1, c_idx2)

            if cell_key in multi_lists:
                candidate_indices.extend(multi_lists[cell_key])
            cells_probed += 1

            if u + 1 < K1 and (u + 1, v) not in visited:
                d_next = float(q_dist1[order1[u + 1]] + q_dist2[order2[v]])
                heapq.heappush(pq, (d_next, u + 1, v))
                visited.add((u + 1, v))

            if v + 1 < K2 and (u, v + 1) not in visited:
                d_next = float(q_dist1[order1[u]] + q_dist2[order2[v + 1]])
                heapq.heappush(pq, (d_next, u, v + 1))
                visited.add((u, v + 1))

        if not candidate_indices:
            return {
                "k": k,
                "dimension": D,
                "total_cells": K1 * K2,
                "probed_cells": cells_probed,
                "total_candidates": 0,
                "matches": [],
            }

        cand_unique = list(set(candidate_indices))
        cand_vectors = X[cand_unique]
        dists = np.linalg.norm(cand_vectors - q, axis=1)
        order = np.argsort(dists)[:min(k, len(cand_unique))]

        matches = [
            {
                "id": ids[cand_unique[idx]],
                "index": int(cand_unique[idx]),
                "distance": float(dists[idx]),
            }
            for idx in order
        ]

        return {
            "k": k,
            "dimension": D,
            "total_cells": K1 * K2,
            "probed_cells": cells_probed,
            "total_candidates": len(cand_unique),
            "matches": matches,
        }
