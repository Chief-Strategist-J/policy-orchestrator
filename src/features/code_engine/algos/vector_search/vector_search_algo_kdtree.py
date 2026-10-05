"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KD-TREE SPATIAL PARTITIONING (#57)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs an axis-aligned orthogonal KD-tree (#57) for exact and bounded
   sub-linear vector retrieval in low-to-medium dimensions (D <= 32).
   Partitions space recursively along the dimension of maximum spread/variance.

2. ALGORITHMIC MECHANICS:
   - Tree Construction: Selects the split axis d = depth % D (or highest variance).
     Computes the median along axis d. Left subtree receives points < median;
     right subtree receives points >= median.
   - Search Traversal: Descends recursively to find the target leaf cell.
     Backtracks to check alternate bounding half-spaces whenever the hypersphere
     of radius r (current best distance to k-th point) intersects the hyperplane |q[d] - split_val| < r.
   - Time Complexity: O(N log N) build, O(log N) average query in low dimensions.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Deterministic Pivot: Uses median with stable secondary sorting.
================================================================================
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class KdNode:
    def __init__(
        self,
        point_idx: int,
        axis: int,
        split_val: float,
        left: Optional["KdNode"] = None,
        right: Optional["KdNode"] = None,
    ):
        self.point_idx = point_idx
        self.axis = axis
        self.split_val = split_val
        self.left = left
        self.right = right


class VectorSearchAlgoKdTree:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-57
      name: VectorSearchAlgoKdTree
      version: 1.0.0
      category: vector
      capability_tags: [vector, spatial_tree, kdtree, partition, nearest_neighbor]
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
        time: O(N log N) build, O(log N) query
        space: O(N)
      preconditions:
        - len(input.vectors) > 0
        - len(input.query) > 0
      postconditions:
        - len(output.matches) <= input.k
      compatible_adapters:
        - ADAPTER-KDTREE-SEARCH-RESULT
    ---
    """

    @classmethod
    def build_tree(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
    ) -> Tuple[Optional[KdNode], np.ndarray]:
        X = np.asarray(vectors, dtype=np.float32)
        N, D = X.shape
        if N == 0:
            return None, X

        indices = list(range(N))

        def _recursive_build(idx_list: List[int], depth: int) -> Optional[KdNode]:
            if not idx_list:
                return None

            axis = depth % D
            idx_list.sort(key=lambda i: (float(X[i, axis]), i))
            median_pos = len(idx_list) // 2
            median_idx = idx_list[median_pos]
            split_val = float(X[median_idx, axis])

            left_node = _recursive_build(idx_list[:median_pos], depth + 1)
            right_node = _recursive_build(idx_list[median_pos + 1:], depth + 1)

            return KdNode(
                point_idx=median_idx,
                axis=axis,
                split_val=split_val,
                left=left_node,
                right=right_node,
            )

        root = _recursive_build(indices, 0)
        return root, X

    @classmethod
    def query_k_nearest(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
        query: Union[List[float], np.ndarray],
        k: int = 5,
        vector_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        root, X = cls.build_tree(vectors)
        N, D = X.shape
        q = np.asarray(query, dtype=np.float32)

        if root is None or k <= 0:
            return {"k": k, "dimension": D, "total_nodes": N, "matches": []}

        if vector_ids is None:
            ids = [str(i) for i in range(N)]
        else:
            ids = vector_ids

        best_matches: List[Tuple[float, int]] = []

        def _search_node(node: Optional[KdNode]):
            if node is None:
                return

            dist = float(np.linalg.norm(X[node.point_idx] - q))
            best_matches.append((dist, node.point_idx))
            best_matches.sort(key=lambda item: item[0])
            if len(best_matches) > k:
                best_matches.pop()

            cur_best_radius = best_matches[-1][0] if len(best_matches) == k else float("inf")

            axis = node.axis
            diff = float(q[axis] - node.split_val)

            first_branch = node.left if diff < 0 else node.right
            second_branch = node.right if diff < 0 else node.left

            _search_node(first_branch)

            if abs(diff) < cur_best_radius or len(best_matches) < k:
                _search_node(second_branch)

        _search_node(root)

        matches = [
            {
                "id": ids[idx],
                "index": int(idx),
                "distance": float(d),
            }
            for d, idx in best_matches
        ]

        return {
            "k": k,
            "dimension": D,
            "total_nodes": N,
            "matches": matches,
        }
