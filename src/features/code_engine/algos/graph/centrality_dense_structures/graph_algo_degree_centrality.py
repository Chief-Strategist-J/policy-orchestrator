"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DEGREE CENTRALITY & STRENGTH (ALGO-GRAPH-CENT-101)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive degree centrality and vertex strength calculator.
   Computes in-degree, out-degree, total degree, weighted vertex strength,
   max-normalized degree, and average neighbor degree for directed/undirected graphs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) linear scan over adjacency structures.
   - Space Complexity: O(V) auxiliary memory for metric maps.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[Tuple[TNode, float]]] - Outgoing adjacency with edge weights.
   - is_directed: bool - Flag indicating whether the graph is directed (default: True).

4. OUTPUT PARAMETERS:
   - in_degrees: Dict[TNode, int] - Number of incoming edges per vertex.
   - out_degrees: Dict[TNode, int] - Number of outgoing edges per vertex.
   - total_degrees: Dict[TNode, int] - Total incident edges per vertex.
   - strengths: Dict[TNode, float] - Sum of incident edge weights per vertex.
   - normalized_degrees: Dict[TNode, float] - Degree divided by (V - 1).
   - avg_neighbor_degrees: Dict[TNode, float] - Mean degree of adjacent neighbors.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Adjacency list contains valid vertex keys.
   - Guardrails: Handles isolated vertices with degree 0 without divide-by-zero errors.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDegreeCentrality(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-101
      name: GraphAlgoDegreeCentrality
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, degree, strength, neighbor_degree]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency:
            type: object
            description: Map of node to list of (neighbor, weight) tuples.
          is_directed: {type: boolean, default: true}
      outputs:
        type: object
        required: [in_degrees, out_degrees, total_degrees, strengths, normalized_degrees, avg_neighbor_degrees]
        properties:
          in_degrees: {type: object}
          out_degrees: {type: object}
          total_degrees: {type: object}
          strengths: {type: object}
          normalized_degrees: {type: object}
          avg_neighbor_degrees: {type: object}
      parameters:
        is_directed: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]], is_directed: bool = True) -> None:
        """
        Initialize the degree centrality engine.

        Args:
            adjacency: Adjacency dictionary mapping node to list of (neighbor, weight) pairs.
            is_directed: Whether the graph is directed.
        """
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = adjacency
        self._is_directed: bool = is_directed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v, _ in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_metrics(self) -> Dict[str, Dict[TNode, float]]:
        """
        Compute degree centrality and strength metrics for all vertices.

        Returns:
            Dictionary containing in_degrees, out_degrees, total_degrees, strengths,
            normalized_degrees, and avg_neighbor_degrees maps.
        """
        n: int = len(self._nodes)
        out_deg: Dict[TNode, int] = {u: 0 for u in self._nodes}
        in_deg: Dict[TNode, int] = {u: 0 for u in self._nodes}
        strength: Dict[TNode, float] = {u: 0.0 for u in self._nodes}

        for u, neighbors in self._adj.items():
            out_deg[u] = len(neighbors)
            for v, w in neighbors:
                in_deg[v] = in_deg.get(v, 0) + 1
                strength[u] = strength.get(u, 0.0) + w
                if self._is_directed:
                    strength[v] = strength.get(v, 0.0) + w

        total_deg: Dict[TNode, int] = {}
        for u in self._nodes:
            total_deg[u] = (out_deg[u] + in_deg[u]) if self._is_directed else out_deg[u]

        denom: float = float(n - 1) if n > 1 else 1.0
        norm_deg: Dict[TNode, float] = {u: total_deg[u] / denom for u in self._nodes}

        avg_neighbor_deg: Dict[TNode, float] = {}
        for u in self._nodes:
            nbrs = [v for v, _ in self._adj.get(u, [])]
            if not nbrs:
                avg_neighbor_deg[u] = 0.0
            else:
                avg_neighbor_deg[u] = sum(total_deg.get(v, 0) for v in nbrs) / float(len(nbrs))

        return {
            "in_degrees": {u: float(in_deg[u]) for u in self._nodes},
            "out_degrees": {u: float(out_deg[u]) for u in self._nodes},
            "total_degrees": {u: float(total_deg[u]) for u in self._nodes},
            "strengths": strength,
            "normalized_degrees": norm_deg,
            "avg_neighbor_degrees": avg_neighbor_deg,
        }
