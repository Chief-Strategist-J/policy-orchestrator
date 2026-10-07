"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HITS & SALSA LINK ANALYSIS (ALGO-GRAPH-CENT-106)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dual Hub-Authority ranking suite providing Kleinberg's HITS power iteration
   and Lempel-Moran SALSA (Stochastic Approach for Link-Structure Analysis) bipartite
   random walk stationary equilibrium. Separates link aggregators (hubs) from content
   sources (authorities).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E)) per power iteration round.
   - Space Complexity: O(V) score vectors.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed graph adjacency (u -> v).
   - max_iter: int - Maximum number of power iterations (default: 50).
   - tol: float - L1 convergence norm threshold (default: 1e-6).

4. OUTPUT PARAMETERS:
   - hits_hubs: Dict[TNode, float] - Kleinberg HITS hub score vector.
   - hits_authorities: Dict[TNode, float] - Kleinberg HITS authority score vector.
   - salsa_hubs: Dict[TNode, float] - SALSA random-walk hub equilibrium distribution.
   - salsa_authorities: Dict[TNode, float] - SALSA random-walk authority equilibrium distribution.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Adjacency list with directed links.
   - Guardrails: Vectors are L2 normalized (HITS) and L1 normalized (SALSA) after every iteration.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHitsSalsa(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-106
      name: GraphAlgoHitsSalsa
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, hits, salsa, hubs_authorities, link_analysis]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_iter: {type: integer, default: 50}
          tol: {type: number, default: 1e-6}
      outputs:
        type: object
        required: [hits_hubs, hits_authorities, salsa_hubs, salsa_authorities]
        properties:
          hits_hubs: {type: object}
          hits_authorities: {type: object}
          salsa_hubs: {type: object}
          salsa_authorities: {type: object}
      parameters:
        max_iter: {type: integer, default: 50}
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
        adjacency: Dict[TNode, List[TNode]],
        max_iter: int = 50,
        tol: float = 1e-6,
    ) -> None:
        """
        Initialize the HITS and SALSA link analysis suite.

        Args:
            adjacency: Directed graph adjacency mapping.
            max_iter: Maximum power iterations.
            tol: L1 convergence residual tolerance.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
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

    def compute_hits(self) -> Tuple[Dict[TNode, float], Dict[TNode, float]]:
        """
        Compute Kleinberg's HITS Hub and Authority score vectors.

        Returns:
            Tuple of (hubs_map, authorities_map).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}

        hubs: Dict[TNode, float] = {u: 1.0 / math.sqrt(n) for u in self._nodes}
        auths: Dict[TNode, float] = {u: 1.0 / math.sqrt(n) for u in self._nodes}

        for _ in range(self._max_iter):
            next_auths: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
            for u in self._nodes:
                for in_v in self._in_neighbors.get(u, []):
                    next_auths[u] += hubs[in_v]

            norm_a = math.sqrt(sum(v * v for v in next_auths.values()))
            if norm_a > 0:
                next_auths = {u: v / norm_a for u, v in next_auths.items()}

            next_hubs: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
            for u in self._nodes:
                for out_v in self._adj.get(u, []):
                    next_hubs[u] += next_auths[out_v]

            norm_h = math.sqrt(sum(v * v for v in next_hubs.values()))
            if norm_h > 0:
                next_hubs = {u: v / norm_h for u, v in next_hubs.items()}

            diff = sum(abs(next_hubs[u] - hubs[u]) + abs(next_auths[u] - auths[u]) for u in self._nodes)
            hubs, auths = next_hubs, next_auths
            if diff < self._tol:
                break

        return hubs, auths

    def compute_salsa(self) -> Tuple[Dict[TNode, float], Dict[TNode, float]]:
        """
        Compute SALSA random-walk stationary equilibrium distributions.

        Returns:
            Tuple of (salsa_hubs, salsa_authorities).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}

        hub_nodes = [u for u in self._nodes if len(self._adj.get(u, [])) > 0]
        auth_nodes = [u for u in self._nodes if len(self._in_neighbors.get(u, [])) > 0]

        s_hubs: Dict[TNode, float] = {u: (1.0 / len(hub_nodes) if u in hub_nodes else 0.0) for u in self._nodes}
        s_auths: Dict[TNode, float] = {u: (1.0 / len(auth_nodes) if u in auth_nodes else 0.0) for u in self._nodes}

        for _ in range(self._max_iter):
            next_auths: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
            for a in auth_nodes:
                for h in self._in_neighbors[a]:
                    deg_h = len(self._adj.get(h, []))
                    if deg_h > 0:
                        next_auths[a] += s_hubs[h] / float(deg_h)

            total_a = sum(next_auths.values())
            if total_a > 0:
                next_auths = {u: v / total_a for u, v in next_auths.items()}

            next_hubs: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
            for h in hub_nodes:
                for a in self._adj.get(h, []):
                    deg_a = len(self._in_neighbors.get(a, []))
                    if deg_a > 0:
                        next_hubs[h] += next_auths[a] / float(deg_a)

            total_h = sum(next_hubs.values())
            if total_h > 0:
                next_hubs = {u: v / total_h for u, v in next_hubs.items()}

            diff = sum(abs(next_hubs[u] - s_hubs[u]) + abs(next_auths[u] - s_auths[u]) for u in self._nodes)
            s_hubs, s_auths = next_hubs, next_auths
            if diff < self._tol:
                break

        return s_hubs, s_auths
