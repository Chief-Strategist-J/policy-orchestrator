"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KONIG MINIMUM VERTEX COVER (ALGO-GRAPH-MATCH-90)
================================================================================

1. OVERVIEW & OBJECTIVE:
   König's theorem for minimum vertex cover construction in bipartite graphs.
   Constructs the minimum cardinality vertex cover from a maximum matching using
   alternating reachable BFS components.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E * sqrt(V)) matching + O(V + E) alternating BFS.
   - Space Complexity: O(V + E) alternating reachability sets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer & Verifier.
   - Guarantees: Exact equality |MinVertexCover| = |MaxMatching| holds as optimality certificate.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from src.features.code_engine.algos.graph.connectivity_flows.graph_algo_hopcroft_karp_matching import (
    GraphAlgoHopcroftKarpMatching,
)

TLeft = TypeVar("TLeft", bound=Hashable)
TRight = TypeVar("TRight", bound=Hashable)


class GraphAlgoKonigVertexCover(Generic[TLeft, TRight]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MATCH-90
      name: GraphAlgoKonigVertexCover
      version: 1.0.0
      category: graph_matching
      capability_tags: [graph, bipartite_graph, vertex_cover, konig_theorem, duality_certificate]
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
        required: [cover_size, left_cover, right_cover, matching_size]
        properties:
          cover_size: {type: integer}
          left_cover:
            type: array
            items: {type: string}
          right_cover:
            type: array
            items: {type: string}
          matching_size: {type: integer}
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

    def compute_minimum_vertex_cover(self) -> Tuple[Set[TLeft], Set[TRight], int]:
        hk = GraphAlgoHopcroftKarpMatching[TLeft, TRight](self._left, self._right, self._adj)
        matching_size, match_pairs = hk.compute_maximum_matching()

        rev_match: Dict[TRight, TLeft] = {v: u for u, v in match_pairs.items()}
        unmatched_left = [u for u in self._left if u not in match_pairs]

        z_left: Set[TLeft] = set(unmatched_left)
        z_right: Set[TRight] = set()
        queue: deque[TLeft] = deque(unmatched_left)

        while queue:
            u = queue.popleft()
            for v in self._adj.get(u, []):
                if v not in z_right and match_pairs.get(u) != v:
                    z_right.add(v)
                    matched_l = rev_match.get(v)
                    if matched_l is not None and matched_l not in z_left:
                        z_left.add(matched_l)
                        queue.append(matched_l)

        left_cover = set(self._left) - z_left
        right_cover = set(z_right)

        return left_cover, right_cover, matching_size
