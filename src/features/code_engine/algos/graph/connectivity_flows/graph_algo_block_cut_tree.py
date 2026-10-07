"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BLOCK-CUT TREE (ALGO-GRAPH-CONN-54)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Biconnected components extraction and Block-Cut Tree structural decomposition.
   Decomposes an undirected graph into maximal biconnected components (blocks)
   and articulation points, forming a bipartite tree.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) single DFS pass with edge stack.
   - Space Complexity: O(V + E) block and tree adjacency.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Complete tree representation connecting cut vertices and blocks.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBlockCutTree(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CONN-54
      name: GraphAlgoBlockCutTree
      version: 1.0.0
      category: graph_connectivity
      capability_tags: [graph, biconnected_components, block_cut_tree, 2_vertex_connected]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [blocks, articulation_points, tree_adjacency]
        properties:
          blocks:
            type: array
            items:
              type: array
              items: {type: string}
          articulation_points:
            type: array
            items: {type: string}
          tree_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def decompose(self) -> Tuple[List[Set[TNode]], Set[TNode], Dict[str, List[str]]]:
        discovery: Dict[TNode, int] = {}
        low: Dict[TNode, int] = {}
        parent: Dict[TNode, Optional[TNode]] = {}
        articulation_points: Set[TNode] = set()
        blocks: List[Set[TNode]] = []
        edge_stack: List[Tuple[TNode, TNode]] = []
        timer = 0

        for node in sorted(self._adj.keys(), key=lambda x: str(x)):
            if node in discovery:
                continue

            stack: List[Tuple[TNode, int]] = [(node, 0)]
            discovery[node] = timer
            low[node] = timer
            parent[node] = None
            timer += 1
            children_count: Dict[TNode, int] = {node: 0}

            while stack:
                u, edge_idx = stack[-1]
                neighbors = self._adj.get(u, [])

                if edge_idx < len(neighbors):
                    v = neighbors[edge_idx]
                    stack[-1] = (u, edge_idx + 1)

                    if v == parent[u]:
                        continue

                    if v in discovery:
                        low[u] = min(low[u], discovery[v])
                        if discovery[v] < discovery[u]:
                            edge_stack.append((u, v))
                    else:
                        parent[v] = u
                        children_count[u] = children_count.get(u, 0) + 1
                        discovery[v] = timer
                        low[v] = timer
                        timer += 1
                        edge_stack.append((u, v))
                        stack.append((v, 0))
                else:
                    stack.pop()
                    p = parent[u]
                    if p is not None:
                        low[p] = min(low[p], low[u])
                        if (parent[p] is not None and low[u] >= discovery[p]) or (parent[p] is None and children_count.get(p, 0) > 1):
                            articulation_points.add(p)

                        if low[u] >= discovery[p]:
                            block: Set[TNode] = set()
                            while edge_stack:
                                eu, ev = edge_stack.pop()
                                block.add(eu)
                                block.add(ev)
                                if (eu, ev) == (p, u) or (eu, ev) == (u, p):
                                    break
                            if block:
                                blocks.append(block)

        tree_adj: Dict[str, List[str]] = {}
        for idx, block in enumerate(blocks):
            block_id = f"block_{idx}"
            tree_adj[block_id] = []
            for ap in articulation_points:
                if ap in block:
                    ap_id = f"cut_{ap}"
                    if ap_id not in tree_adj:
                        tree_adj[ap_id] = []
                    tree_adj[block_id].append(ap_id)
                    tree_adj[ap_id].append(block_id)

        return blocks, articulation_points, tree_adj
