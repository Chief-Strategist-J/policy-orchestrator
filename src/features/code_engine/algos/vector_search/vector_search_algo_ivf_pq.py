"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IVF WITH PRODUCT QUANTIZATION (ALGO-VEC-SRCH-62)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Combines Inverted File coarse partitioning with Product Quantization (IVF-PQ, #62).
   Vectors are assigned to coarse Voronoi centroids, their residual vectors
   (x - c) are split into M sub-vectors, and each sub-vector is quantized into K*
   codebook centroids. Enables searching billions of vectors in RAM using Asymmetric
   Distance Computation (ADC) lookup tables.

2. ALGORITHMIC MECHANICS:
   - Indexing: Assigns vectors to nearest coarse centroids. For each cluster,
     computes residuals r = x - centroid. Splits residuals into M sub-vectors
     of dimension D/M and quantizes each against sub-codebooks into uint8 codes.
   - Querying: Finds top nprobe coarse centroids. For each centroid, calculates
     a precomputed distance lookup table between query sub-vectors and codebook centroids.
   - Distance Evaluation: Evaluates candidate distances via table lookups and additions:
     dist(q, x) approx sum_m Table[m, code[m]].

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Asymmetric Distance Computation: Keeps query unquantized for minimal quantization loss.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class VectorSearchAlgoIvfPq:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-62
      name: VectorSearchAlgoIvfPq
      version: 1.0.0
      category: vector
      capability_tags: [vector, ivf_pq, product_quantization, adc, compressed_search]
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
          num_clusters: {type: integer, default: 4}
          nprobe: {type: integer, default: 2}
          subspaces: {type: integer, default: 2}
          codebook_size: {type: integer, default: 4}
          seed: {type: integer, default: 42}
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [k, dimension, num_clusters, nprobe, subspaces, matches]
        properties:
          k: {type: integer}
          dimension: {type: integer}
          num_clusters: {type: integer}
          nprobe: {type: integer}
          subspaces: {type: integer}
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
        time: O(N * D) build, O(nprobe * (M * K* + |list| * M)) search
        space: O(N * M bytes)
      preconditions:
        - len(input.vectors) > 0
        - len(input.query) > 0
      postconditions:
        - len(output.matches) <= input.k
      compatible_adapters:
        - ADAPTER-IVF-PQ-MATCHES
    ---
    """

    @classmethod
    def train_kmeans(cls, data: np.ndarray, k: int, rng: np.random.RandomState, max_iter: int = 10) -> np.ndarray:
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
        num_clusters: int = 4,
        nprobe: int = 2,
        subspaces: int = 2,
        codebook_size: int = 4,
        seed: int = 42,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(vectors, dtype=np.float32)
        q = np.asarray(query, dtype=np.float32)
        N, D = X.shape

        if N == 0 or k <= 0:
            return {"k": k, "dimension": D, "num_clusters": num_clusters, "nprobe": nprobe, "subspaces": subspaces, "matches": []}

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        rng = np.random.RandomState(seed)
        M = max(1, min(subspaces, D))
        sub_d = D // M

        coarse_centroids = cls.train_kmeans(X, num_clusters, rng=rng)
        C = coarse_centroids.shape[0]

        dists_coarse = np.linalg.norm(X[:, None, :] - coarse_centroids[None, :, :], axis=2)
        coarse_assign = np.argmin(dists_coarse, axis=1)

        residuals = X - coarse_centroids[coarse_assign]

        sub_codebooks: List[np.ndarray] = []
        quantized_codes = np.zeros((N, M), dtype=np.int32)

        for m in range(M):
            start = m * sub_d
            end = (m + 1) * sub_d if m < M - 1 else D
            sub_residuals = residuals[:, start:end]
            sub_cb = cls.train_kmeans(sub_residuals, codebook_size, rng=rng)
            sub_codebooks.append(sub_cb)
            sub_dists = np.linalg.norm(sub_residuals[:, None, :] - sub_cb[None, :, :], axis=2)
            quantized_codes[:, m] = np.argmin(sub_dists, axis=1)

        inv_lists: Dict[int, List[int]] = {c: [] for c in range(C)}
        for idx, cluster_id in enumerate(coarse_assign):
            inv_lists[cluster_id].append(idx)

        q_to_coarse = np.linalg.norm(coarse_centroids - q, axis=1)
        actual_nprobe = min(max(1, nprobe), C)
        probed_clusters = [int(idx) for idx in np.argsort(q_to_coarse)[:actual_nprobe]]

        candidates: List[Tuple[float, int]] = []

        for cluster_id in probed_clusters:
            c_center = coarse_centroids[cluster_id]
            q_res = q - c_center
            cand_indices = inv_lists[cluster_id]
            if not cand_indices:
                continue

            lut: List[np.ndarray] = []
            for m in range(M):
                start = m * sub_d
                end = (m + 1) * sub_d if m < M - 1 else D
                q_sub = q_res[start:end]
                sub_cb = sub_codebooks[m]
                lut_m = np.sum((sub_cb - q_sub[None, :]) ** 2, axis=1)
                lut.append(lut_m)

            for idx in cand_indices:
                codes = quantized_codes[idx]
                adc_dist = sum(lut[m][codes[m]] for m in range(M))
                candidates.append((float(adc_dist), idx))

        candidates.sort(key=lambda item: item[0])
        top_candidates = candidates[:k]

        matches = [
            {
                "id": ids[idx],
                "index": int(idx),
                "distance": float(d),
            }
            for d, idx in top_candidates
        ]

        return {
            "k": k,
            "dimension": D,
            "num_clusters": C,
            "nprobe": actual_nprobe,
            "subspaces": M,
            "matches": matches,
        }
