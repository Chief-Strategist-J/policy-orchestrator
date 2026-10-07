"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: K-CLIQUE LISTING (ALGO-GRAPH-DENSE-124)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Chiba-Nishizeki / kClist recursive k-clique enumeration algorithm.
   Orders vertices by degeneracy orientation to prune recursion trees.
   Recursively enumerates all complete subgraphs of exactly k vertices without duplicates.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * m * (c / 2)^(k - 2)) bounded by graph degeneracy c.
   - Space Complexity: O(k + V) recursion candidate sets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - k: int - Clique size to enumerate (k >= 2).
   - max_cliques: Optional[int] - Maximum number of cliques to return before truncation.

4. OUTPUT PARAMETERS:
   - total_count: int - Total number of k-cliques discovered.
   - cliques: List[List[TNode]] - List of k-vertex sets forming complete subgraphs.
   - is_truncated: bool - True if enumeration was capped by max_cliques.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: k >= 2.
   - Guardrails: Capped enumeration budget prevents combinatorial blowups on dense instances.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoKCliqueListing(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-124
      name: GraphAlgoKCliqueListing
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, k_cliques, chiba_nishizeki, clique_enumeration]
      inputs:
        type: object
        required: [adjacency, k]
        properties:
          adjacency: {type: object}
          k: {type: integer}
          max_cliques: {type: integer}
      outputs:
        type: object
        required: [total_count, cliques, is_truncated]
        properties:
          total_count: {type: integer}
          cliques: {type: array, items: {type: array, items: {type: string}}}
          is_truncated: {type: boolean}
      parameters:
        k: {type: integer}
        max_cliques: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(k * m * (c / 2)^(k - 2))
        space: O(k + V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        k: int,
        max_cliques: Optional[int] = None,
    ) -> None:
        """
        Initialize the k-clique enumeration engine.

        Args:
            adjacency: Graph adjacency dictionary.
            k: Target clique size.
            max_cliques: Optional limit on enumerated cliques.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._k: int = k
        self._max_cliques: Optional[int] = max_cliques
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def list_cliques(self) -> Tuple[int, List[List[TNode]], bool]:
        """
        Enumerate all k-cliques using degeneracy-ordered candidate filtering.

        Returns:
            Tuple of (total_count, cliques_list, is_truncated_flag).
        """
        if self._k < 1 or len(self._nodes) < self._k:
            return 0, [], False

        if self._k == 1:
            cliques = [[u] for u in self._nodes]
            if self._max_cliques is not None and len(cliques) > self._max_cliques:
                return len(cliques), cliques[: self._max_cliques], True
            return len(cliques), cliques, False

        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        order = sorted(self._nodes, key=lambda u: (degrees[u], str(u)))
        rank = {u: i for i, u in enumerate(order)}

        forward_adj: Dict[TNode, List[TNode]] = {u: [] for u in self._nodes}
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if rank[v] > rank[u]:
                    forward_adj[u].append(v)

        cliques: List[List[TNode]] = []
        total_count: int = 0
        truncated: bool = False

        def _extend(clique: List[TNode], candidates: List[TNode]) -> None:
            nonlocal total_count, truncated
            if len(clique) == self._k:
                total_count += 1
                if self._max_cliques is None or len(cliques) < self._max_cliques:
                    cliques.append(list(clique))
                else:
                    truncated = True
                return

            for i, v in enumerate(candidates):
                if truncated and self._max_cliques is not None and len(cliques) >= self._max_cliques:
                    return
                clique.append(v)
                nbrs_v = self._adj.get(v, set())
                next_cand = [cand for cand in candidates[i + 1:] if cand in nbrs_v]
                if len(clique) + len(next_cand) >= self._k:
                    _extend(clique, next_cand)
                clique.pop()

        for u in self._nodes:
            if truncated and self._max_cliques is not None and len(cliques) >= self._max_cliques:
                break
            f_u = sorted(forward_adj[u], key=lambda x: rank[x])
            if 1 + len(f_u) >= self._k:
                _extend([u], f_u)

        return total_count, cliques, truncated
