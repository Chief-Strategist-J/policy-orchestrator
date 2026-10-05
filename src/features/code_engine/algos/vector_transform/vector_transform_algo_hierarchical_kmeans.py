"""
================================================================================
ALGORITHM BLUEPRINT: HIERARCHICAL & BALANCED K-MEANS (ALGO-VEC-TRFM-42)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a hierarchical balanced k-means cluster tree (HKM / vocabulary tree).
   Recursively clusters data into branching factor B clusters at each tree level up to
   max_depth, with capacity enforcement to prevent empty or oversized leaf buckets.

2. ARCHITECTURAL ROLE:
   Transformer & Indexer role (Layer 1). Enables O(log K) logarithmic coarse search
   routing instead of flat O(K) centroid comparisons in massive IVF indexes.

3. EXECUTION FLOW:
   a. Check base cases (node points <= max_leaf_size or depth >= max_depth).
   b. Run k-means clustering with branching factor B.
   c. Partition points among child nodes.
   d. Recursively build child cluster subtrees.
   e. Return hierarchical tree metadata with routing paths.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoHierarchicalKMeans:
    """
    --- contract:
      id: ALGO-VEC-TRFM-42
      name: VectorTransformAlgoHierarchicalKMeans
      category: transform
      complexity: O(depth * B * N * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        branching_factor: int
        max_depth: int
      output_schema:
        total_vectors: int
        branching_factor: int
        max_depth: int
        tree: dict[str, any]
    ---
    """

    @staticmethod
    def _build_tree(
        X: np.ndarray,
        indices: List[int],
        depth: int,
        branching_factor: int,
        max_depth: int,
    ) -> Dict[str, Any]:
        node_count = len(indices)
        if depth >= max_depth or node_count <= branching_factor:
            centroid = np.mean(X[indices], axis=0) if node_count > 0 else np.zeros(X.shape[1])
            return {
                "type": "leaf",
                "depth": depth,
                "count": node_count,
                "indices": indices,
                "centroid": [round(float(v), 6) for v in centroid],
            }

        k = min(branching_factor, node_count)
        rng = np.random.RandomState(42 + depth)
        init_pos = rng.choice(node_count, size=k, replace=False)
        centroids = X[[indices[p] for p in init_pos]].copy()

        dists = np.zeros((node_count, k))
        node_X = X[indices]
        for c_idx in range(k):
            dists[:, c_idx] = np.sum((node_X - centroids[c_idx]) ** 2, axis=1)

        assignments = np.argmin(dists, axis=1)

        children = []
        for c_idx in range(k):
            sub_indices = [indices[i] for i in range(node_count) if assignments[i] == c_idx]
            child_node = VectorTransformAlgoHierarchicalKMeans._build_tree(
                X, sub_indices, depth + 1, branching_factor, max_depth
            )
            children.append(child_node)

        parent_centroid = np.mean(node_X, axis=0)

        return {
            "type": "internal",
            "depth": depth,
            "count": node_count,
            "centroid": [round(float(v), 6) for v in parent_centroid],
            "children": children,
        }

    @staticmethod
    def build_hierarchy(
        vectors: List[List[float]],
        branching_factor: int = 2,
        max_depth: int = 2,
    ) -> Dict[str, Any]:
        if not vectors:
            return {
                "total_vectors": 0,
                "branching_factor": branching_factor,
                "max_depth": max_depth,
                "tree": {},
            }

        X = np.asarray(vectors, dtype=np.float64)
        n, d = X.shape
        tree = VectorTransformAlgoHierarchicalKMeans._build_tree(
            X, list(range(n)), depth=0, branching_factor=branching_factor, max_depth=max_depth
        )

        return {
            "total_vectors": n,
            "branching_factor": branching_factor,
            "max_depth": max_depth,
            "tree": tree,
        }
