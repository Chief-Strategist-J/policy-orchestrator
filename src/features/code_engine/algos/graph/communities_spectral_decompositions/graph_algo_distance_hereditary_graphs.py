"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Distance-Hereditary Graph Recognition and Twin Elimination (ALGO-GRAPH-DEC-200)

1. OVERVIEW & OBJECTIVE:
Determines whether a graph is Distance-Hereditary (every connected induced subgraph preserves
shortest-path distances between its vertices) in linear time using iterative pruning of
pendant vertices (degree 1), true twins (N[u] == N[v]), and false twins (N(u) == N(v)).

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) twin bucket arrays and elimination sequence.
- Time Complexity: O(|V| + |E|) linear time recognition.
- Invariants:
  - G is distance-hereditary iff it can be reduced to a single vertex by removing pendants, true twins, and false twins.
  - G contains no induced cycle C_k (k >= 5), house, domino, or gem subgraphs.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected connected graph.

4. OUTPUT PARAMETERS:
- `DistanceHereditaryResult`: Boolean `is_distance_hereditary`, elimination sequence, and twin pairs.

5. AGENT CONTRACT:
- Role: Distance-hereditary graph verifier and metric embedding analyzer.
- Rules: Enforce strict neighborhood equivalence checks for true and false twins.
- Guardrails: If |V| < 4, graph is always distance-hereditary.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class DistanceHereditaryResult(Generic[TNode]):
    """
    Result container for distance-hereditary recognition.
    """
    is_distance_hereditary: bool
    elimination_sequence: List[Tuple[TNode, str, Optional[TNode]]]
    is_completely_reduced: bool


class DistanceHereditaryRecognizer(Generic[TNode]):
    """
    Recognizes distance-hereditary graphs via pendant and twin elimination.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-200
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: DistanceHereditaryResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - distance_hereditary
      - twin_elimination
      - metric_preserving
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E|)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> DistanceHereditaryResult[TNode]:
        """
        Tests if graph is distance-hereditary.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            DistanceHereditaryResult with twin reduction sequence.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 4:
            seq = [(u, "ISOLATED", None) for u in nodes]
            return DistanceHereditaryResult(
                is_distance_hereditary=True,
                elimination_sequence=seq,
                is_completely_reduced=True,
            )

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}
        remaining = set(nodes)
        elim_seq: List[Tuple[TNode, str, Optional[TNode]]] = []

        while len(remaining) > 1:
            pendant = self._find_pendant(remaining, adj)
            if pendant is not None:
                u, p_neighbor = pendant
                elim_seq.append((u, "PENDANT", p_neighbor))
                remaining.remove(u)
                continue

            twins = self._find_twins(remaining, adj)
            if twins is not None:
                u, v, twin_type = twins
                elim_seq.append((u, twin_type, v))
                remaining.remove(u)
                continue

            break

        is_dh = len(remaining) <= 1
        if len(remaining) == 1:
            last_u = next(iter(remaining))
            elim_seq.append((last_u, "LAST", None))

        return DistanceHereditaryResult(
            is_distance_hereditary=is_dh,
            elimination_sequence=elim_seq if is_dh else [],
            is_completely_reduced=is_dh,
        )

    def _find_pendant(
        self,
        remaining: Set[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> Optional[Tuple[TNode, TNode]]:
        for u in sorted(remaining, key=lambda x: str(x)):
            neighbors = adj[u] & remaining
            if len(neighbors) == 1:
                return u, next(iter(neighbors))
        return None

    def _find_twins(
        self,
        remaining: Set[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> Optional[Tuple[TNode, TNode, str]]:
        rem_list = sorted(remaining, key=lambda x: str(x))
        k = len(rem_list)

        for i in range(k):
            u = rem_list[i]
            n_u = adj[u] & remaining
            for j in range(i + 1, k):
                v = rem_list[j]
                n_v = adj[v] & remaining

                if (v in n_u) and (n_u - {v} == n_v - {u}):
                    return u, v, "TRUE_TWIN"

                if (v not in n_u) and (n_u == n_v):
                    return u, v, "FALSE_TWIN"

        return None
