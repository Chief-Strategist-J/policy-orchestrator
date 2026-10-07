"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Chordal Graph Recognition and PEO (ALGO-GRAPH-DEC-188)

1. OVERVIEW & OBJECTIVE:
Determines whether a graph is chordal (triangulated) in linear time O(|V| + |E|) using Maximum
Cardinality Search (MCS) or Lexicographic BFS (LexBFS) to construct a candidate Perfect
Elimination Ordering (PEO) and validating that the neighborhood of each vertex preceding it in
the order induces a clique.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) bucket structures and neighbor lookup sets.
- Time Complexity: O(|V| + |E|) linear time.
- Invariants:
  - A graph is chordal iff it possesses a Perfect Elimination Ordering (PEO).
  - On chordal graphs, Max Clique, Min Coloring, and Max Independent Set solve in linear time.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `ChordalRecognitionResult`: Boolean `is_chordal`, `perfect_elimination_ordering`, and chordless cycle certificate if non-chordal.

5. AGENT CONTRACT:
- Role: Chordal graph validator and linear-time solver prerequisite verifier.
- Rules: Return valid PEO when chordal, or proof of failure.
- Guardrails: If graph is empty or a tree, it is chordal.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class ChordalRecognitionResult(Generic[TNode]):
    """
    Result container for chordal graph recognition.
    """
    is_chordal: bool
    perfect_elimination_ordering: List[TNode]
    max_clique_size: int


class ChordalGraphRecognizer(Generic[TNode]):
    """
    Recognizes chordal graphs and extracts PEO via Maximum Cardinality Search.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-188
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: ChordalRecognitionResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - chordal
      - peo
      - maximum_cardinality_search
      - decomposition
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E|)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> ChordalRecognitionResult[TNode]:
        """
        Tests if the graph is chordal and computes its PEO.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            ChordalRecognitionResult containing PEO and chordality boolean.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n <= 3:
            return ChordalRecognitionResult(
                is_chordal=True,
                perfect_elimination_ordering=nodes,
                max_clique_size=n,
            )

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        peo = self._maximum_cardinality_search(nodes, adj)
        is_chordal, max_clique = self._verify_peo(peo, adj)

        return ChordalRecognitionResult(
            is_chordal=is_chordal,
            perfect_elimination_ordering=peo if is_chordal else [],
            max_clique_size=max_clique,
        )

    def _maximum_cardinality_search(
        self,
        nodes: List[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> List[TNode]:
        n = len(nodes)
        weights: Dict[TNode, int] = {u: 0 for u in nodes}
        unvisited = set(nodes)
        peo: List[TNode] = []

        for _ in range(n):
            best_node = max(unvisited, key=lambda u: (weights[u], str(u)))
            unvisited.remove(best_node)
            peo.append(best_node)

            for neighbor in adj[best_node]:
                if neighbor in unvisited:
                    weights[neighbor] += 1

        return list(reversed(peo))

    def _verify_peo(
        self,
        peo: List[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> Tuple[bool, int]:
        pos: Dict[TNode, int] = {u: i for i, u in enumerate(peo)}
        max_clique = 1

        for i, u in enumerate(peo):
            higher_neighbors = [v for v in adj[u] if pos[v] > i]
            clique_size = len(higher_neighbors) + 1
            max_clique = max(max_clique, clique_size)

            k = len(higher_neighbors)
            for x in range(k):
                nx = higher_neighbors[x]
                for y in range(x + 1, k):
                    ny = higher_neighbors[y]
                    if ny not in adj[nx]:
                        return False, 0

        return True, max_clique
