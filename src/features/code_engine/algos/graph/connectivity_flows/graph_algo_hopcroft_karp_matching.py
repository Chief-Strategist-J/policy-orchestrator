"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HOPCROFT-KARP MAXIMUM MATCHING (ALGO-GRAPH-MATCH-84)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hopcroft-Karp algorithm for maximum cardinality bipartite matching.
   Combines multi-source BFS to find shortest alternating augmenting path lengths
   with DFS to augment multiple vertex-disjoint paths in each phase.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E * sqrt(V)) bounded augmenting phases.
   - Space Complexity: O(V + E) matching and layer arrays.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Exact maximum cardinality bipartite matching.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TLeft = TypeVar("TLeft", bound=Hashable)
TRight = TypeVar("TRight", bound=Hashable)


class GraphAlgoHopcroftKarpMatching(Generic[TLeft, TRight]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MATCH-84
      name: GraphAlgoHopcroftKarpMatching
      version: 1.0.0
      category: graph_matching
      capability_tags: [graph, bipartite_matching, hopcroft_karp, maximum_cardinality_matching]
      inputs:
        type: object
        required: [left_nodes, right_nodes, adjacency]
        properties:
          left_nodes:
            type: array
            items: {type: string}
          right_nodes:
            type: array
            items: {type: string}
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
        time: O(E * sqrt(V))
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        left_nodes: List[TLeft],
        right_nodes: List[TRight],
        adjacency: Dict[TLeft, List[TRight]],
    ) -> None:
        self._left: List[TLeft] = sorted(list(set(left_nodes)), key=lambda x: str(x))
        self._right: List[TRight] = sorted(list(set(right_nodes)), key=lambda x: str(x))
        self._adj: Dict[TLeft, List[TRight]] = {u: list(neighbors) for u, neighbors in adjacency.items()}

    def compute_maximum_matching(self) -> Tuple[int, Dict[TLeft, TRight]]:
        pair_u: Dict[TLeft, Optional[TRight]] = {u: None for u in self._left}
        pair_v: Dict[TRight, Optional[TLeft]] = {v: None for v in self._right}
        dist: Dict[Optional[TLeft], float] = {}

        def bfs() -> bool:
            queue: deque[TLeft] = deque()
            for u in self._left:
                if pair_u[u] is None:
                    dist[u] = 0.0
                    queue.append(u)
                else:
                    dist[u] = float("inf")

            dist[None] = float("inf")

            while queue:
                u = queue.popleft()
                if dist[u] < dist[None]:
                    for v in self._adj.get(u, []):
                        matched_left = pair_v[v]
                        if dist.get(matched_left, float("inf")) == float("inf"):
                            dist[matched_left] = dist[u] + 1.0
                            if matched_left is not None:
                                queue.append(matched_left)

            return dist[None] != float("inf")

        def dfs(u: Optional[TLeft]) -> bool:
            if u is not None:
                for v in self._adj.get(u, []):
                    matched_left = pair_v[v]
                    if dist.get(matched_left, float("inf")) == dist[u] + 1.0:
                        if dfs(matched_left):
                            pair_v[v] = u
                            pair_u[u] = v
                            return True
                dist[u] = float("inf")
                return False
            return True

        matching_size = 0
        while bfs():
            for u in self._left:
                if pair_u[u] is None and dfs(u):
                    matching_size += 1

        return matching_size, {u: v for u, v in pair_u.items() if v is not None}
