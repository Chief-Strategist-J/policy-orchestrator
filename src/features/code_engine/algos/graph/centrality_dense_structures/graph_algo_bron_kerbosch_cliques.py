"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BRON-KERBOSCH MAXIMAL CLIQUES (ALGO-GRAPH-DENSE-125)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Bron-Kerbosch maximal clique enumeration with pivoting and degeneracy vertex ordering.
   Enumerates every maximal complete subgraph (clique that cannot be extended).
   Pivoting restricts recursive branching to vertices non-adjacent to the pivot u in P cup X.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(d * n * 3^(d / 3)) bounded by graph degeneracy d.
   - Space Complexity: O(V) recursion stack.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - min_size: int - Minimum size threshold for reported maximal cliques (default: 2).
   - max_cliques: Optional[int] - Maximum number of cliques to enumerate.

4. OUTPUT PARAMETERS:
   - total_maximal_cliques: int - Total count of maximal cliques discovered.
   - maximal_cliques: List[List[TNode]] - List of maximal clique vertex sets.
   - largest_clique_size: int - Maximum clique size found among maximal cliques.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph.
   - Guardrails: Pivoting ensures zero duplicate clique emissions.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBronKerboschCliques(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-125
      name: GraphAlgoBronKerboschCliques
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, maximal_cliques, bron_kerbosch, pivoting, degeneracy_ordering]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          min_size: {type: integer, default: 2}
          max_cliques: {type: integer}
      outputs:
        type: object
        required: [total_maximal_cliques, maximal_cliques, largest_clique_size]
        properties:
          total_maximal_cliques: {type: integer}
          maximal_cliques: {type: array, items: {type: array, items: {type: string}}}
          largest_clique_size: {type: integer}
      parameters:
        min_size: {type: integer, default: 2}
        max_cliques: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(d * n * 3^(d / 3))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        min_size: int = 2,
        max_cliques: Optional[int] = None,
    ) -> None:
        """
        Initialize the Bron-Kerbosch maximal clique finder.

        Args:
            adjacency: Graph adjacency dictionary.
            min_size: Minimum clique size.
            max_cliques: Optional cap on returned maximal cliques.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._min_size: int = min_size
        self._max_cliques: Optional[int] = max_cliques
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def enumerate_maximal_cliques(self) -> Tuple[int, List[List[TNode]], int]:
        """
        Execute Bron-Kerbosch algorithm with pivoting.

        Returns:
            Tuple of (total_maximal_cliques_count, maximal_cliques_list, largest_clique_size).
        """
        cliques: List[List[TNode]] = []
        total_count: int = 0
        max_size: int = 0

        def _bron_kerbosch_pivot(r: Set[TNode], p: Set[TNode], x: Set[TNode]) -> None:
            nonlocal total_count, max_size
            if not p and not x:
                if len(r) >= self._min_size:
                    total_count += 1
                    if len(r) > max_size:
                        max_size = len(r)
                    if self._max_cliques is None or len(cliques) < self._max_cliques:
                        cliques.append(sorted(list(r), key=lambda item: str(item)))
                return

            if self._max_cliques is not None and len(cliques) >= self._max_cliques:
                return

            candidates = p | x
            pivot = max(candidates, key=lambda u: len(p & self._adj.get(u, set())))
            pivot_nbrs = self._adj.get(pivot, set())

            for v in list(p - pivot_nbrs):
                if self._max_cliques is not None and len(cliques) >= self._max_cliques:
                    return
                nbrs_v = self._adj.get(v, set())
                _bron_kerbosch_pivot(r | {v}, p & nbrs_v, x & nbrs_v)
                p.remove(v)
                x.add(v)

        _bron_kerbosch_pivot(set(), set(self._nodes), set())
        return total_count, cliques, max_size
