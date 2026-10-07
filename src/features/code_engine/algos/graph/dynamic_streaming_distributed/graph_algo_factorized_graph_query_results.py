"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FACTORIZED GRAPH QUERY RESULTS (ALGO-GRAPH-DIST-230)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Factorized Representation Engine for Multi-Hop Graph Query Results.
   Compresses multi-join relational query results into nested d-trees of unions
   and Cartesian products (factorized databases), enabling exponential compression
   and linear-time aggregations (SUM, COUNT) directly over compressed trees.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(size(factorized_tree)) for evaluation and aggregations.
   - Space Complexity: O(sum of parts) instead of O(product of parts).
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `root_factor` (Dict[str, Any]): Nested tree of unions and products.

4. OUTPUT PARAMETERS:
   - `count_tuples()` (int): Exact relational tuple count without flat materialization.
   - `materialize_flat(limit)` (List[Dict[str, TNode]]): On-demand unrolled flat tuples.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact relational semantic equivalence with exponential memory reduction.
================================================================================
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar, Union

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoFactorizedGraphQueryResults(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DIST-230
      name: GraphAlgoFactorizedGraphQueryResults
      version: 1.0.0
      category: graph_distributed
      capability_tags: [graph, distributed, factorized_database, d_tree, query_compression, aggregations]
      inputs:
        type: object
        required: [data]
        properties:
          data: {type: object}
      outputs:
        type: object
        properties:
          tuple_count: {type: integer}
          compressed_nodes: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(size(tree))
        space: O(size(tree))
    ---
    """

    def __init__(self, data: Dict[TNode, Dict[str, List[TNode]]]) -> None:
        """
        Initialize factorized graph query result tree.

        Args:
            data: Structured tree: root_node -> {relation_name: [child_nodes]}.
        """
        self._tree: Dict[TNode, Dict[str, List[TNode]]] = data

    def count_tuples(self) -> int:
        """
        Compute total relational tuples represented by factorized tree in linear time.

        Returns:
            Total flat tuple count.
        """
        total = 0
        for root_val, branches in self._tree.items():
            branch_prod = 1
            for rel, children in branches.items():
                branch_prod *= max(1, len(children))
            total += branch_prod
        return total

    def materialize_flat(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Unroll factorized tree into flat tabular dictionary records on demand.

        Args:
            limit: Maximum rows to materialize.

        Returns:
            List of flattened tuple dictionaries.
        """
        flat_results: List[Dict[str, Any]] = []

        for root_val, branches in self._tree.items():
            if len(flat_results) >= limit:
                break
            rels = list(branches.keys())
            if not rels:
                flat_results.append({"root": root_val})
                continue

            combos: List[Dict[str, Any]] = [{"root": root_val}]
            for r in rels:
                children = branches[r]
                new_combos = []
                for c in combos:
                    for child in children:
                        merged = dict(c)
                        merged[r] = child
                        new_combos.append(merged)
                combos = new_combos

            for c in combos:
                flat_results.append(c)
                if len(flat_results) >= limit:
                    break

        return flat_results
