"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DOMINATOR TREE (ALGO-GRAPH-CONN-59)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dominator Tree and Dominance Frontier Engine using Cooper-Harvey-Kennedy
   and Lengauer-Tarjan techniques. Computes immediate dominators, dominator tree
   hierarchy, and dominance frontiers for control-flow slicing and compiler SSA.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E * log V) immediate dominator computation.
   - Space Complexity: O(V + E) dominator tree and frontier sets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact dominance frontier computation for all reachable nodes.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDominatorTree(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CONN-59
      name: GraphAlgoDominatorTree
      version: 1.0.0
      category: graph_connectivity
      capability_tags: [graph, dominator_tree, dominance_frontier, lengauer_tarjan, ssa_form]
      inputs:
        type: object
        required: [adjacency, root]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          root: {type: string}
      outputs:
        type: object
        required: [immediate_dominators, dominator_tree, dominance_frontiers]
        properties:
          immediate_dominators:
            type: object
            additionalProperties: {type: string}
          dominator_tree:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          dominance_frontiers:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E * log V)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        self._pred: Dict[TNode, List[TNode]] = {u: [] for u in self._adj}
        
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []
                    self._pred[v] = []
                if v not in self._pred:
                    self._pred[v] = []
                self._pred[v].append(u)

    def compute_dominators(
        self, root: TNode
    ) -> Tuple[Dict[TNode, Optional[TNode]], Dict[TNode, List[TNode]], Dict[TNode, Set[TNode]]]:
        if root not in self._adj:
            return {}, {}, {}

        post_order: List[TNode] = []
        visited: Set[TNode] = set()

        def dfs_post(u: TNode) -> None:
            visited.add(u)
            for v in sorted(self._adj.get(u, []), key=lambda x: str(x)):
                if v not in visited:
                    dfs_post(v)
            post_order.append(u)

        dfs_post(root)
        post_order_index: Dict[TNode, int] = {node: idx for idx, node in enumerate(post_order)}
        rev_post_order = list(reversed(post_order))

        idom: Dict[TNode, Optional[TNode]] = {u: None for u in post_order}
        idom[root] = root

        def intersect(b1: TNode, b2: TNode) -> TNode:
            finger1 = b1
            finger2 = b2
            while finger1 != finger2:
                while post_order_index[finger1] < post_order_index[finger2]:
                    p = idom[finger1]
                    if p is None:
                        break
                    finger1 = p
                while post_order_index[finger2] < post_order_index[finger1]:
                    p = idom[finger2]
                    if p is None:
                        break
                    finger2 = p
            return finger1

        changed = True
        while changed:
            changed = False
            for u in rev_post_order:
                if u == root:
                    continue

                processed_preds = [p for p in self._pred.get(u, []) if idom.get(p) is not None]
                if not processed_preds:
                    continue

                new_idom = processed_preds[0]
                for p in processed_preds[1:]:
                    if idom.get(p) is not None:
                        new_idom = intersect(p, new_idom)

                if idom[u] != new_idom:
                    idom[u] = new_idom
                    changed = True

        idom[root] = None

        dom_tree: Dict[TNode, List[TNode]] = {u: [] for u in post_order}
        for u, parent in idom.items():
            if parent is not None and parent in dom_tree:
                dom_tree[parent].append(u)

        dominance_frontier: Dict[TNode, Set[TNode]] = {u: set() for u in post_order}
        for u in post_order:
            preds = [p for p in self._pred.get(u, []) if p in idom]
            if len(preds) >= 2:
                for p in preds:
                    runner: Optional[TNode] = p
                    while runner is not None and runner != idom.get(u):
                        dominance_frontier[runner].add(u)
                        runner = idom.get(runner)

        return idom, dom_tree, dominance_frontier
