"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SIMPLIFIED GRAPH CONVOLUTION (SGC) (ALGO-GRAPH-GNN-262)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Simplifying Graph Convolutional Networks (SGC) Engine (Wu et al.).
   Collapses consecutive GCN non-linear activation layers into a single precomputed
   graph feature smoothing operator X_tilde = (A_hat)^K * X, reducing deep GNN training
   and inference complexity to standard linear logistic regression.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(K * M * d) precomputation, O(V * d * C) linear model training.
   - Space Complexity: O(V * d) smoothed feature buffer.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topology.
   - `features` (Dict[TNode, List[float]]): Input node features X.
   - `k_hops` (int): Number of smoothing filter multiplications K.

4. OUTPUT PARAMETERS:
   - `smooth_features()` (Dict[TNode, List[float]]): Precomputed smoothed feature matrix X_tilde.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact equivalence to GCN linear feature filter without parameter explosion.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSgcSimplifiedConvolution(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-262
      name: GraphAlgoSgcSimplifiedConvolution
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, sgc, linear_gnn, feature_smoothing, linear_classifier]
      inputs:
        type: object
        required: [adjacency, features]
        properties:
          adjacency: {type: object}
          features: {type: object}
          k_hops: {type: integer, minimum: 1, maximum: 10}
      outputs:
        type: object
        properties:
          smoothed_features: {type: object}
      parameters:
        k_hops: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * M * d)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        features: Dict[TNode, List[float]],
        k_hops: int = 2,
    ) -> None:
        """
        Initialize SGC linear smoothing engine.

        Args:
            adjacency: Adjacency dictionary.
            features: Input node feature vectors.
            k_hops: Smoothing exponent K.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._features: Dict[TNode, List[float]] = {u: list(features.get(u, [1.0])) for u in self._nodes}
        self._k_hops: int = max(1, min(10, k_hops))
        self._dim: int = len(next(iter(self._features.values()))) if self._features else 1

    def smooth_features(self) -> Dict[TNode, List[float]]:
        """
        Compute smoothed feature matrix X_tilde = (A_hat)^K * X.

        Returns:
            Dictionary mapping node to smoothed feature coordinates.
        """
        if not self._nodes:
            return {}

        degs = {u: math.sqrt(len(self._adj.get(u, [])) + 1.0) for u in self._nodes}
        curr_x: Dict[TNode, List[float]] = {u: list(self._features[u]) for u in self._nodes}

        for _ in range(self._k_hops):
            next_x: Dict[TNode, List[float]] = {}
            for u in self._nodes:
                nbrs = self._adj.get(u, []) + [u]
                deg_u = degs[u]
                agg = [0.0] * self._dim

                for v in nbrs:
                    deg_v = degs[v]
                    w = 1.0 / (deg_u * deg_v)
                    for d in range(self._dim):
                        agg[d] += w * curr_x[v][d]

                next_x[u] = agg

            curr_x = next_x

        return curr_x
