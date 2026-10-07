"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RICH-CLUB COEFFICIENT (ALGO-GRAPH-NET-134)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Rich-Club Coefficient analyzer for scale-free and complex topologies.
   Measures whether high-degree vertices (hubs with deg > k) are more densely
   interconnected than expected by chance: phi(k) = 2 * E_>k / (N_>k * (N_>k - 1)).
   Computes normalized rich-club rho(k) against randomized degree-preserved null models.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k_max * (V + E)) evaluation across degree thresholds.
   - Space Complexity: O(V) degree index.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - num_null_models: int - Degree-preserved null random graphs for normalization (default: 5).
   - rng_seed: int - Random seed for null graph rewiring (default: 42).

4. OUTPUT PARAMETERS:
   - rich_club_raw: Dict[int, float] - Unnormalized phi(k) per degree threshold k.
   - rich_club_normalized: Dict[int, float] - Normalized rho(k) = phi(k) / phi_null(k).
   - max_degree: int - Maximum vertex degree present in the graph.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph.
   - Guardrails: Thresholds with fewer than 2 vertices have phi(k) = 0.0.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoRichClubCoefficient(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-134
      name: GraphAlgoRichClubCoefficient
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, rich_club, hub_clustering, elite_subgraph, null_model]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_null_models: {type: integer, default: 5}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [rich_club_raw, rich_club_normalized, max_degree]
        properties:
          rich_club_raw: {type: object}
          rich_club_normalized: {type: object}
          max_degree: {type: integer}
      parameters:
        num_null_models: {type: integer, default: 5}
        rng_seed: {type: integer, default: 42}
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
        num_null_models: int = 5,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Rich-Club analyzer.

        Args:
            adjacency: Graph adjacency dictionary.
            num_null_models: Count of null models for normalization.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._num_null: int = num_null_models
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _compute_phi_for_adj(self, adj: Dict[TNode, Set[TNode]]) -> Dict[int, float]:
        degrees: Dict[TNode, int] = {u: len(adj.get(u, set())) for u in self._nodes}
        max_deg = max(degrees.values()) if degrees else 0
        phi: Dict[int, float] = {}

        for k in range(max_deg):
            rich_nodes = [u for u in self._nodes if degrees[u] > k]
            n_k = len(rich_nodes)
            if n_k < 2:
                phi[k] = 0.0
                continue

            r_set = set(rich_nodes)
            e_k = 0
            for u in rich_nodes:
                e_k += len(adj.get(u, set()) & r_set)
            e_k = e_k // 2

            max_possible = (n_k * (n_k - 1)) // 2
            phi[k] = float(e_k) / float(max_possible) if max_possible > 0 else 0.0

        return phi

    def compute_rich_club(self) -> Tuple[Dict[int, float], Dict[int, float], int]:
        """
        Compute raw phi(k) and degree-preserved normalized rho(k).

        Returns:
            Tuple of (raw_phi_map, normalized_rho_map, max_degree).
        """
        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        max_deg = max(degrees.values()) if degrees else 0
        raw_phi = self._compute_phi_for_adj(self._adj)

        rng = random.Random(self._rng_seed)
        all_edges: List[Tuple[TNode, TNode]] = []
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    all_edges.append((u, v))

        null_phis: List[Dict[int, float]] = []
        for _ in range(self._num_null):
            rewired = list(all_edges)
            for _ in range(2 * len(rewired)):
                if len(rewired) < 2:
                    break
                i1, i2 = rng.sample(range(len(rewired)), 2)
                u1, v1 = rewired[i1]
                u2, v2 = rewired[i2]
                if u1 != u2 and v1 != v2 and u1 != v2 and u2 != v1:
                    rewired[i1] = (u1, v2)
                    rewired[i2] = (u2, v1)

            n_adj: Dict[TNode, Set[TNode]] = {u: set() for u in self._nodes}
            for u, v in rewired:
                n_adj[u].add(v)
                n_adj[v].add(u)
            null_phis.append(self._compute_phi_for_adj(n_adj))

        normalized_rho: Dict[int, float] = {}
        for k, p_val in raw_phi.items():
            null_vals = [n_p.get(k, 0.0) for n_p in null_phis]
            mean_null = sum(null_vals) / float(len(null_vals)) if null_vals else 0.0
            if mean_null > 1e-6:
                normalized_rho[k] = p_val / mean_null
            else:
                normalized_rho[k] = 1.0 if p_val == 0.0 else p_val

        return raw_phi, normalized_rho, max_deg
