"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SYMMETRY BREAKING SUBGRAPH SEARCH (ALGO-GRAPH-ENUM-233)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Symmetry Breaking Subgraph Search Engine.
   Generates canonical ordering predicates from the automorphism group Aut(P) of query
   patterns (via stabilizer chains), guaranteeing each isomorphic subgraph occurrence
   in the target graph is discovered exactly once without redundant overcounting.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: |Aut(P)|x reduction in search tree traversal space.
   - Space Complexity: O(V + M) target graph adjacency and recursion stack.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Target graph.

4. OUTPUT PARAMETERS:
   - `search_triangles_symmetry_broken()` (List[Tuple[TNode, TNode, TNode]]): Exactly 1 hit per triangle.
   - `search_squares_symmetry_broken()` (List[Tuple[TNode, TNode, TNode, TNode]]): Exactly 1 hit per 4-cycle C_4.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact non-redundant occurrence count matching combinatorial ground truth.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSymmetryBreakingSubgraphSearch(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENUM-233
      name: GraphAlgoSymmetryBreakingSubgraphSearch
      version: 1.0.0
      category: graph_enumeration
      capability_tags: [graph, enumeration, symmetry_breaking, automorphism, canonical_ordering, motifs]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        properties:
          triangle_count: {type: integer}
          c4_count: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M^{k/2})
        space: O(V + M)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize symmetry breaking search engine.

        Args:
            adjacency: Adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = set()

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))

    def search_triangles_symmetry_broken(self) -> List[Tuple[TNode, TNode, TNode]]:
        """
        Search 3-cycles with symmetry condition: id(u) < id(v) < id(w).

        Returns:
            List of unique triangle 3-tuples.
        """
        triangles: List[Tuple[TNode, TNode, TNode]] = []
        for i, u in enumerate(self._nodes):
            for v in self._adj[u]:
                if str(v) > str(u):
                    for w in self._adj[v]:
                        if str(w) > str(v) and w in self._adj[u]:
                            triangles.append((u, v, w))
        return triangles

    def search_squares_symmetry_broken(self) -> List[Tuple[TNode, TNode, TNode, TNode]]:
        """
        Search 4-cycles (C_4: u - v - w - x - u) with symmetry breaking:
        id(u) = min(u, v, w, x) and id(v) < id(x).

        Returns:
            List of canonical 4-cycle 4-tuples (u, v, w, x).
        """
        c4_list: List[Tuple[TNode, TNode, TNode, TNode]] = []

        for u in self._nodes:
            nbrs_u = [v for v in self._adj[u] if str(v) > str(u)]
            for i, v in enumerate(nbrs_u):
                for x in nbrs_u[i + 1:]:
                    common_w = self._adj[v].intersection(self._adj[x])
                    for w in common_w:
                        if w != u and str(w) > str(u):
                            c4_list.append((u, v, w, x))

        return c4_list
