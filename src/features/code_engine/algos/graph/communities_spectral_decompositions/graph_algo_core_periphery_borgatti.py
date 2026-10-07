"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CORE-PERIPHERY DETECTION (ALGO-GRAPH-COMM-163)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Borgatti-Everett discrete and continuous core-periphery structure detection algorithm.
   Evaluates network alignment against an idealized core-periphery pattern:
   - Core nodes connect densely to other core nodes.
   - Core nodes connect to peripheral nodes.
   - Peripheral nodes do NOT connect to each other.
   Optimizes correlation rho between empirical adjacency A and ideal pattern delta_ij = c_i * c_j.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * V^2) discrete genetic/local search.
   - Space Complexity: O(V) coreness vector.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - max_iter: int - Maximum local refinement passes (default: 20).
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - core_nodes: List[TNode] - Vertices assigned to the cohesive core.
   - periphery_nodes: List[TNode] - Vertices assigned to the sparse periphery.
   - correlation_rho: float - Pearson correlation with idealized blockmodel matrix.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph.
   - Guardrails: Core and periphery partitions are non-overlapping and cover all V.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCorePeripheryBorgatti(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-163
      name: GraphAlgoCorePeripheryBorgatti
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, core_periphery, borgatti_everett, blockmodels, structural_polarization]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_iter: {type: integer, default: 20}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [core_nodes, periphery_nodes, correlation_rho]
        properties:
          core_nodes: {type: array, items: {type: string}}
          periphery_nodes: {type: array, items: {type: string}}
          correlation_rho: {type: number}
      parameters:
        max_iter: {type: integer, default: 20}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(I * V^2)
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        max_iter: int = 20,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Core-Periphery analyzer.

        Args:
            adjacency: Graph adjacency dictionary.
            max_iter: Refinement iterations.
            rng_seed: Random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._max_iter: int = max_iter
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _compute_correlation(self, core_set: Set[TNode]) -> float:
        n = len(self._nodes)
        if n < 2:
            return 0.0

        pairs_a = []
        pairs_delta = []

        for i in range(n):
            u = self._nodes[i]
            is_u_core = 1.0 if u in core_set else 0.0
            for j in range(i + 1, n):
                v = self._nodes[j]
                is_v_core = 1.0 if v in core_set else 0.0

                a_ij = 1.0 if v in self._adj.get(u, set()) else 0.0
                delta_ij = 1.0 if (is_u_core == 1.0 or is_v_core == 1.0) else 0.0

                pairs_a.append(a_ij)
                pairs_delta.append(delta_ij)

        m = float(len(pairs_a))
        mean_a = sum(pairs_a) / m
        mean_d = sum(pairs_delta) / m

        var_a = sum((x - mean_a) ** 2 for x in pairs_a)
        var_d = sum((y - mean_d) ** 2 for y in pairs_delta)

        if var_a < 1e-12 or var_d < 1e-12:
            return 0.0

        cov = sum((pairs_a[i] - mean_a) * (pairs_delta[i] - mean_d) for i in range(int(m)))
        return cov / math.sqrt(var_a * var_d)

    def detect_core_periphery(self) -> Tuple[List[TNode], List[TNode], float]:
        """
        Partition graph into core and periphery sets maximizing pattern correlation.

        Returns:
            Tuple of (core_nodes_list, periphery_nodes_list, correlation_rho).
        """
        n = len(self._nodes)
        if n == 0:
            return [], [], 0.0

        rng = random.Random(self._rng_seed)
        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        sorted_by_deg = sorted(self._nodes, key=lambda u: (-degrees[u], str(u)))

        init_core_sz = max(1, n // 3)
        core: Set[TNode] = set(sorted_by_deg[:init_core_sz])
        best_rho = self._compute_correlation(core)

        for _ in range(self._max_iter):
            improved = False
            shuffled = list(self._nodes)
            rng.shuffle(shuffled)

            for u in shuffled:
                if u in core:
                    core.remove(u)
                    rho = self._compute_correlation(core)
                    if rho > best_rho:
                        best_rho = rho
                        improved = True
                    else:
                        core.add(u)
                else:
                    core.add(u)
                    rho = self._compute_correlation(core)
                    if rho > best_rho:
                        best_rho = rho
                        improved = True
                    else:
                        core.remove(u)

            if not improved:
                break

        core_list = sorted(list(core), key=lambda x: str(x))
        periphery_list = sorted(list(set(self._nodes) - core), key=lambda x: str(x))

        return core_list, periphery_list, best_rho
