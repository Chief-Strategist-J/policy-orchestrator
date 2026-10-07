"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PAGERANK POWER ITERATION (ALGO-GRAPH-CENT-102)
================================================================================

1. OVERVIEW & OBJECTIVE:
   In-depth PageRank implementation with power iteration, dangling node mass redistribution,
   damping factor attenuation, and L1 convergence residual tolerance.
   Supports weighted edges and uniform/custom personalization vectors.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E)) per power iteration round.
   - Space Complexity: O(V) auxiliary vectors.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[Tuple[TNode, float]]] - Outgoing adjacency with edge weights.
   - damping: float - Damping factor d (default: 0.85).
   - max_iter: int - Maximum number of power iterations (default: 100).
   - tol: float - L1 convergence norm threshold epsilon (default: 1e-6).
   - personalization: Optional[Dict[TNode, float]] - Teleportation distribution vector.

4. OUTPUT PARAMETERS:
   - ranks: Dict[TNode, float] - Equilibrium probability distribution summing to 1.0.
   - iterations: int - Total power iteration rounds executed.
   - converged: bool - Whether the L1 norm difference fell below tol.
   - residual: float - Final L1 norm difference between successive vectors.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Damping factor must satisfy 0 < d < 1.
   - Guardrails: Dangling nodes (out-degree = 0) redistribute mass uniformly to avoid score leaks.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPageRankInDepth(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-102
      name: GraphAlgoPageRankInDepth
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, pagerank, power_iteration, stationary_distribution]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          damping: {type: number, default: 0.85}
          max_iter: {type: integer, default: 100}
          tol: {type: number, default: 1e-6}
          personalization: {type: object}
      outputs:
        type: object
        required: [ranks, iterations, converged, residual]
        properties:
          ranks: {type: object}
          iterations: {type: integer}
          converged: {type: boolean}
          residual: {type: number}
      parameters:
        damping: {type: number, default: 0.85}
        max_iter: {type: integer, default: 100}
        tol: {type: number, default: 1e-6}
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
        adjacency: Dict[TNode, List[Tuple[TNode, float]]],
        damping: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-6,
        personalization: Optional[Dict[TNode, float]] = None,
    ) -> None:
        """
        Initialize the PageRank solver.

        Args:
            adjacency: Adjacency dictionary mapping node to list of (target, weight) pairs.
            damping: Teleportation damping factor (default: 0.85).
            max_iter: Max power iterations.
            tol: L1 convergence residual tolerance.
            personalization: Optional custom teleportation probability distribution.
        """
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = adjacency
        self._d: float = damping
        self._max_iter: int = max_iter
        self._tol: float = tol
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

        n: int = len(self._nodes)
        if personalization is not None and sum(personalization.values()) > 0:
            total_p = sum(personalization.values())
            self._teleport: Dict[TNode, float] = {u: personalization.get(u, 0.0) / total_p for u in self._nodes}
        else:
            self._teleport = {u: 1.0 / float(n) for u in self._nodes} if n > 0 else {}

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v, _ in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_pagerank(self) -> Tuple[Dict[TNode, float], int, bool, float]:
        """
        Execute power iteration to compute the stationary PageRank vector.

        Returns:
            Tuple of (ranks_dict, iterations_executed, converged_flag, final_residual).
        """
        n: int = len(self._nodes)
        if n == 0:
            return {}, 0, True, 0.0

        r: Dict[TNode, float] = {u: 1.0 / float(n) for u in self._nodes}
        out_weights: Dict[TNode, float] = {}
        for u in self._nodes:
            nbrs = self._adj.get(u, [])
            out_weights[u] = sum(w for _, w in nbrs)

        converged: bool = False
        final_residual: float = 0.0
        iters: int = 0

        for it in range(self._max_iter):
            iters = it + 1
            next_r: Dict[TNode, float] = {u: (1.0 - self._d) * self._teleport[u] for u in self._nodes}

            dangling_mass: float = 0.0
            for u in self._nodes:
                if out_weights[u] == 0:
                    dangling_mass += r[u]

            dangling_contrib: float = self._d * dangling_mass
            for u in self._nodes:
                next_r[u] += dangling_contrib * self._teleport[u]

            for u in self._nodes:
                total_w = out_weights[u]
                if total_w > 0:
                    flow = (self._d * r[u]) / total_w
                    for v, w in self._adj.get(u, []):
                        next_r[v] += flow * w

            diff: float = sum(abs(next_r[u] - r[u]) for u in self._nodes)
            r = next_r
            final_residual = diff

            if diff < self._tol:
                converged = True
                break

        return r, iters, converged, final_residual
