"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PRIM MINIMUM SPANNING TREE (ALGO-GRAPH-TREE-62)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Prim's algorithm for minimum spanning tree construction.
   Grows an MST from an arbitrary root vertex by greedily adding
   the lightest frontier edge connected to the visited tree.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E log V) binary heap priority queue.
   - Space Complexity: O(V + E) priority queue and visited sets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Preconditions: Adjacency represents undirected non-negative weighted graph.
================================================================================
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPrimMst(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-62
      name: GraphAlgoPrimMst
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, mst, minimum_spanning_tree, prim, priority_queue]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: array
                items: [{type: string}, {type: number}]
          start_node: {type: string}
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
      parameters:
        start_node: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E log V)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {
            u: list(edges) for u, edges in adjacency.items()
        }
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def compute_mst(self, start_node: Optional[TNode] = None) -> Tuple[float, List[Tuple[TNode, TNode, float]]]:
        nodes = sorted(list(self._adj.keys()), key=lambda x: str(x))
        if not nodes:
            return 0.0, []

        start = start_node if start_node is not None else nodes[0]
        visited: Set[TNode] = {start}
        mst_edges: List[Tuple[TNode, TNode, float]] = []
        total_weight = 0.0

        pq: List[Tuple[float, str, str, TNode, TNode]] = []
        for v, w in self._adj.get(start, []):
            heapq.heappush(pq, (w, str(start), str(v), start, v))

        while pq and len(visited) < len(nodes):
            w, _, _, u, v = heapq.heappop(pq)
            if v in visited:
                continue

            visited.add(v)
            mst_edges.append((u, v, w))
            total_weight += w

            for nxt, nxt_w in self._adj.get(v, []):
                if nxt not in visited:
                    heapq.heappush(pq, (nxt_w, str(v), str(nxt), v, nxt))

        return total_weight, mst_edges
