"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BORUVKA MINIMUM SPANNING TREE (ALGO-GRAPH-TREE-63)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Boruvka's parallel component-merging algorithm for minimum spanning trees.
   Constructs an MST via simultaneous component-level contraction rounds,
   where each connected component finds its minimal outgoing edge in parallel.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E log V) across at most log V contraction phases.
   - Space Complexity: O(V + E) union-find and edge list storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guardrails: Strict deterministic tie-breaking ensures cycle-free contraction.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from src.features.code_engine.algos.graph.connectivity_flows.graph_algo_union_find import GraphAlgoUnionFind

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBoruvkaMst(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-63
      name: GraphAlgoBoruvkaMst
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, mst, minimum_spanning_tree, boruvka, parallel_contraction]
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
        time: O(E log V)
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
        n = len(self._nodes)
        if n <= 1:
            return 0.0, []

        uf = GraphAlgoUnionFind[TNode](self._nodes)
        mst_edges: List[Tuple[TNode, TNode, float]] = []
        total_weight = 0.0
        num_trees = n

        while num_trees > 1:
            cheapest: Dict[TNode, Tuple[TNode, TNode, float]] = {}

            for u, v, w in self._edges:
                root_u = uf.find(u)
                root_v = uf.find(v)

                if root_u != root_v:
                    if root_u not in cheapest or w < cheapest[root_u][2]:
                        cheapest[root_u] = (u, v, w)
                    if root_v not in cheapest or w < cheapest[root_v][2]:
                        cheapest[root_v] = (u, v, w)

            if not cheapest:
                break

            added_in_round = False
            for root, (u, v, w) in sorted(cheapest.items(), key=lambda item: str(item[0])):
                if uf.union(u, v):
                    mst_edges.append((u, v, w))
                    total_weight += w
                    num_trees -= 1
                    added_in_round = True

            if not added_in_round:
                break

        return total_weight, mst_edges
