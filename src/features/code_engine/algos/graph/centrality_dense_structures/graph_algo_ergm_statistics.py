"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ERGM SUFFICIENT STATISTICS (ALGO-GRAPH-MODEL-143)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Exponential Random Graph Model (ERGM) sufficient statistic vector calculator.
   Computes standard canonical network statistics:
   - Edge count (density).
   - 2-Star and k-Star counts.
   - Triangle count (transitivity).
   - GWESP (Geometrically Weighted Edgewise Shared Partner) curved transitivity statistic.
   Provides foundation for MCMC parameter estimation and network hypothesis testing.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m^1.5) bounded by triangle and shared-partner evaluation.
   - Space Complexity: O(V) degree and partner histograms.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - gwesp_alpha: float - Geometric decay parameter alpha for GWESP (default: 0.25).

4. OUTPUT PARAMETERS:
   - edge_count: int - Total number of edges in the network.
   - two_star_count: int - Total number of 2-stars sum_u (deg(u) * (deg(u) - 1) / 2).
   - triangle_count: int - Total number of triangles.
   - gwesp_statistic: float - Geometric weighted edgewise shared partner statistic.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph.
   - Guardrails: Non-negative statistics ensure proper exponential family log-likelihood evaluation.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoErgmStatistics(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-143
      name: GraphAlgoErgmStatistics
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, ergm, exponential_random_graph, sufficient_statistics, gwesp, 2_stars]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          gwesp_alpha: {type: number, default: 0.25}
      outputs:
        type: object
        required: [edge_count, two_star_count, triangle_count, gwesp_statistic]
        properties:
          edge_count: {type: integer}
          two_star_count: {type: integer}
          triangle_count: {type: integer}
          gwesp_statistic: {type: number}
      parameters:
        gwesp_alpha: {type: number, default: 0.25}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m^1.5)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], gwesp_alpha: float = 0.25) -> None:
        """
        Initialize the ERGM Sufficient Statistics calculator.

        Args:
            adjacency: Graph adjacency dictionary.
            gwesp_alpha: GWESP geometric decay constant.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._alpha: float = gwesp_alpha
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_statistics(self) -> Tuple[int, int, int, float]:
        """
        Compute ERGM sufficient statistics: edges, 2-stars, triangles, and GWESP.

        Returns:
            Tuple of (edge_count, two_star_count, triangle_count, gwesp_statistic).
        """
        degrees: Dict[TNode, int] = {u: len(self._adj.get(u, set())) for u in self._nodes}
        edge_count: int = sum(degrees.values()) // 2
        two_stars: int = sum((d * (d - 1)) // 2 for d in degrees.values())

        edges: List[Tuple[TNode, TNode]] = []
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    edges.append((u, v))

        triangles: int = 0
        gwesp_stat: float = 0.0
        decay = math.exp(self._alpha)

        for u, v in edges:
            shared = len(self._adj[u] & self._adj[v])
            triangles += shared
            if shared > 0:
                gwesp_weight = decay * (1.0 - (1.0 - (1.0 / decay)) ** shared)
                gwesp_stat += gwesp_weight

        triangles = triangles // 3

        return edge_count, two_stars, triangles, gwesp_stat
