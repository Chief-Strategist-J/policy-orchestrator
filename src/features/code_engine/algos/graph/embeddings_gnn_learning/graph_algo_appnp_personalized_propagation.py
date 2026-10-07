"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: APPNP PERSONALIZED PROPAGATION (ALGO-GRAPH-GNN-261)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Approximate Personalized Propagation of Neural Predictions (APPNP) Engine (Klicpera et al.).
   Decouples neural feature transformation from multi-hop graph propagation: generates
   base predictions H^(0) via MLP, then propagates predictions across K hops via
   Personalized PageRank power iterations H^(k+1) = (1 - alpha) * A_hat * H^(k) + alpha * H^(0),
   completely eliminating over-smoothing while capturing deep 10+ hop neighborhoods.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(K * M * d) sparse propagation steps without parameter explosion.
   - Space Complexity: O(V * d) vertex prediction and teleportation state.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `base_predictions` (Dict[TNode, List[float]]): Initial neural prediction vectors H^(0).
   - `alpha` (float): Teleportation probability (retaining anchor to H^(0)).
   - `k_steps` (int): Number of Personalized PageRank propagation rounds K.

4. OUTPUT PARAMETERS:
   - `propagate()` (Dict[TNode, List[float]]): Multi-hop propagated prediction distributions.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Teleport factor alpha strictly prevents asymptotic collapse to singular dominant eigenvector.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAppnpPersonalizedPropagation(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-261
      name: GraphAlgoAppnpPersonalizedPropagation
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, appnp, personalized_pagerank, over_smoothing, propagation]
      inputs:
        type: object
        required: [adjacency, base_predictions]
        properties:
          adjacency: {type: object}
          base_predictions: {type: object}
          alpha: {type: number, minimum: 0.01, maximum: 0.99}
          k_steps: {type: integer, minimum: 1, maximum: 50}
      outputs:
        type: object
        properties:
          propagated_predictions: {type: object}
      parameters:
        alpha: {type: number}
        k_steps: {type: integer}
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
        base_predictions: Dict[TNode, List[float]],
        alpha: float = 0.15,
        k_steps: int = 10,
    ) -> None:
        """
        Initialize APPNP personalized propagation engine.

        Args:
            adjacency: Adjacency map.
            base_predictions: Precomputed MLP predictions H^(0).
            alpha: Teleport factor.
            k_steps: Propagation iterations K.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._h0: Dict[TNode, List[float]] = {u: list(base_predictions.get(u, [0.0])) for u in self._nodes}
        self._alpha: float = max(0.01, min(0.99, alpha))
        self._k_steps: int = max(1, min(50, k_steps))
        self._dim: int = len(next(iter(self._h0.values()))) if self._h0 else 1

    def propagate(self) -> Dict[TNode, List[float]]:
        """
        Execute K-step APPNP Personalized PageRank prediction propagation.

        Returns:
            Dictionary mapping node to propagated prediction vector.
        """
        if not self._nodes:
            return {}

        degs = {u: math.sqrt(len(self._adj.get(u, [])) + 1.0) for u in self._nodes}
        curr_h: Dict[TNode, List[float]] = {u: list(self._h0[u]) for u in self._nodes}

        for _ in range(self._k_steps):
            next_h: Dict[TNode, List[float]] = {}
            for u in self._nodes:
                nbrs = self._adj.get(u, []) + [u]
                deg_u = degs[u]
                agg = [0.0] * self._dim

                for v in nbrs:
                    deg_v = degs[v]
                    w = 1.0 / (deg_u * deg_v)
                    for d in range(self._dim):
                        agg[d] += w * curr_h[v][d]

                combined = [
                    (1.0 - self._alpha) * agg[d] + self._alpha * self._h0[u][d]
                    for d in range(self._dim)
                ]
                next_h[u] = combined

            curr_h = next_h

        return curr_h
