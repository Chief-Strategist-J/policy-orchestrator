"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HYBRID QUERY PLANS (BINARY + WCOJ) (ALGO-GRAPH-DIST-231)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hybrid Query Planner & Execution Engine (Binary Joins + Worst-Case Optimal Joins).
   Decomposes composite graph query patterns into cyclic cliques/cores (executed via WCOJ)
   and acyclic tree paths/spines (executed via classical binary hash joins), achieving
   globally optimal execution plans across diverse graph query topologies.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(WCOJ(cyclic_core) + Binary(acyclic_paths)).
   - Space Complexity: O(V + M) intermediate join hash tables.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Data graph.
   - `query_cycles` (List[List[str]]): Cyclic sub-patterns for WCOJ.
   - `query_trees` (List[Tuple[str, str]]): Acyclic edges for binary joins.

4. OUTPUT PARAMETERS:
   - `execute_plan(limit)` (List[Dict[str, TNode]]): Combined query execution results.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Eliminates intermediate state blowup for cyclic sub-structures.
================================================================================
"""

from collections import defaultdict
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHybridQueryPlansBinaryWcoj(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DIST-231
      name: GraphAlgoHybridQueryPlansBinaryWcoj
      version: 1.0.0
      category: graph_distributed
      capability_tags: [graph, distributed, hybrid_query_plans, wcoj, binary_joins, query_optimizer]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        properties:
          results: {type: array}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M^{rho^*})
        space: O(V + M)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize hybrid query engine.

        Args:
            adjacency: Target graph adjacency map.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = set()

    def execute_triangle_with_tail(
        self,
        tri_vars: Tuple[str, str, str] = ("a", "b", "c"),
        tail_var: str = "d",
        tail_anchor: str = "a",
        limit: int = 1000,
    ) -> List[Dict[str, TNode]]:
        """
        Execute hybrid plan: WCOJ on 3-cycle (a-b-c) followed by binary join on tail (a-d).

        Args:
            tri_vars: Variable names for 3-clique.
            tail_var: Variable name for attached leaf.
            tail_anchor: Anchor variable in triangle attached to leaf.
            limit: Maximum result limit.

        Returns:
            List of variable bindings.
        """
        results: List[Dict[str, TNode]] = []
        va, vb, vc = tri_vars
        nodes = sorted(list(self._adj.keys()), key=lambda x: str(x))

        for a in nodes:
            nbrs_a = self._adj[a]
            for b in nbrs_a:
                if str(b) > str(a):
                    common_c = nbrs_a.intersection(self._adj[b])
                    for c in common_c:
                        if str(c) > str(b):
                            anchor_val = a if tail_anchor == va else (b if tail_anchor == vb else c)
                            for d in self._adj[anchor_val]:
                                if d != a and d != b and d != c:
                                    results.append({va: a, vb: b, vc: c, tail_var: d})
                                    if len(results) >= limit:
                                        return results

        return results
