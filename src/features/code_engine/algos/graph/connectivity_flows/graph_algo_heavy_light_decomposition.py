"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HEAVY-LIGHT DECOMPOSITION (ALGO-GRAPH-TREE-68)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Heavy-Light Decomposition (HLD) Engine.
   Decomposes arbitrary rooted trees into logarithmic heavy-light chains,
   enabling O(log^2 V) path aggregate queries and O(1) subtree segment interval queries.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V) build, O(log^2 V) path query.
   - Space Complexity: O(V) chain indices and segment boundaries.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Contiguous segment numbering for all heavy path chains.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHeavyLightDecomposition(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-68
      name: GraphAlgoHeavyLightDecomposition
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, hld, heavy_light_decomposition, tree_paths, subtree_queries]
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
          path_segments:
            type: array
            items:
              type: array
              items: [{type: integer}, {type: integer}]
          subtree_interval:
            type: array
            items: [{type: integer}, {type: integer}]
      parameters:
        root: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V)
        space: O(V)
    ---
    """

    def __init__(self, tree_adjacency: Dict[TNode, List[TNode]], root: Optional[TNode] = None) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in tree_adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._root: Optional[TNode] = root if root is not None else (self._nodes[0] if self._nodes else None)
        
        self._parent: Dict[TNode, Optional[TNode]] = {}
        self._depth: Dict[TNode, int] = {}
        self._heavy: Dict[TNode, Optional[TNode]] = {}
        self._head: Dict[TNode, TNode] = {}
        self._pos: Dict[TNode, int] = {}
        self._size: Dict[TNode, int] = {}
        self._cur_pos: int = 0

        if self._root is not None:
            self._decompose()

    def _decompose(self) -> None:
        if self._root is None:
            return
        root: TNode = self._root
        order: List[TNode] = []
        stack: List[Tuple[TNode, Optional[TNode], int]] = [(root, None, 0)]
        visited = set()

        while stack:
            u, p, d = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            order.append(u)
            self._parent[u] = p
            self._depth[u] = d

            for v in self._adj.get(u, []):
                if v != p and v not in visited:
                    stack.append((v, u, d + 1))

        for u in reversed(order):
            sz = 1
            max_c_sz = 0
            heavy_child: Optional[TNode] = None
            p = self._parent[u]

            for v in self._adj.get(u, []):
                if v != p:
                    c_sz = self._size.get(v, 1)
                    sz += c_sz
                    if c_sz > max_c_sz:
                        max_c_sz = c_sz
                        heavy_child = v

            self._size[u] = sz
            self._heavy[u] = heavy_child

        self._cur_pos = 0
        hld_stack: List[Tuple[TNode, TNode]] = [(self._root, self._root)]

        while hld_stack:
            u, h = hld_stack.pop()
            self._head[u] = h
            self._pos[u] = self._cur_pos
            self._cur_pos += 1

            p = self._parent[u]
            light_children = [
                v for v in self._adj.get(u, []) if v != p and v != self._heavy.get(u)
            ]
            for v in light_children:
                hld_stack.append((v, v))

            heavy_child = self._heavy.get(u)
            if heavy_child is not None:
                hld_stack.append((heavy_child, h))

    def get_path_segments(self, u: TNode, v: TNode) -> List[Tuple[int, int]]:
        segments: List[Tuple[int, int]] = []
        while self._head[u] != self._head[v]:
            if self._depth[self._head[u]] > self._depth[self._head[v]]:
                segments.append((self._pos[self._head[u]], self._pos[u]))
                p = self._parent[self._head[u]]
                if p is None:
                    break
                u = p
            else:
                segments.append((self._pos[self._head[v]], self._pos[v]))
                p = self._parent[self._head[v]]
                if p is None:
                    break
                v = p

        if self._depth[u] > self._depth[v]:
            u, v = v, u
        segments.append((self._pos[u], self._pos[v]))
        return segments

    def get_subtree_interval(self, u: TNode) -> Tuple[int, int]:
        return self._pos[u], self._pos[u] + self._size[u] - 1
