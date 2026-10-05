"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RANDOM PROJECTION FOREST (ALGO-VEC-SRCH-60)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements an Annoy-style Random Projection Tree Forest (#60) for approximate
   nearest neighbor search. Splits points recursively using random separating
   hyperplanes. An ensemble of multiple independent trees provides high recall
   while maintaining logarithmic search latency.

2. ALGORITHMIC MECHANICS:
   - Forest Building: Constructs `num_trees` randomized binary trees.
     At each internal node, samples two random points, determines the equidistant
     hyperplane normal w and offset b. Splits points based on sign(dot(w, x) - b).
   - Priority Queue Search: Query traverses all trees simultaneously using a priority
     queue tracking distance to boundary hyperplanes.
   - Merges candidate sets from all trees, removes duplicates, and exact-scores survivors.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Deterministic Seeding: Accepts an optional seed for repeatable index construction.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import numpy as np


class RpNode:
    def __init__(
        self,
        normal: Optional[np.ndarray] = None,
        offset: float = 0.0,
        leaf_indices: Optional[List[int]] = None,
        left: Optional["RpNode"] = None,
        right: Optional["RpNode"] = None,
    ):
        self.normal = normal
        self.offset = offset
        self.leaf_indices = leaf_indices
        self.left = left
        self.right = right


class VectorSearchAlgoRpForest:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-60
      name: VectorSearchAlgoRpForest
      version: 1.0.0
      category: vector
      capability_tags: [vector, annoy, rp_tree, forest, random_projection, ann]
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
          num_trees: {type: integer, default: 5}
          max_leaf_size: {type: integer, default: 32}
          search_k: {type: integer, default: 100}
          seed: {type: integer}
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [k, dimension, num_trees, candidates_inspected, matches]
        properties:
          k: {type: integer}
          dimension: {type: integer}
          num_trees: {type: integer}
          candidates_inspected: {type: integer}
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
        time: O(T * N log N) build, O(T * log N + search_k * D) search
        space: O(T * N)
      preconditions:
        - len(input.vectors) > 0
        - len(input.query) > 0
      postconditions:
        - len(output.matches) <= input.k
      compatible_adapters:
        - ADAPTER-RP-FOREST-MATCHES
    ---
    """

    @classmethod
    def build_tree(
        cls,
        vectors: np.ndarray,
        max_leaf_size: int,
        rng: np.random.RandomState,
    ) -> Optional[RpNode]:
        N, D = vectors.shape

        def _build_recursive(indices: List[int]) -> Optional[RpNode]:
            if len(indices) <= max_leaf_size:
                return RpNode(leaf_indices=indices)

            sampled = rng.choice(indices, size=2, replace=False)
            p1 = vectors[sampled[0]]
            p2 = vectors[sampled[1]]

            normal = p1 - p2
            norm_val = np.linalg.norm(normal)
            if norm_val == 0.0:
                return RpNode(leaf_indices=indices)

            normal = normal / norm_val
            midpoint = (p1 + p2) * 0.5
            offset = float(np.dot(normal, midpoint))

            projections = np.dot(vectors[indices], normal) - offset
            left_idx = [indices[i] for i in range(len(indices)) if projections[i] <= 0]
            right_idx = [indices[i] for i in range(len(indices)) if projections[i] > 0]

            if not left_idx or not right_idx:
                return RpNode(leaf_indices=indices)

            left = _build_recursive(left_idx)
            right = _build_recursive(right_idx)

            return RpNode(normal=normal, offset=offset, left=left, right=right)

        return _build_recursive(list(range(N)))

    @classmethod
    def search(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
        query: Union[List[float], np.ndarray],
        k: int = 5,
        num_trees: int = 5,
        max_leaf_size: int = 32,
        search_k: int = 100,
        seed: Optional[int] = 42,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(vectors, dtype=np.float32)
        q = np.asarray(query, dtype=np.float32)
        N, D = X.shape

        if N == 0 or k <= 0:
            return {"k": k, "dimension": D, "num_trees": num_trees, "candidates_inspected": 0, "matches": []}

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        rng = np.random.RandomState(seed)
        forest = [cls.build_tree(X, max_leaf_size=max_leaf_size, rng=rng) for _ in range(num_trees)]

        candidates: Set[int] = set()
        effective_search_k = max(search_k, k * num_trees)

        q_heap: List[Tuple[float, int, RpNode]] = []
        counter = 0

        for root in forest:
            if root is not None:
                heapq.heappush(q_heap, (float("inf"), counter, root))
                counter += 1

        while q_heap and len(candidates) < effective_search_k:
            dist, _, node = heapq.heappop(q_heap)
            if node.leaf_indices is not None:
                candidates.update(node.leaf_indices)
            else:
                margin = float(np.dot(node.normal, q) - node.offset)
                if margin <= 0:
                    if node.left:
                        heapq.heappush(q_heap, (min(dist, abs(margin)), counter, node.left))
                        counter += 1
                    if node.right:
                        heapq.heappush(q_heap, (abs(margin), counter, node.right))
                        counter += 1
                else:
                    if node.right:
                        heapq.heappush(q_heap, (min(dist, abs(margin)), counter, node.right))
                        counter += 1
                    if node.left:
                        heapq.heappush(q_heap, (abs(margin), counter, node.left))
                        counter += 1

        cand_list = list(candidates)
        cand_vectors = X[cand_list]
        dists = np.linalg.norm(cand_vectors - q, axis=1)

        sorted_order = np.argsort(dists)[:min(k, len(cand_list))]

        matches = [
            {
                "id": ids[cand_list[idx]],
                "index": int(cand_list[idx]),
                "distance": float(dists[idx]),
            }
            for idx in sorted_order
        ]

        return {
            "k": k,
            "dimension": D,
            "num_trees": num_trees,
            "candidates_inspected": len(cand_list),
            "matches": matches,
        }
