"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TREE DP REROOTING (ALGO-GRAPH-TREE-73)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tree Dynamic Programming with Rerooting.
   Computes all-root tree aggregates (e.g. sum of distances, eccentricities) in linear O(V) time
   using a two-pass downward (bottom-up) and upward (top-down rerooting) dynamic programming approach.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V) two-pass traversal.
   - Space Complexity: O(V) subtree size and distance accumulators.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact distance sum computation for all tree vertices as candidate roots.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTreeDpRerooting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-73
      name: GraphAlgoTreeDpRerooting
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, tree_dp, rerooting, sum_of_distances, all_roots_aggregation]
      inputs:
        type: object
        required: [tree_adjacency]
        properties:
          tree_adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: array
                items: [{type: string}, {type: number}]
      outputs:
        type: object
        required: [distances_sum_per_root]
        properties:
          distances_sum_per_root:
            type: object
            additionalProperties: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V)
        space: O(V)
    ---
    """

    def __init__(self, tree_adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {
            u: list(edges) for u, edges in tree_adjacency.items()
        }
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))

    def compute_sum_of_distances(self) -> Dict[TNode, float]:
        if not self._nodes:
            return {}

        root = self._nodes[0]
        count: Dict[TNode, int] = {u: 1 for u in self._nodes}
        ans: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
        n = len(self._nodes)

        order: List[TNode] = []
        parent: Dict[TNode, Optional[TNode]] = {root: None}
        edge_to_parent: Dict[TNode, float] = {root: 0.0}
        stack = [root]
        visited = {root}

        while stack:
            u = stack.pop()
            order.append(u)
            for v, w in self._adj.get(u, []):
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    edge_to_parent[v] = w
                    stack.append(v)

        for u in reversed(order):
            for v, w in self._adj.get(u, []):
                if v != parent[u]:
                    count[u] += count[v]
                    ans[u] += ans[v] + count[v] * w

        for u in order:
            p = parent[u]
            if p is not None:
                w = edge_to_parent[u]
                ans[u] = ans[p] + (n - 2 * count[u]) * w

        return ans
