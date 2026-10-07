"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: K-TRUSS DECOMPOSITION (ALGO-GRAPH-DENSE-127)
================================================================================

1. OVERVIEW & OBJECTIVE:
   K-Truss triangle-supported dense subgraph decomposition and edge truss peeling algorithm.
   A k-truss is a maximal subgraph where every edge participates in at least (k - 2) triangles.
   Computes exact edge trussness numbers via iterative triangle support reduction.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m^1.5) triangle support maintenance.
   - Space Complexity: O(E) edge truss number map.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - edge_trussness: Dict[Tuple[TNode, TNode], int] - Maximal truss level k for each edge (k >= 2).
   - max_truss_k: int - Maximum truss level present in the entire graph.
   - truss_edge_counts: Dict[int, int] - Number of edges belonging to each k-truss.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph without multi-edges.
   - Guardrails: Edge support tracks mutual neighbors |N(u) cap N(v)|.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoKTrussDecomposition(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-127
      name: GraphAlgoKTrussDecomposition
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, k_truss, truss_decomposition, cohesive_subgraphs, fraud_detection]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [edge_trussness, max_truss_k, truss_edge_counts]
        properties:
          edge_trussness: {type: object}
          max_truss_k: {type: integer}
          truss_edge_counts: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m^1.5)
        space: O(E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the k-truss decomposition solver.

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

    def _canonical_edge(self, u: TNode, v: TNode) -> Tuple[TNode, TNode]:
        return (u, v) if str(u) < str(v) else (v, u)

    def compute_truss_decomposition(self) -> Tuple[Dict[Tuple[TNode, TNode], int], int, Dict[int, int]]:
        """
        Execute iterative triangle-supported edge peeling.

        Returns:
            Tuple of (edge_trussness_map, max_truss_k, truss_edge_counts).
        """
        edges: Set[Tuple[TNode, TNode]] = set()
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    edges.add((u, v))

        if not edges:
            return {}, 0, {}

        current_adj: Dict[TNode, Set[TNode]] = {u: set(self._adj.get(u, set())) for u in self._nodes}
        edge_support: Dict[Tuple[TNode, TNode], int] = {}
        for u, v in edges:
            common = len(current_adj[u] & current_adj[v])
            edge_support[(u, v)] = common

        edge_truss: Dict[Tuple[TNode, TNode], int] = {}
        remaining_edges = set(edges)
        k: int = 2

        while remaining_edges:
            while True:
                to_remove = [e for e in remaining_edges if edge_support[e] < k - 2]
                if not to_remove:
                    break
                for u, v in to_remove:
                    edge_truss[(u, v)] = max(2, k - 1)
                    remaining_edges.remove((u, v))
                    current_adj[u].remove(v)
                    current_adj[v].remove(u)

                    common_w = current_adj[u] & current_adj[v]
                    for w in common_w:
                        e_uw = self._canonical_edge(u, w)
                        e_vw = self._canonical_edge(v, w)
                        if e_uw in edge_support:
                            edge_support[e_uw] -= 1
                        if e_vw in edge_support:
                            edge_support[e_vw] -= 1
            k += 1

        max_k = max(edge_truss.values()) if edge_truss else 0
        truss_counts: Dict[int, int] = {}
        for tr in edge_truss.values():
            truss_counts[tr] = truss_counts.get(tr, 0) + 1

        return edge_truss, max_k, truss_counts
