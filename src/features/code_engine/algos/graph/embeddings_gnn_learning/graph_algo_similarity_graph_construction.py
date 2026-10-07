"""ALGORITHM & ARCHITECTURE BLUEPRINT: SIMILARITY GRAPH CONSTRUCTION (EPSILON, MUTUAL K-NN, ADAPTIVE KERNELS) (ALGO-GRAPH-SIM-284)

1. OVERVIEW & OBJECTIVE
Constructs continuous and discrete similarity graphs from unstructured multidimensional data points. Supports
three standard geometric affinity formulations: (1) Epsilon-neighborhood graphs (connecting pairs within distance epsilon),
(2) Mutual k-NN graphs (connecting pairs where each is among the k-nearest neighbors of the other), and
(3) Self-Tuning Adaptive Gaussian Kernels (Zelnik-Manor & Perona: W_{ij} = exp(-d(i, j)^2 / (sigma_i * sigma_j))).

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V|^2) similarity affinity matrix representation.
- Time Complexity: O(|V|^2 * d + |V|^2 log |V|) pairwise distance computation and sorting.
- Invariants:
  - Similarity matrix W is non-negative and symmetric: W_{ij} = W_{ji} >= 0.
  - Mutual k-NN enforces edge (u, v) iff u in TopK(v) AND v in TopK(u).

3. INPUT PARAMETERS:
- points: Mapping[TNode, Sequence[float]] point coordinate vectors.
- method: str 'epsilon', 'knn', 'mutual_knn', or 'adaptive_kernel'.
- epsilon: float distance cutoff for epsilon-neighborhood graphs.
- k: int neighbor count for k-NN / mutual k-NN / adaptive scale sigma_i = d(x_i, x_{i, k}).
- sigma: float global Gaussian bandwidth parameter for fixed-kernel affinity.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'weighted_adjacency': Dict[TNode, Dict[TNode, float]] weighted graph edges.
  - 'edge_count': int total non-zero edges in graph.
  - 'method': str construction mode executed.
  - 'local_scales': Dict[TNode, float] per-node sigma_i local scale estimates.

5. AGENT CONTRACT:
- Strict zero-inline-comment rule.
- Pure numeric distance operations.
"""

from __future__ import annotations

import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSimilarityGraphConstruction(Generic[TNode]):
    """Versatile similarity graph constructor supporting Epsilon, Mutual k-NN, and Self-Tuning kernels.

    ```yaml
    contract:
      id: ALGO-GRAPH-SIM-284
      name: GraphAlgoSimilarityGraphConstruction
      inputs:
        - name: points
          type: Mapping[TNode, Sequence[float]]
          description: Input point feature vectors.
        - name: method
          type: str
          default: 'adaptive_kernel'
          description: Affinity type ('epsilon', 'knn', 'mutual_knn', 'adaptive_kernel').
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Weighted similarity graph adjacency and local scale parameters.
      parameters:
        epsilon: float (default 1.0)
        k: int (default 7)
        sigma: float (default 1.0)
      capability_tags:
        - SIMILARITY_GRAPH
        - MUTUAL_KNN
        - ADAPTIVE_KERNEL
        - EPSILON_GRAPH
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V|^2 * d)
        space: O(|V|^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        points: Mapping[TNode, Sequence[float]],
        method: str = "adaptive_kernel",
        epsilon: float = 1.0,
        k: int = 7,
        sigma: float = 1.0,
    ) -> Dict[str, Any]:
        """Builds similarity graph using the specified geometric affinity metric."""
        nodes = list(points.keys())
        n = len(nodes)
        if n == 0:
            return {
                "weighted_adjacency": {},
                "edge_count": 0,
                "method": method,
                "local_scales": {},
            }

        dist_matrix: List[List[float]] = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = self._euclidean_dist(points[nodes[i]], points[nodes[j]])
                dist_matrix[i][j] = d
                dist_matrix[j][i] = d

        local_scales: Dict[TNode, float] = {}
        top_k_indices: Dict[int, Set[int]] = {}

        for i in range(n):
            sorted_nbrs = sorted(range(n), key=lambda j: dist_matrix[i][j])
            valid_nbrs = [j for j in sorted_nbrs if j != i]
            k_idx = min(k - 1, len(valid_nbrs) - 1)
            scale_val = dist_matrix[i][valid_nbrs[k_idx]] if valid_nbrs else 1.0
            local_scales[nodes[i]] = max(1e-6, scale_val)
            top_k_indices[i] = set(valid_nbrs[: min(k, len(valid_nbrs))])

        adj: Dict[TNode, Dict[TNode, float]] = {u: {} for u in nodes}
        edge_count = 0

        if method == "epsilon":
            for i in range(n):
                for j in range(i + 1, n):
                    d = dist_matrix[i][j]
                    if d <= epsilon:
                        w = math.exp(- (d * d) / (2.0 * sigma * sigma)) if sigma > 0 else 1.0
                        adj[nodes[i]][nodes[j]] = w
                        adj[nodes[j]][nodes[i]] = w
                        edge_count += 2

        elif method == "knn":
            for i in range(n):
                for j in top_k_indices[i]:
                    d = dist_matrix[i][j]
                    w = math.exp(- (d * d) / (2.0 * sigma * sigma)) if sigma > 0 else 1.0
                    adj[nodes[i]][nodes[j]] = w
                    edge_count += 1

        elif method == "mutual_knn":
            for i in range(n):
                for j in range(i + 1, n):
                    if j in top_k_indices[i] and i in top_k_indices[j]:
                        d = dist_matrix[i][j]
                        w = math.exp(- (d * d) / (2.0 * sigma * sigma)) if sigma > 0 else 1.0
                        adj[nodes[i]][nodes[j]] = w
                        adj[nodes[j]][nodes[i]] = w
                        edge_count += 2

        else:
            for i in range(n):
                for j in range(i + 1, n):
                    d = dist_matrix[i][j]
                    s_i = local_scales[nodes[i]]
                    s_j = local_scales[nodes[j]]
                    w = math.exp(- (d * d) / (s_i * s_j))
                    if w > 1e-4:
                        adj[nodes[i]][nodes[j]] = w
                        adj[nodes[j]][nodes[i]] = w
                        edge_count += 2

        return {
            "weighted_adjacency": adj,
            "edge_count": edge_count,
            "method": method,
            "local_scales": local_scales,
        }

    def _euclidean_dist(self, p1: Sequence[float], p2: Sequence[float]) -> float:
        """Calculates Euclidean metric distance."""
        s = 0.0
        for x, y in zip(p1, p2):
            diff = float(x) - float(y)
            s += diff * diff
        return math.sqrt(s)
