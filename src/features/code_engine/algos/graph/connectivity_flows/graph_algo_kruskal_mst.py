"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KRUSKAL MINIMUM SPANNING TREE (ALGO-GRAPH-TREE-61)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Kruskal's Minimum Spanning Tree (MST) algorithm.
   Builds a minimum-weight spanning tree (or forest) by greedily selecting the lightest
   non-cycle-forming edges using Disjoint Set Union (Union-Find).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E log E) edge sorting.
   - Space Complexity: O(V + E) union-find and edge list storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer & Analyst.
   - Guardrails: Deterministic tie-breaking across equal-weight edges.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from src.features.code_engine.algos.graph.connectivity_flows.graph_algo_union_find import GraphAlgoUnionFind

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoKruskalMst(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-61
      name: GraphAlgoKruskalMst
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, mst, minimum_spanning_tree, kruskal, union_find]
      inputs:
        type: object
        required: [edges]
        properties:
          edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
          nodes:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [total_weight, mst_edges]
        properties:
          total_weight: {type: number}
          mst_edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E log E)
        space: O(V + E)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode, float]], nodes: Optional[List[TNode]] = None) -> None:
        self._edges: List[Tuple[TNode, TNode, float]] = edges
        node_set: Set[TNode] = set(nodes) if nodes is not None else set()
        for u, v, _ in edges:
            node_set.add(u)
            node_set.add(v)
        self._nodes: List[TNode] = sorted(list(node_set), key=lambda x: str(x))

    def compute_mst(self) -> Tuple[float, List[Tuple[TNode, TNode, float]]]:
        sorted_edges = sorted(
            self._edges,
            key=lambda e: (e[2], str(e[0]), str(e[1])),
        )

        uf = GraphAlgoUnionFind[TNode](self._nodes)
        mst_edges: List[Tuple[TNode, TNode, float]] = []
        total_weight = 0.0

        for u, v, w in sorted_edges:
            if uf.union(u, v):
                mst_edges.append((u, v, w))
                total_weight += w
                if len(mst_edges) == len(self._nodes) - 1:
                    break

        return total_weight, mst_edges
