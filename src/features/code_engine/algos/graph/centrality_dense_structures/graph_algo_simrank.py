"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SIMRANK STRUCTURAL SIMILARITY (ALGO-GRAPH-SIM-105)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Iterative SimRank vertex-to-vertex structural similarity engine.
   Based on the structural principle: "two vertices are similar if referenced by similar vertices".
   Computes fixed-point similarity matrix s(a, b) with geometric decay constant C.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(K * V^2 * d_in^2) iterative matrix fixed-point updates.
   - Space Complexity: O(V^2) similarity matrix storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed graph adjacency list (u -> v).
   - decay_c: float - SimRank decay constant C in (0, 1) (default: 0.8).
   - max_iter: int - Number of iteration rounds (default: 10).
   - tol: float - Frobenius/L1 convergence norm threshold (default: 1e-4).

4. OUTPUT PARAMETERS:
   - similarities: Dict[Tuple[TNode, TNode], float] - All-pairs SimRank score in [0.0, 1.0].
   - iterations: int - Execution rounds performed before convergence.
   - max_delta: float - Maximum change in score observed in the final round.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Adjacency list contains valid graph relationships.
   - Guardrails: s(u, u) = 1.0 identically at all iterations.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSimRank(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SIM-105
      name: GraphAlgoSimRank
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, similarity, simrank, structural_equivalence, link_analysis]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          decay_c: {type: number, default: 0.8}
          max_iter: {type: integer, default: 10}
          tol: {type: number, default: 0.0001}
      outputs:
        type: object
        required: [similarities, iterations, max_delta]
        properties:
          similarities: {type: object}
          iterations: {type: integer}
          max_delta: {type: number}
      parameters:
        decay_c: {type: number, default: 0.8}
        max_iter: {type: integer, default: 10}
        tol: {type: number, default: 0.0001}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * V^2 * d^2)
        space: O(V^2)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        decay_c: float = 0.8,
        max_iter: int = 10,
        tol: float = 1e-4,
    ) -> None:
        """
        Initialize the SimRank engine.

        Args:
            adjacency: Graph outgoing adjacency mapping.
            decay_c: Decay factor C in (0, 1).
            max_iter: Maximum iteration rounds.
            tol: Convergence tolerance.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._c: float = decay_c
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

    def compute_similarity(self) -> Tuple[Dict[Tuple[TNode, TNode], float], int, float]:
        """
        Compute the all-pairs SimRank matrix.

        Returns:
            Tuple of (similarities_map, iterations_executed, final_max_delta).
        """
        sim: Dict[Tuple[TNode, TNode], float] = {}
        for u in self._nodes:
            for v in self._nodes:
                sim[(u, v)] = 1.0 if u == v else 0.0

        iters: int = 0
        final_delta: float = 0.0

        for it in range(self._max_iter):
            iters = it + 1
            next_sim: Dict[Tuple[TNode, TNode], float] = {}
            max_delta: float = 0.0

            for u in self._nodes:
                for v in self._nodes:
                    if u == v:
                        next_sim[(u, v)] = 1.0
                        continue

                    in_u = self._in_neighbors.get(u, [])
                    in_v = self._in_neighbors.get(v, [])

                    if not in_u or not in_v:
                        next_sim[(u, v)] = 0.0
                    else:
                        sum_sim: float = 0.0
                        for nu in in_u:
                            for nv in in_v:
                                sum_sim += sim.get((nu, nv), 0.0)
                        val: float = (self._c / float(len(in_u) * len(in_v))) * sum_sim
                        next_sim[(u, v)] = val

                    delta = abs(next_sim[(u, v)] - sim[(u, v)])
                    if delta > max_delta:
                        max_delta = delta

            sim = next_sim
            final_delta = max_delta
            if max_delta < self._tol:
                break

        return sim, iters, final_delta
