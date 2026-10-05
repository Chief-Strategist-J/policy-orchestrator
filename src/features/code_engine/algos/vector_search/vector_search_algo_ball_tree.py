"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BALL TREE METRIC INDEX (ALGO-VEC-SRCH-58)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Partitions metric space into bounding hyperspheres (#58) defined by a center
   vector and radius r. Highly effective in high dimensions where KD-trees degrade
   due to the curse of dimensionality. Prunes entire subtrees if the distance from
   the query to the ball's center exceeds r + current_best_search_radius.

2. ALGORITHMIC MECHANICS:
   - Tree Construction: Given subset of points, computes mean vector as centroid.
     Radius is max distance from centroid to any point in the subset.
     Finds the point with greatest distance from centroid, then the point furthest
     from that point, defining a split axis. Projects points onto axis and splits at median.
   - Search Traversal: Recursively visits closer ball child first. Prunes farther ball
     if max(0, dist(q, ball.center) - ball.radius) >= current_kth_distance.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Valid Metric: Assumes triangle inequality holds.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class BallNode:
    def __init__(
        self,
        center: np.ndarray,
        radius: float,
        point_indices: List[int],
        left: Optional["BallNode"] = None,
        right: Optional["BallNode"] = None,
    ):
        self.center = center
        self.radius = radius
        self.point_indices = point_indices
        self.left = left
        self.right = right


class VectorSearchAlgoBallTree:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-58
      name: VectorSearchAlgoBallTree
      version: 1.0.0
      category: vector
      capability_tags: [vector, spatial_tree, ball_tree, metric_space, nearest_neighbor]
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
          leaf_size: {type: integer, default: 16}
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
        - ADAPTER-BALLTREE-SEARCH-RESULT
    ---
    """

    @classmethod
    def build_tree(
        cls,
        vectors: np.ndarray,
        leaf_size: int = 16,
    ) -> Optional[BallNode]:
        N, D = vectors.shape
        if N == 0:
            return None

        def _build_recursive(indices: List[int]) -> Optional[BallNode]:
            if not indices:
                return None

            pts = vectors[indices]
            center = np.mean(pts, axis=0)
            diffs = pts - center
            dists = np.linalg.norm(diffs, axis=1)
            radius = float(np.max(dists)) if len(dists) > 0 else 0.0

            if len(indices) <= leaf_size:
                return BallNode(
                    center=center,
                    radius=radius,
                    point_indices=indices,
                )

            furthest_idx = indices[int(np.argmax(dists))]
            p1 = vectors[furthest_idx]
            dists_p1 = np.linalg.norm(pts - p1, axis=1)
            furthest_p2_idx = indices[int(np.argmax(dists_p1))]
            p2 = vectors[furthest_p2_idx]

            axis = p2 - p1
            axis_norm = np.linalg.norm(axis)
            if axis_norm > 0:
                axis = axis / axis_norm
                projections = np.dot(pts - p1, axis)
                median_val = float(np.median(projections))
                left_idx = [indices[i] for i in range(len(indices)) if projections[i] <= median_val]
                right_idx = [indices[i] for i in range(len(indices)) if projections[i] > median_val]
            else:
                half = len(indices) // 2
                left_idx = indices[:half]
                right_idx = indices[half:]

            if not left_idx or not right_idx:
                return BallNode(center=center, radius=radius, point_indices=indices)

            left_node = _build_recursive(left_idx)
            right_node = _build_recursive(right_idx)

            return BallNode(
                center=center,
                radius=radius,
                point_indices=indices,
                left=left_node,
                right=right_node,
            )

        return _build_recursive(list(range(N)))

    @classmethod
    def query_k_nearest(
        cls,
        vectors: Union[List[List[float]], np.ndarray],
        query: Union[List[float], np.ndarray],
        k: int = 5,
        leaf_size: int = 16,
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

        root = cls.build_tree(X, leaf_size=leaf_size)
        best_matches: List[Tuple[float, int]] = []

        def _search(node: Optional[BallNode]):
            if node is None:
                return

            dist_to_center = float(np.linalg.norm(q - node.center))
            cur_radius = best_matches[-1][0] if len(best_matches) == k else float("inf")

            if dist_to_center - node.radius >= cur_radius and len(best_matches) >= k:
                return

            if node.left is None and node.right is None:
                for idx in node.point_indices:
                    d = float(np.linalg.norm(X[idx] - q))
                    best_matches.append((d, idx))
                    best_matches.sort(key=lambda item: item[0])
                    if len(best_matches) > k:
                        best_matches.pop()
                return

            left_dist = float(np.linalg.norm(q - node.left.center)) if node.left else float("inf")
            right_dist = float(np.linalg.norm(q - node.right.center)) if node.right else float("inf")

            if left_dist <= right_dist:
                _search(node.left)
                _search(node.right)
            else:
                _search(node.right)
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
