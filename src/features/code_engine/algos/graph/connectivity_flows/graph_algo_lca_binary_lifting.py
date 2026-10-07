"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LOWEST COMMON ANCESTOR BINARY LIFTING (ALGO-GRAPH-TREE-67)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Lowest Common Ancestor (LCA) and tree distance query engine using Binary Lifting.
   Precomputes 2^k ancestor jump pointers for fast O(log V) LCA lookup and tree distance queries.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V log V) preprocessing, O(log V) per query.
   - Space Complexity: O(V log V) jump table.
   - Purity: Pure functional query, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Tree structure must be acyclic and connected.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLcaBinaryLifting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-67
      name: GraphAlgoLcaBinaryLifting
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, lca, binary_lifting, tree_distance, tree_hierarchy]
      inputs:
        type: object
        required: [tree_adjacency]
        properties:
          tree_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          root: {type: string}
      outputs:
        type: object
        properties:
          lca: {type: string}
          tree_distance: {type: integer}
      parameters:
        root: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V log V)
        space: O(V log V)
    ---
    """

    def __init__(self, tree_adjacency: Dict[TNode, List[TNode]], root: Optional[TNode] = None) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in tree_adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._root: TNode = root if root is not None else (self._nodes[0] if self._nodes else None)
        self._depth: Dict[TNode, int] = {}
        self._up: Dict[TNode, List[Optional[TNode]]] = {}
        self._max_log: int = 20

        if self._root is not None:
            self._preprocess()

    def _preprocess(self) -> None:
        for u in self._nodes:
            self._up[u] = [None] * self._max_log

        stack: List[Tuple[TNode, Optional[TNode], int]] = [(self._root, None, 0)]
        visited = set()

        while stack:
            u, parent, d = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            self._depth[u] = d
            self._up[u][0] = parent

            for i in range(1, self._max_log):
                prev_anc = self._up[u][i - 1]
                if prev_anc is not None:
                    self._up[u][i] = self._up[prev_anc][i - 1]
                else:
                    self._up[u][i] = None

            for v in self._adj.get(u, []):
                if v != parent and v not in visited:
                    stack.append((v, u, d + 1))

    def query_lca(self, u: TNode, v: TNode) -> Optional[TNode]:
        if u not in self._depth or v not in self._depth:
            return None

        if self._depth[u] < self._depth[v]:
            u, v = v, u

        diff = self._depth[u] - self._depth[v]
        for i in range(self._max_log):
            if (diff >> i) & 1:
                anc = self._up[u][i]
                if anc is not None:
                    u = anc

        if u == v:
            return u

        for i in range(self._max_log - 1, -1, -1):
            if self._up[u][i] != self._up[v][i]:
                anc_u = self._up[u][i]
                anc_v = self._up[v][i]
                if anc_u is not None and anc_v is not None:
                    u = anc_u
                    v = anc_v

        return self._up[u][0]

    def query_distance(self, u: TNode, v: TNode) -> int:
        lca = self.query_lca(u, v)
        if lca is None:
            return -1
        return self._depth[u] + self._depth[v] - 2 * self._depth[lca]
