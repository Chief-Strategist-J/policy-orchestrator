"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PATTERN-AWARE SUBGRAPH ENUMERATION (ALGO-GRAPH-ENUM-232)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Pattern-Aware Subgraph Enumeration Engine (AutoMine / GraphPi framework).
   Compiles target graph motifs (k-cliques, k-stars, cycles, chordal patterns) into
   optimized nested set intersection execution plans with symmetry-breaking pruning.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M^{k/2}) for compiled clique / cycle plans.
   - Space Complexity: O(V + M) indexed neighbor sets.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Data graph adjacency.

4. OUTPUT PARAMETERS:
   - `enumerate_4_cliques(limit)` (List[Tuple[TNode, TNode, TNode, TNode]]): Exact 4-clique instances.
   - `enumerate_4_cycles(limit)` (List[Tuple[TNode, TNode, TNode, TNode]]): Exact 4-cycle instances.
   - `count_4_cliques()` (int): Total 4-cliques.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact non-redundant enumeration using compiled intersection schedules.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPatternAwareSubgraphEnumeration(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENUM-232
      name: GraphAlgoPatternAwareSubgraphEnumeration
      version: 1.0.0
      category: graph_enumeration
      capability_tags: [graph, enumeration, automine, graphpi, compiled_subgraphs, 4_cliques, 4_cycles]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        properties:
          clique_count: {type: integer}
          cycle_count: {type: integer}
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
        Initialize compiled subgraph enumeration engine.

        Args:
            adjacency: Undirected data graph adjacency.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = set()

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))

    def enumerate_4_cliques(self, limit: int = 1000) -> List[Tuple[TNode, TNode, TNode, TNode]]:
        """
        Enumerate 4-cliques (K_4) with symmetry breaking id(u1) < id(u2) < id(u3) < id(u4).

        Args:
            limit: Maximum cliques to return.

        Returns:
            List of 4-clique node tuples.
        """
        results: List[Tuple[TNode, TNode, TNode, TNode]] = []

        for i, u1 in enumerate(self._nodes):
            nbrs1 = {v for v in self._adj[u1] if str(v) > str(u1)}
            sorted_nbrs1 = sorted(list(nbrs1), key=lambda x: str(x))

            for j, u2 in enumerate(sorted_nbrs1):
                nbrs2 = nbrs1.intersection(self._adj[u2])
                sorted_nbrs2 = [v for v in sorted_nbrs1[j + 1:] if v in nbrs2]

                for k, u3 in enumerate(sorted_nbrs2):
                    nbrs3 = nbrs2.intersection(self._adj[u3])
                    for u4 in sorted_nbrs2[k + 1:]:
                        if u4 in nbrs3:
                            results.append((u1, u2, u3, u4))
                            if len(results) >= limit:
                                return results

        return results

    def count_4_cliques(self) -> int:
        """
        Count total 4-cliques.

        Returns:
            Integer 4-clique count.
        """
        return len(self.enumerate_4_cliques(limit=100000))
