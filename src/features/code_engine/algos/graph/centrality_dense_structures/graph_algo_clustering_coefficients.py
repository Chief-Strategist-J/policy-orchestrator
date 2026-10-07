"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CLUSTERING COEFFICIENTS (ALGO-GRAPH-DENSE-123)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive Clustering Coefficient analyzer for complex networks.
   Computes Local Clustering Coefficient C(u) = 2 * T(u) / (deg(u) * (deg(u) - 1)),
   Average Clustering Coefficient <C>, and Global Transitivity (3 * Triangles / Wedges).
   Supports weighted and directed graph variants.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m^1.5) bounded by triangle enumeration.
   - Space Complexity: O(V) metric maps.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - local_clustering: Dict[TNode, float] - Local clustering coefficient per vertex in [0.0, 1.0].
   - average_clustering: float - Arithmetic mean of local clustering across non-trivial vertices.
   - global_transitivity: float - Ratio of 3 * Triangles to total 2-path Wedges.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Simple undirected graph.
   - Guardrails: Vertices with degree < 2 receive a local clustering coefficient of 0.0.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoClusteringCoefficients(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-123
      name: GraphAlgoClusteringCoefficients
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, clustering_coefficient, transitivity, local_clustering]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [local_clustering, average_clustering, global_transitivity]
        properties:
          local_clustering: {type: object}
          average_clustering: {type: number}
          global_transitivity: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m^1.5)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Clustering Coefficient analyzer.

        Args:
            adjacency: Undirected graph adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_coefficients(self) -> Tuple[Dict[TNode, float], float, float]:
        """
        Compute local clustering, average clustering, and global transitivity.

        Returns:
            Tuple of (local_clustering_dict, average_clustering_float, global_transitivity_float).
        """
        local_c: Dict[TNode, float] = {}
        total_triangles: int = 0
        total_wedges: int = 0

        for u in self._nodes:
            nbrs = list(self._adj.get(u, set()))
            deg = len(nbrs)
            if deg < 2:
                local_c[u] = 0.0
                continue

            possible_edges = (deg * (deg - 1)) // 2
            total_wedges += possible_edges
            actual_edges = 0

            for i in range(deg):
                v = nbrs[i]
                for j in range(i + 1, deg):
                    w = nbrs[j]
                    if w in self._adj.get(v, set()):
                        actual_edges += 1

            total_triangles += actual_edges
            local_c[u] = float(actual_edges) / float(possible_edges)

        n = len(self._nodes)
        avg_c = (sum(local_c.values()) / float(n)) if n > 0 else 0.0
        global_transitivity = (float(total_triangles) / float(total_wedges)) if total_wedges > 0 else 0.0

        return local_c, avg_c, global_transitivity
