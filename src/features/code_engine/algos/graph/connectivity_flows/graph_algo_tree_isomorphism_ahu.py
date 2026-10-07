"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TREE ISOMORPHISM AHU (ALGO-GRAPH-TREE-72)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Aho-Hopcroft-Ullman (AHU) Tree Isomorphism Algorithm.
   Determines structural isomorphism between rooted or unrooted trees in linear time
   via canonical bottom-up recursive subtree signature encoding.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V log V) tree center detection and canonical encoding.
   - Space Complexity: O(V) signature string representations.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact canonical isomorphism certificate for identical graph topologies.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTreeIsomorphismAhu(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-72
      name: GraphAlgoTreeIsomorphismAhu
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, tree_isomorphism, ahu_algorithm, canonical_encoding, tree_centers]
      inputs:
        type: object
        required: [tree1_adj, tree2_adj]
        properties:
          tree1_adj:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          tree2_adj:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [are_isomorphic, canonical_representation1, canonical_representation2]
        properties:
          are_isomorphic: {type: boolean}
          canonical_representation1: {type: string}
          canonical_representation2: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V log V)
        space: O(V)
    ---
    """

    @staticmethod
    def are_isomorphic(
        tree1_adj: Dict[TNode, List[TNode]],
        tree2_adj: Dict[TNode, List[TNode]],
    ) -> bool:
        cert1 = GraphAlgoTreeIsomorphismAhu.get_canonical_representation(tree1_adj)
        cert2 = GraphAlgoTreeIsomorphismAhu.get_canonical_representation(tree2_adj)
        return cert1 == cert2

    @staticmethod
    def find_tree_centers(tree_adj: Dict[TNode, List[TNode]]) -> List[TNode]:
        nodes = list(tree_adj.keys())
        n = len(nodes)
        if n <= 2:
            return sorted(nodes, key=lambda x: str(x))

        degree: Dict[TNode, int] = {u: len(tree_adj[u]) for u in nodes}
        leaves: deque[TNode] = deque([u for u in nodes if degree[u] <= 1])
        removed_count = 0

        while n - removed_count > 2:
            leaf_count = len(leaves)
            removed_count += leaf_count
            for _ in range(leaf_count):
                u = leaves.popleft()
                for v in tree_adj.get(u, []):
                    degree[v] -= 1
                    if degree[v] == 1:
                        leaves.append(v)

        return sorted(list(leaves), key=lambda x: str(x))

    @staticmethod
    def encode_rooted_tree(tree_adj: Dict[TNode, List[TNode]], root: TNode) -> str:
        def _encode(u: TNode, parent: Optional[TNode]) -> str:
            child_codes: List[str] = []
            for v in tree_adj.get(u, []):
                if v != parent:
                    child_codes.append(_encode(v, u))
            child_codes.sort()
            return "(" + "".join(child_codes) + ")"

        return _encode(root, None)

    @staticmethod
    def get_canonical_representation(tree_adj: Dict[TNode, List[TNode]]) -> str:
        centers = GraphAlgoTreeIsomorphismAhu.find_tree_centers(tree_adj)
        if not centers:
            return "()"
        encodings = [GraphAlgoTreeIsomorphismAhu.encode_rooted_tree(tree_adj, c) for c in centers]
        return min(encodings)
