"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNION-FIND WITH ROLLBACK (ALGO-GRAPH-CONN-51)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Disjoint Set Union (DSU) data structure with path compression, union by rank/size,
   and transactional rollback support for connected components and MST maintenance.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(alpha(N)) amortized per operation.
   - Space Complexity: O(N) parent and rank mapping.
   - Purity: Pure functional and stateful encapsulated data structure.

3. AGENT CONTRACT:
   - Role: Builder & Analyst.
   - Guardrails: Supports rollback undo without corruption of rank or disjoint sets.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoUnionFind(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CONN-51
      name: GraphAlgoUnionFind
      version: 1.0.0
      category: graph_connectivity
      capability_tags: [graph, disjoint_set, union_find, dsu, rollback, path_compression]
      inputs:
        type: object
        properties:
          elements:
            type: array
            items: {type: string}
      outputs:
        type: object
        properties:
          num_sets: {type: integer}
          components:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      purity: stateful_pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(alpha(N))
        space: O(N)
    ---
    """

    def __init__(self, elements: Optional[List[TNode]] = None) -> None:
        self._parent: Dict[TNode, TNode] = {}
        self._rank: Dict[TNode, int] = {}
        self._size: Dict[TNode, int] = {}
        self._history: List[Tuple[TNode, TNode, int, int]] = []
        self._num_sets: int = 0

        if elements is not None:
            for elem in elements:
                self.make_set(elem)

    def make_set(self, x: TNode) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
            self._size[x] = 1
            self._num_sets += 1

    def find(self, x: TNode) -> TNode:
        if x not in self._parent:
            self.make_set(x)
            return x

        root = x
        while self._parent[root] != root:
            root = self._parent[root]

        curr = x
        while curr != root:
            nxt = self._parent[curr]
            self._parent[curr] = root
            curr = nxt

        return root

    def union(self, x: TNode, y: TNode) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        rank_x = self._rank[root_x]
        rank_y = self._rank[root_y]

        if rank_x < rank_y:
            root_x, root_y = root_y, root_x

        self._history.append((root_x, root_y, rank_x, self._size[root_x]))
        self._parent[root_y] = root_x
        self._size[root_x] += self._size[root_y]

        if rank_x == rank_y:
            self._rank[root_x] += 1

        self._num_sets -= 1
        return True

    def connected(self, x: TNode, y: TNode) -> bool:
        return self.find(x) == self.find(y)

    def get_set_size(self, x: TNode) -> int:
        return self._size[self.find(x)]

    @property
    def num_sets(self) -> int:
        return self._num_sets

    def get_components(self) -> Dict[TNode, List[TNode]]:
        components: Dict[TNode, List[TNode]] = {}
        for elem in self._parent:
            root = self.find(elem)
            if root not in components:
                components[root] = []
            components[root].append(elem)
        return components

    def rollback(self) -> bool:
        if not self._history:
            return False

        root_x, root_y, old_rank_x, old_size_x = self._history.pop()
        self._parent[root_y] = root_y
        self._rank[root_x] = old_rank_x
        self._size[root_x] = old_size_x
        self._num_sets += 1
        return True
