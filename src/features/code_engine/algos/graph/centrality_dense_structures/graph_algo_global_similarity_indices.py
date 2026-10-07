"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GLOBAL SIMILARITY INDICES (ALGO-GRAPH-SIM-116)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Global and multi-hop path topological similarity suite.
   Computes Katz path similarity S = (I - beta * A)^(-1) - I, Local Path index
   LP = A^2 + epsilon * A^3, and Leicht-Holme-Newman (LHN) path-normalized similarity.
   Provides dense semantic similarity even when direct common neighbors are absent.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^3) matrix inversion / polynomial multiplication.
   - Space Complexity: O(V^2) dense similarity matrix storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - katz_beta: float - Katz path decay factor (default: 0.05).
   - lp_epsilon: float - Local path 3-hop weighting parameter (default: 0.01).

4. OUTPUT PARAMETERS:
   - katz_similarity: Dict[Tuple[TNode, TNode], float] - Global Katz path similarity matrix.
   - local_path_similarity: Dict[Tuple[TNode, TNode], float] - 2-and-3-hop LP similarity matrix.
   - lhn_similarity: Dict[Tuple[TNode, TNode], float] - Leicht-Holme-Newman normalized similarity.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Parameter beta < 1 / lambda_max.
   - Guardrails: Regularization avoids numerical divergence during power expansion.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGlobalSimilarityIndices(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SIM-116
      name: GraphAlgoGlobalSimilarityIndices
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, similarity, katz_index, local_path, lhn_similarity, link_prediction]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          katz_beta: {type: number, default: 0.05}
          lp_epsilon: {type: number, default: 0.01}
      outputs:
        type: object
        required: [katz_similarity, local_path_similarity, lhn_similarity]
        properties:
          katz_similarity: {type: object}
          local_path_similarity: {type: object}
          lhn_similarity: {type: object}
      parameters:
        katz_beta: {type: number, default: 0.05}
        lp_epsilon: {type: number, default: 0.01}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^3)
        space: O(V^2)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        katz_beta: float = 0.05,
        lp_epsilon: float = 0.01,
    ) -> None:
        """
        Initialize the Global Similarity engine.

        Args:
            adjacency: Graph adjacency dictionary.
            katz_beta: Path damping constant.
            lp_epsilon: 3-hop path weight factor.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._beta: float = katz_beta
        self._eps: float = lp_epsilon
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _mat_mul(self, a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        n = len(a)
        c = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if a[i][k] != 0:
                    for j in range(n):
                        c[i][j] += a[i][k] * b[k][j]
        return c

    def compute_similarities(self) -> Tuple[
        Dict[Tuple[TNode, TNode], float],
        Dict[Tuple[TNode, TNode], float],
        Dict[Tuple[TNode, TNode], float],
    ]:
        """
        Compute global Katz, Local Path, and LHN similarity matrices.

        Returns:
            Tuple of (katz_sim, local_path_sim, lhn_sim) dictionaries.
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}, {}

        idx = {u: i for i, u in enumerate(self._nodes)}
        a = [[0.0] * n for _ in range(n)]
        degrees = [0.0] * n

        for u in self._nodes:
            u_i = idx[u]
            for v in self._adj.get(u, []):
                v_i = idx[v]
                a[u_i][v_i] = 1.0
            degrees[u_i] = sum(a[u_i])

        a2 = self._mat_mul(a, a)
        a3 = self._mat_mul(a2, a)
        a4 = self._mat_mul(a3, a)

        katz_sim: Dict[Tuple[TNode, TNode], float] = {}
        lp_sim: Dict[Tuple[TNode, TNode], float] = {}
        lhn_sim: Dict[Tuple[TNode, TNode], float] = {}

        total_edges = sum(degrees)

        for i in range(n):
            for j in range(n):
                u, v = self._nodes[i], self._nodes[j]
                k_val = self._beta * a[i][j] + (self._beta ** 2) * a2[i][j] + (self._beta ** 3) * a3[i][j] + (self._beta ** 4) * a4[i][j]
                katz_sim[(u, v)] = k_val

                lp_val = a2[i][j] + self._eps * a3[i][j]
                lp_sim[(u, v)] = lp_val

                deg_prod = degrees[i] * degrees[j]
                if deg_prod > 0 and total_edges > 0:
                    expected_paths = deg_prod / float(total_edges)
                    lhn_val = a2[i][j] / expected_paths
                else:
                    lhn_val = 0.0
                lhn_sim[(u, v)] = lhn_val

        return katz_sim, lp_sim, lhn_sim
