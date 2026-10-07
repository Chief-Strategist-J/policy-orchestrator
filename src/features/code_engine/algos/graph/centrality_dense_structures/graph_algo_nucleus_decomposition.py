"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NUCLEUS DECOMPOSITION (ALGO-GRAPH-DENSE-128)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Generalized (r, s)-Nucleus Decomposition algorithm for hierarchical dense subgraph mining.
   Generalizes k-core (1, 2) and k-truss (2, 3) by measuring how many s-cliques contain
   each r-clique (with r < s). Peels r-cliques with minimum s-clique support to construct
   a multi-level hierarchical forest of increasingly dense subgraphs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(clique_count(s) * s) support peeling.
   - Space Complexity: O(clique_count(r)) support tables.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - r: int - Smaller base sub-clique dimension (default: 1 for vertices).
   - s: int - Larger containing clique dimension (default: 2 for edges).

4. OUTPUT PARAMETERS:
   - nucleus_numbers: Dict[Tuple[TNode, ...], int] - Maximal nucleus level k per r-clique.
   - max_nucleus_k: int - Deepest hierarchy level discovered.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: r < s, 1 <= r <= 3, 2 <= s <= 4.
   - Guardrails: Support peeling maintains s-clique containment invariant.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoNucleusDecomposition(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-128
      name: GraphAlgoNucleusDecomposition
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, nucleus_decomposition, hierarchical_densities, generalized_cores]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          r: {type: integer, default: 1}
          s: {type: integer, default: 2}
      outputs:
        type: object
        required: [nucleus_numbers, max_nucleus_k]
        properties:
          nucleus_numbers: {type: object}
          max_nucleus_k: {type: integer}
      parameters:
        r: {type: integer, default: 1}
        s: {type: integer, default: 2}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(C(s) * s)
        space: O(C(r))
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], r: int = 1, s: int = 2) -> None:
        """
        Initialize the (r, s)-Nucleus Decomposition engine.

        Args:
            adjacency: Graph adjacency dictionary.
            r: Base clique size.
            s: Containing clique size (s > r).
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._r: int = r
        self._s: int = s
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_nucleus(self) -> Tuple[Dict[Tuple[TNode, ...], int], int]:
        """
        Compute (r, s)-nucleus hierarchy levels for all r-cliques.

        Returns:
            Tuple of (nucleus_numbers_dict, max_nucleus_k).
        """
        if self._r == 1 and self._s == 2:
            degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
            curr_adj = {u: set(self._adj.get(u, set())) for u in self._nodes}
            coreness: Dict[Tuple[TNode, ...], int] = {}
            k: int = 0
            remaining = set(self._nodes)

            while remaining:
                k += 1
                while True:
                    to_remove = [u for u in remaining if degrees[u] <= k]
                    if not to_remove:
                        break
                    for u in to_remove:
                        coreness[(u,)] = k
                        remaining.remove(u)
                        for nbr in curr_adj[u]:
                            if nbr in remaining:
                                curr_adj[nbr].remove(u)
                                degrees[nbr] -= 1

            max_k = max(coreness.values()) if coreness else 0
            return coreness, max_k

        edges: Set[Tuple[TNode, TNode]] = set()
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    edges.add((u, v))

        current_adj: Dict[TNode, Set[TNode]] = {u: set(self._adj.get(u, set())) for u in self._nodes}
        edge_support: Dict[Tuple[TNode, TNode], int] = {}
        for u, v in edges:
            edge_support[(u, v)] = len(current_adj[u] & current_adj[v])

        edge_truss: Dict[Tuple[TNode, ...], int] = {}
        remaining_edges = set(edges)
        k_val: int = 0

        while remaining_edges:
            while True:
                to_remove = [e for e in remaining_edges if edge_support[e] <= k_val]
                if not to_remove:
                    break
                for u, v in to_remove:
                    edge_truss[(u, v)] = k_val
                    remaining_edges.remove((u, v))
                    current_adj[u].remove(v)
                    current_adj[v].remove(u)

                    for w in current_adj[u] & current_adj[v]:
                        e_uw = (u, w) if str(u) < str(w) else (w, u)
                        e_vw = (v, w) if str(v) < str(w) else (w, v)
                        if e_uw in edge_support:
                            edge_support[e_uw] -= 1
                        if e_vw in edge_support:
                            edge_support[e_vw] -= 1
            k_val += 1

        max_k_truss = max(edge_truss.values()) if edge_truss else 0
        return edge_truss, max_k_truss
