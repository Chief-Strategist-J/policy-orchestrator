"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CENTROID DECOMPOSITION (ALGO-GRAPH-TREE-69)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Centroid Decomposition Engine.
   Recursively partitions trees at their center of mass (centroids), building a balanced
   hierarchical Centroid Tree of depth at most O(log V) for divide-and-conquer path counting.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V log V) total decomposition work.
   - Space Complexity: O(V) centroid hierarchy storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Tree height bounded by log2(V).
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCentroidDecomposition(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-69
      name: GraphAlgoCentroidDecomposition
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, centroid_decomposition, tree_divide_and_conquer, path_counting]
      inputs:
        type: object
        required: [tree_adjacency]
        properties:
          tree_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [root_centroid, centroid_tree, centroid_parents]
        properties:
          root_centroid: {type: string}
          centroid_tree:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          centroid_parents:
            type: object
            additionalProperties: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V log V)
        space: O(V)
    ---
    """

    def __init__(self, tree_adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in tree_adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

        self._removed: Set[TNode] = set()
        self._subtree_size: Dict[TNode, int] = {}
        self._centroid_parent: Dict[TNode, Optional[TNode]] = {}
        self._centroid_tree: Dict[TNode, List[TNode]] = {u: [] for u in self._adj}
        self._root_centroid: Optional[TNode] = None

    def build_centroid_tree(self) -> Tuple[Optional[TNode], Dict[TNode, List[TNode]], Dict[TNode, Optional[TNode]]]:
        nodes = sorted(list(self._adj.keys()), key=lambda x: str(x))
        if not nodes:
            return None, {}, {}

        self._root_centroid = self._decompose(nodes[0], None)
        return self._root_centroid, self._centroid_tree, self._centroid_parent

    def _get_sizes(self, u: TNode, parent: Optional[TNode]) -> int:
        sz = 1
        for v in self._adj.get(u, []):
            if v != parent and v not in self._removed:
                sz += self._get_sizes(v, u)
        self._subtree_size[u] = sz
        return sz

    def _find_centroid(self, u: TNode, parent: Optional[TNode], total_size: int) -> TNode:
        for v in self._adj.get(u, []):
            if v != parent and v not in self._removed:
                if self._subtree_size[v] > total_size // 2:
                    return self._find_centroid(v, u, total_size)
        return u

    def _decompose(self, entry_node: TNode, parent_centroid: Optional[TNode]) -> TNode:
        total_sz = self._get_sizes(entry_node, None)
        centroid = self._find_centroid(entry_node, None, total_sz)

        self._removed.add(centroid)
        self._centroid_parent[centroid] = parent_centroid

        if parent_centroid is not None:
            self._centroid_tree[parent_centroid].append(centroid)

        for v in self._adj.get(centroid, []):
            if v not in self._removed:
                self._decompose(v, centroid)

        return centroid
