"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VANTAGE-POINT TREE (ALGO-VEC-SRCH-59)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a metric Vantage-Point Tree (VP-tree, #59) that recursively partitions
   space using spherical shells centered on selected vantage points.
   Requires only a metric distance function (such as L2 or angular distance),
   making it ideal for general metric spaces without explicit coordinate systems.

2. ALGORITHMIC MECHANICS:
   - Tree Construction: Selects a vantage point v from the subset.
     Computes distances d(v, x) to all remaining points.
     Finds the median radius mu. Points with d(v, x) <= mu form the inside branch;
     points with d(v, x) > mu form the outside branch.
   - Search Traversal: Given query q, computes d(v, q).
     Explores the branch containing q first.
     Prunes the alternate branch using the triangle inequality:
     - If d(v, q) - tau > mu: Prunes inside branch.
     - If d(v, q) + tau < mu: Prunes outside branch.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Metric Space Strictness: Requires symmetry and triangle inequality.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class VpNode:
    def __init__(
        self,
        vantage_idx: int,
        threshold: float,
        left: Optional["VpNode"] = None,
        right: Optional["VpNode"] = None,
    ):
        self.vantage_idx = vantage_idx
        self.threshold = threshold
        self.left = left
        self.right = right


class VectorSearchAlgoVpTree:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-59
      name: VectorSearchAlgoVpTree
      version: 1.0.0
      category: vector
      capability_tags: [vector, spatial_tree, vp_tree, vantage_point, metric_space]
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
          vector_ids:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [k, dimension, total_nodes, matches]
        properties:
          k: {type: integer}
          dimension: {type: integer}
          total_nodes: {type: integer}
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
        time: O(N log N) build, O(log N) search
        space: O(N)
      preconditions:
        - len(input.vectors) > 0
        - len(input.query) > 0
      postconditions:
        - len(output.matches) <= input.k
      compatible_adapters:
        - ADAPTER-VPTREE-SEARCH-RESULT
    ---
    """

    @classmethod
    def build_tree(
        cls,
        vectors: np.ndarray,
    ) -> Optional[VpNode]:
        N, D = vectors.shape
        if N == 0:
            return None

        def _build_recursive(indices: List[int]) -> Optional[VpNode]:
            if not indices:
                return None

            v_idx = indices[0]
            if len(indices) == 1:
                return VpNode(vantage_idx=v_idx, threshold=0.0)

            rem_indices = indices[1:]
            v_vec = vectors[v_idx]
            dists = np.linalg.norm(vectors[rem_indices] - v_vec, axis=1)

            sorted_order = np.argsort(dists)
            median_pos = len(rem_indices) // 2
            threshold = float(dists[sorted_order[median_pos]])

            inside_indices = [rem_indices[i] for i in sorted_order[:median_pos]]
            outside_indices = [rem_indices[i] for i in sorted_order[median_pos:]]

            left = _build_recursive(inside_indices)
            right = _build_recursive(outside_indices)

            return VpNode(
                vantage_idx=v_idx,
                threshold=threshold,
                left=left,
                right=right,
            )

        return _build_recursive(list(range(N)))

    @classmethod
    def query_k_nearest(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
        query: Union[List[float], np.ndarray],
        k: int = 5,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(vectors, dtype=np.float32)
        q = np.asarray(query, dtype=np.float32)
        N, D = X.shape

        if N == 0 or k <= 0:
            return {"k": k, "dimension": D, "total_nodes": N, "matches": []}

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        root = cls.build_tree(X)
        best_matches: List[Tuple[float, int]] = []

        def _search(node: Optional[VpNode]):
            if node is None:
                return

            dist = float(np.linalg.norm(q - X[node.vantage_idx]))
            best_matches.append((dist, node.vantage_idx))
            best_matches.sort(key=lambda item: item[0])
            if len(best_matches) > k:
                best_matches.pop()

            tau = best_matches[-1][0] if len(best_matches) == k else float("inf")

            if dist < node.threshold:
                _search(node.left)
                if dist + tau >= node.threshold:
                    _search(node.right)
            else:
                _search(node.right)
                if dist - tau <= node.threshold:
                    _search(node.left)

        _search(root)

        matches = [
            {"id": ids[idx], "index": int(idx), "distance": float(d)}
            for d, idx in best_matches
        ]

        return {
            "k": k,
            "dimension": D,
            "total_nodes": N,
            "matches": matches,
        }
