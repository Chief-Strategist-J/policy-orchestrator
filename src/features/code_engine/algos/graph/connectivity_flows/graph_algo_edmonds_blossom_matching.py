"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EDMONDS BLOSSOM MATCHING (ALGO-GRAPH-MATCH-87)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Edmonds' Blossom algorithm for maximum cardinality matching in general (non-bipartite) graphs.
   Explores alternating BFS trees, contracting odd-length cycles (blossoms) into super-nodes,
   and expanding blossoms during augmenting path reconstruction.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^2 * E) augmenting path phases.
   - Space Complexity: O(V + E) matching, base, and parent pointers.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Maximum cardinality matching in arbitrary undirected graphs.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEdmondsBlossomMatching(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MATCH-87
      name: GraphAlgoEdmondsBlossomMatching
      version: 1.0.0
      category: graph_matching
      capability_tags: [graph, general_matching, edmonds_blossom, non_bipartite_matching, blossom_contraction]
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
        required: [matching_size, matching_pairs]
        properties:
          matching_size: {type: integer}
          matching_pairs:
            type: object
            additionalProperties: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^2 * E)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))

    def compute_maximum_matching(self) -> Tuple[int, Dict[TNode, TNode]]:
        match: Dict[TNode, Optional[TNode]] = {u: None for u in self._nodes}

        for root in self._nodes:
            if match[root] is not None:
                continue

            parent: Dict[TNode, Optional[TNode]] = {u: None for u in self._nodes}
            base: Dict[TNode, TNode] = {u: u for u in self._nodes}
            in_blossom: Dict[TNode, bool] = {u: False for u in self._nodes}
            in_queue: Dict[TNode, bool] = {u: False for u in self._nodes}
            tree_type: Dict[TNode, int] = {u: 0 for u in self._nodes}

            queue: deque[TNode] = deque([root])
            tree_type[root] = 1
            in_queue[root] = True

            def lca(u: TNode, v: TNode) -> TNode:
                path: List[TNode] = []
                visited_lca: Set[TNode] = set()

                curr: Optional[TNode] = u
                while curr is not None:
                    curr = base[curr]
                    path.append(curr)
                    if match[curr] is None:
                        break
                    p = parent[match[curr]]
                    curr = p

                visited_lca = set(path)
                curr = v
                while curr is not None:
                    curr = base[curr]
                    if curr in visited_lca:
                        return curr
                    if match[curr] is None:
                        break
                    p = parent[match[curr]]
                    curr = p

                return root

            def mark_blossom(b: TNode, u: TNode, v: TNode) -> None:
                while base[u] != b:
                    p = parent[u]
                    mv = match[u]
                    if mv is not None:
                        in_blossom[base[u]] = in_blossom[base[mv]] = True
                        parent[u] = v
                        v = mv
                        u = parent[mv]
                    else:
                        break

            aug_found = False

            while queue and not aug_found:
                u = queue.popleft()

                for v in self._adj.get(u, []):
                    if base[u] == base[v] or match[u] == v:
                        continue

                    if v == root or (match[v] is not None and parent[match[v]] is not None):
                        cur_lca = lca(u, v)
                        for n in self._nodes:
                            in_blossom[n] = False

                        mark_blossom(cur_lca, u, v)
                        mark_blossom(cur_lca, v, u)

                        for n in self._nodes:
                            if in_blossom[base[n]]:
                                base[n] = cur_lca
                                if not in_queue[n]:
                                    in_queue[n] = True
                                    queue.append(n)
                    elif parent[v] is None:
                        parent[v] = u
                        if match[v] is None:
                            curr_v = v
                            while curr_v is not None:
                                pv = parent[curr_v]
                                if pv is not None:
                                    ppv = match[pv]
                                    match[curr_v] = pv
                                    match[pv] = curr_v
                                    curr_v = ppv
                                else:
                                    break
                            aug_found = True
                            break
                        else:
                            mv = match[v]
                            if mv is not None:
                                in_queue[mv] = True
                                queue.append(mv)

        matching_pairs = {u: v for u, v in match.items() if v is not None}
        return len(matching_pairs) // 2, matching_pairs
