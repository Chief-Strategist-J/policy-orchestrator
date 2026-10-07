"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MARKOV CLUSTERING (MCL) (ALGO-GRAPH-COMM-159)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Markov Clustering (MCL) algorithm for graph partitioning based on random flow simulation.
   Alternates between matrix Expansion (squaring transition matrix M = M^2 to propagate flow)
   and Inflation (Hadamard entrywise exponentiation M_ij = (M_ij)^r followed by column normalization)
   until convergence to an idempotent doubly stochastic cluster attractor matrix.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * V^3) dense matrix expansion.
   - Space Complexity: O(V^2) transition matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - inflation_r: float - Inflation exponent parameter r > 1.0 (default: 2.0).
   - expansion_power: int - Random walk step expansion power (default: 2).
   - max_iter: int - Maximum expansion-inflation iteration rounds (default: 20).

4. OUTPUT PARAMETERS:
   - partition: Dict[TNode, int] - Discovered community assignment map.
   - num_clusters: int - Total number of disconnected attractor clusters.
   - converged: bool - Whether the process reached idempotency.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Self-loops are automatically added to avoid bipartite oscillation traps.
   - Guardrails: Column normalization maintains stochastic column sum = 1.0 after inflation.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMarkovClusteringMcl(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-159
      name: GraphAlgoMarkovClusteringMcl
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, mcl, markov_clustering, expansion_inflation, flow_simulation]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          inflation_r: {type: number, default: 2.0}
          expansion_power: {type: integer, default: 2}
          max_iter: {type: integer, default: 20}
      outputs:
        type: object
        required: [partition, num_clusters, converged]
        properties:
          partition: {type: object}
          num_clusters: {type: integer}
          converged: {type: boolean}
      parameters:
        inflation_r: {type: number, default: 2.0}
        max_iter: {type: integer, default: 20}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(I * V^3)
        space: O(V^2)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        inflation_r: float = 2.0,
        expansion_power: int = 2,
        max_iter: int = 20,
    ) -> None:
        """
        Initialize the Markov Clustering engine.

        Args:
            adjacency: Graph adjacency dictionary.
            inflation_r: Inflation power parameter r.
            expansion_power: Matrix squaring power.
            max_iter: Maximum iterations.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._r: float = inflation_r
        self._p: int = expansion_power
        self._max_iter: int = max_iter
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

    def cluster(self) -> Tuple[Dict[TNode, int], int, bool]:
        """
        Execute MCL Expansion and Inflation cycles.

        Returns:
            Tuple of (partition_map, num_clusters, converged_flag).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, 0, True
        if n == 1:
            return {self._nodes[0]: 0}, 1, True

        idx = {u: i for i, u in enumerate(self._nodes)}
        m = [[0.0] * n for _ in range(n)]

        for u in self._nodes:
            u_i = idx[u]
            m[u_i][u_i] = 1.0
            for v in self._adj.get(u, set()):
                v_i = idx[v]
                m[v_i][u_i] = 1.0

        for j in range(n):
            col_sum = sum(m[i][j] for i in range(n))
            if col_sum > 0:
                for i in range(n):
                    m[i][j] /= col_sum

        converged = False

        for _ in range(self._max_iter):
            expanded = list(m)
            for _ in range(self._p - 1):
                expanded = self._mat_mul(expanded, m)

            inflated = [[0.0] * n for _ in range(n)]
            for j in range(n):
                for i in range(n):
                    inflated[i][j] = expanded[i][j] ** self._r

                col_sum = sum(inflated[i][j] for i in range(n))
                if col_sum > 0:
                    for i in range(n):
                        inflated[i][j] /= col_sum

            diff = sum(abs(inflated[i][j] - m[i][j]) for i in range(n) for j in range(n))
            m = inflated
            if diff < 1e-4:
                converged = True
                break

        attractors: Set[int] = set()
        for i in range(n):
            if m[i][i] > 1e-3:
                attractors.add(i)

        if not attractors:
            attractors = set(range(n))

        part: Dict[TNode, int] = {}
        attractor_list = sorted(list(attractors))
        attr_to_c = {attr: c for c, attr in enumerate(attractor_list)}

        for j in range(n):
            best_attr = max(attractor_list, key=lambda i: m[i][j])
            part[self._nodes[j]] = attr_to_c[best_attr]

        return part, len(attractor_list), converged
