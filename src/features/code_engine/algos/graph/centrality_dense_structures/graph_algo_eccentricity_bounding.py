"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ECCENTRICITY BOUNDING & EXTREMES (ALGO-GRAPH-NET-138)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Takes-Kosters distance bound propagation for vertex eccentricities, graph radius,
   graph center, and periphery. Propagates triangular inequality bounds e(v) >= max(d(v, w), e(w) - d(v, w))
   and e(v) <= e(w) + d(v, w) after each BFS to resolve exact eccentricities with a fraction of full BFS runs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * (V + E)) where k is the number of bound-resolving BFS passes.
   - Space Complexity: O(V) lower and upper bound vectors.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Connected undirected graph adjacency.

4. OUTPUT PARAMETERS:
   - eccentricities: Dict[TNode, int] - Exact eccentricity per vertex.
   - graph_radius: int - Minimum eccentricity across all vertices.
   - graph_center: List[TNode] - Vertices achieving minimum eccentricity (radius).
   - graph_periphery: List[TNode] - Vertices achieving maximum eccentricity (diameter).

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected graph.
   - Guardrails: Lower and upper bound convergence terminates each vertex's evaluation.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEccentricityBounding(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-138
      name: GraphAlgoEccentricityBounding
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, eccentricity, takes_kosters, graph_radius, graph_center, periphery]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [eccentricities, graph_radius, graph_center, graph_periphery]
        properties:
          eccentricities: {type: object}
          graph_radius: {type: integer}
          graph_center: {type: array, items: {type: string}}
          graph_periphery: {type: array, items: {type: string}}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * (V + E))
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Eccentricity Bounding engine.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _bfs(self, start: TNode) -> Tuple[Dict[TNode, int], int]:
        dist: Dict[TNode, int] = {start: 0}
        q: Deque[TNode] = deque([start])
        max_d = 0
        while q:
            u = q.popleft()
            d = dist[u]
            if d > max_d:
                max_d = d
            for v in self._adj.get(u, []):
                if v not in dist:
                    dist[v] = d + 1
                    q.append(v)
        return dist, max_d

    def compute_eccentricities(self) -> Tuple[Dict[TNode, int], int, List[TNode], List[TNode]]:
        """
        Compute exact vertex eccentricities via Takes-Kosters bound propagation.

        Returns:
            Tuple of (eccentricities_dict, graph_radius, graph_center_list, graph_periphery_list).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, 0, [], []
        if n == 1:
            u = self._nodes[0]
            return {u: 0}, 0, [u], [u]

        lb: Dict[TNode, int] = {u: 0 for u in self._nodes}
        ub: Dict[TNode, int] = {u: n for u in self._nodes}
        ecc: Dict[TNode, int] = {}
        unresolved = set(self._nodes)

        while unresolved:
            w = max(unresolved, key=lambda u: (ub[u] - lb[u], ub[u]))
            dist_w, ecc_w = self._bfs(w)
            ecc[w] = ecc_w
            unresolved.remove(w)
            lb[w] = ecc_w
            ub[w] = ecc_w

            to_remove = []
            for v in unresolved:
                d_vw = dist_w.get(v, n)
                new_lb = max(lb[v], d_vw, ecc_w - d_vw)
                new_ub = min(ub[v], ecc_w + d_vw)
                lb[v] = new_lb
                ub[v] = new_ub
                if lb[v] >= ub[v]:
                    ecc[v] = lb[v]
                    to_remove.append(v)

            for v in to_remove:
                unresolved.remove(v)

        radius = min(ecc.values())
        diameter = max(ecc.values())

        center = [u for u in self._nodes if ecc[u] == radius]
        periphery = [u for u in self._nodes if ecc[u] == diameter]

        return ecc, radius, center, periphery
