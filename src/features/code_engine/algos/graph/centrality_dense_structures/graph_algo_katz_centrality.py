"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KATZ CENTRALITY (ALGO-GRAPH-CENT-107)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Katz path-attenuated centrality for directed and undirected networks.
   Measures influence based on the total number of paths between vertices, where paths
   of length k are exponentially attenuated by attenuation factor alpha^k.
   Uses baseline score beta to prevent 0-centrality sink traps in DAGs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E)) iterative linear convergence.
   - Space Complexity: O(V) score vectors.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - alpha: float - Attenuation factor alpha < 1 / lambda_max (default: 0.1).
   - beta: float - Uniform baseline exogenous weight (default: 1.0).
   - max_iter: int - Maximum iterations (default: 100).
   - tol: float - L1 residual convergence threshold (default: 1e-6).

4. OUTPUT PARAMETERS:
   - centrality: Dict[TNode, float] - Normalized Katz centrality scores.
   - iterations: int - Number of iterations executed until convergence.
   - converged: bool - Whether the solver converged within max_iter.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Alpha must be chosen below 1 / lambda_max to avoid divergence.
   - Guardrails: Scores are Euclidean L2 normalized upon completion.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoKatzCentrality(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-107
      name: GraphAlgoKatzCentrality
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, katz, path_attenuation, eigenvector_alternative]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          alpha: {type: number, default: 0.1}
          beta: {type: number, default: 1.0}
          max_iter: {type: integer, default: 100}
          tol: {type: number, default: 1e-6}
      outputs:
        type: object
        required: [centrality, iterations, converged]
        properties:
          centrality: {type: object}
          iterations: {type: integer}
          converged: {type: boolean}
      parameters:
        alpha: {type: number, default: 0.1}
        beta: {type: number, default: 1.0}
        max_iter: {type: integer, default: 100}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * (V + E))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        alpha: float = 0.1,
        beta: float = 1.0,
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> None:
        """
        Initialize the Katz Centrality solver.

        Args:
            adjacency: Graph outgoing adjacency mapping.
            alpha: Attenuation factor.
            beta: Base exogenous score.
            max_iter: Maximum iteration limit.
            tol: Convergence tolerance.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._alpha: float = alpha
        self._beta: float = beta
        self._max_iter: int = max_iter
        self._tol: float = tol
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

        self._in_neighbors: Dict[TNode, List[TNode]] = {u: [] for u in self._nodes}
        for u, neighbors in self._adj.items():
            for v in neighbors:
                if v in self._in_neighbors:
                    self._in_neighbors[v].append(u)

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_centrality(self) -> Tuple[Dict[TNode, float], int, bool]:
        """
        Compute Katz centrality scores via iterative fixed-point evaluation.

        Returns:
            Tuple of (centrality_scores, iterations_count, converged_flag).
        """
        n: int = len(self._nodes)
        if n == 0:
            return {}, 0, True

        x: Dict[TNode, float] = {u: self._beta for u in self._nodes}
        converged: bool = False
        iters: int = 0

        for it in range(self._max_iter):
            iters = it + 1
            next_x: Dict[TNode, float] = {}
            for u in self._nodes:
                in_sum = sum(x[v] for v in self._in_neighbors.get(u, []))
                next_x[u] = self._alpha * in_sum + self._beta

            diff = sum(abs(next_x[u] - x[u]) for u in self._nodes)
            x = next_x
            if diff < self._tol:
                converged = True
                break

        norm = math.sqrt(sum(val * val for val in x.values()))
        if norm > 0:
            norm_scores = {u: val / norm for u, val in x.items()}
        else:
            norm_scores = x

        return norm_scores, iters, converged
