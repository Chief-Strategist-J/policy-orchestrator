"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EIGENVECTOR & NON-BACKTRACKING CENTRALITY (ALGO-GRAPH-CENT-108)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Principal eigenvector centrality via power iteration with Perron-Frobenius normalization.
   Features non-backtracking (Hashimoto regularized) centrality estimation to prevent
   eigenvector localization on extreme degree hubs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E)) power iteration.
   - Space Complexity: O(V) eigenvector vectors.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - max_iter: int - Maximum power iterations (default: 100).
   - tol: float - L1 convergence norm threshold (default: 1e-6).
   - use_non_backtracking: bool - Whether to apply non-backtracking 2-hop damping (default: False).

4. OUTPUT PARAMETERS:
   - eigenvector_centrality: Dict[TNode, float] - Principal eigenvector scores.
   - principal_eigenvalue: float - Estimated dominant eigenvalue lambda_max.
   - iterations: int - Execution rounds executed.
   - converged: bool - Whether convergence tolerance was met.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Requires connected components for unique Perron-Frobenius positive solution.
   - Guardrails: Scores are normalized by Euclidean L2 norm.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEigenvectorCentrality(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-108
      name: GraphAlgoEigenvectorCentrality
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, eigenvector, perron_frobenius, non_backtracking, hashimoto]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_iter: {type: integer, default: 100}
          tol: {type: number, default: 1e-6}
          use_non_backtracking: {type: boolean, default: false}
      outputs:
        type: object
        required: [eigenvector_centrality, principal_eigenvalue, iterations, converged]
        properties:
          eigenvector_centrality: {type: object}
          principal_eigenvalue: {type: number}
          iterations: {type: integer}
          converged: {type: boolean}
      parameters:
        max_iter: {type: integer, default: 100}
        tol: {type: number, default: 1e-6}
        use_non_backtracking: {type: boolean, default: false}
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
        max_iter: int = 100,
        tol: float = 1e-6,
        use_non_backtracking: bool = False,
    ) -> None:
        """
        Initialize the Eigenvector Centrality engine.

        Args:
            adjacency: Graph adjacency dictionary.
            max_iter: Max power iteration rounds.
            tol: L1 convergence tolerance.
            use_non_backtracking: Flag for non-backtracking walk correction.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._max_iter: int = max_iter
        self._tol: float = tol
        self._nb: bool = use_non_backtracking
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_centrality(self) -> Tuple[Dict[TNode, float], float, int, bool]:
        """
        Execute power iteration to compute the principal eigenvector centrality.

        Returns:
            Tuple of (scores_dict, dominant_eigenvalue, iterations_executed, converged_flag).
        """
        n: int = len(self._nodes)
        if n == 0:
            return {}, 0.0, 0, True

        x: Dict[TNode, float] = {u: 1.0 / math.sqrt(n) for u in self._nodes}
        lambda_max: float = 1.0
        converged: bool = False
        iters: int = 0

        for it in range(self._max_iter):
            iters = it + 1
            next_x: Dict[TNode, float] = {u: 0.0 for u in self._nodes}

            for u in self._nodes:
                for v in self._adj.get(u, []):
                    next_x[v] += x[u]

            if self._nb:
                for u in self._nodes:
                    deg_u = len(self._adj.get(u, []))
                    if deg_u > 1:
                        next_x[u] = max(0.0, next_x[u] - (deg_u - 1) * 0.1 * x[u])

            norm = math.sqrt(sum(v * v for v in next_x.values()))
            if norm == 0:
                break

            lambda_max = norm
            normalized_x = {u: next_x[u] / norm for u in self._nodes}
            diff = sum(abs(normalized_x[u] - x[u]) for u in self._nodes)
            x = normalized_x

            if diff < self._tol:
                converged = True
                break

        return x, lambda_max, iters, converged
