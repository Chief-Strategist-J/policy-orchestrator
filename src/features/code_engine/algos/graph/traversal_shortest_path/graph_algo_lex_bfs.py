"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LEXICOGRAPHIC BFS (LEX-BFS) (ALGO-GRAPH-TRV-16)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Lexicographic Breadth-First Search (LexBFS) uses partition refinement to
   break traversal ties based on the chronological sequence of visited neighbors.
   Generates elimination orderings for chordal graph recognition, interval graph
   isomorphism, and optimal vertex coloring.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) using doubly-linked partition refinement.
   - Space Complexity: O(V + E) for vertex sets and partition buckets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Outputs: LexBFS ordering and Perfect Elimination Ordering (PEO) verification.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Set, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoLexBfs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-16
      name: GraphAlgoLexBfs
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, lex_bfs, chordal_graph, partition_refinement]
      inputs:
        type: object
        required: [nodes, adjacency_list]
        properties:
          nodes:
            type: array
            items: {type: string}
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [ordering, is_peo, chordal_graph_certified]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V + E)
    ---
    """

    @staticmethod
    def compute(
        nodes: List[str],
        adjacency_list: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        if not all_nodes:
            return {
                "ordering": [],
                "is_peo": True,
                "chordal_graph_certified": True,
            }

        adj_set: Dict[str, Set[str]] = {
            n: set(adjacency_list.get(n, [])) for n in all_nodes
        }

        partitions: List[List[str]] = [list(all_nodes)]
        ordering: List[str] = []

        while partitions:
            v = partitions[0].pop()
            if not partitions[0]:
                partitions.pop(0)
            ordering.append(v)

            v_neighbors = adj_set[v]
            new_partitions: List[List[str]] = []

            for p in partitions:
                intersect = [u for u in p if u in v_neighbors]
                difference = [u for u in p if u not in v_neighbors]

                if intersect:
                    new_partitions.append(intersect)
                if difference:
                    new_partitions.append(difference)

            partitions = new_partitions

        rev_order = ordering[::-1]
        order_pos = {node: idx for idx, node in enumerate(rev_order)}
        is_peo = True

        for i, u in enumerate(rev_order):
            higher_neighbors = [
                v for v in adj_set[u] if order_pos.get(v, -1) > i
            ]
            if higher_neighbors:
                min_higher = min(higher_neighbors, key=lambda v: order_pos[v])
                min_higher_neighbors = adj_set[min_higher]
                for other in higher_neighbors:
                    if other != min_higher and other not in min_higher_neighbors:
                        is_peo = False
                        break
            if not is_peo:
                break

        return {
            "ordering": ordering,
            "perfect_elimination_ordering": rev_order,
            "is_peo": is_peo,
            "chordal_graph_certified": is_peo,
            "num_nodes": len(all_nodes),
        }
