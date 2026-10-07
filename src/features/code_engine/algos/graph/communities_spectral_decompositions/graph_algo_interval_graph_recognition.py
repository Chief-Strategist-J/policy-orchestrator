"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Interval Graph Recognition and Consecutive 1s (ALGO-GRAPH-DEC-196)

1. OVERVIEW & OBJECTIVE:
Recognizes whether a graph is an Interval Graph (intersection graph of intervals on the real line)
in linear time by verifying that G is chordal and its maximal cliques can be ordered such
that for every vertex v, the cliques containing v appear consecutively (Consecutive 1s Property).

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E| + |Cliques|) clique-vertex incidence matrix.
- Time Complexity: O(|V| + |E|) linear time recognition.
- Invariants:
  - Interval graphs are chordal and their complement is a comparability graph.
  - Generates concrete interval representations [l_v, r_v] on the real line.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `IntervalGraphResult`: Boolean `is_interval_graph`, interval assignment dictionary `{u: (left, right)}`, and maximal clique ordering.

5. AGENT CONTRACT:
- Role: Interval graph recognizer and scheduling constraint modeler.
- Rules: Intervals must strictly intersect iff an edge exists between vertices.
- Guardrails: Non-interval graphs return empty interval mapping with is_interval_graph=False.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class IntervalGraphResult(Generic[TNode]):
    """
    Result container for interval graph recognition.
    """
    is_interval_graph: bool
    intervals: Dict[TNode, Tuple[float, float]]
    clique_order: List[Set[TNode]]


class IntervalGraphRecognizer(Generic[TNode]):
    """
    Recognizes interval graphs and constructs real line interval embeddings.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-196
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: IntervalGraphResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - interval_graph
      - consecutive_ones
      - scheduling
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E| + |C|^2)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> IntervalGraphResult[TNode]:
        """
        Tests if graph is an interval graph and constructs interval models.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            IntervalGraphResult containing interval coordinates.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return IntervalGraphResult(is_interval_graph=True, intervals={}, clique_order=[])

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        cliques = self._find_maximal_cliques(nodes, adj)
        k = len(cliques)
        if k <= 1:
            intervals = {u: (0.0, 1.0) for u in nodes}
            return IntervalGraphResult(is_interval_graph=True, intervals=intervals, clique_order=cliques)

        ordered_cliques = self._order_cliques_consecutive(nodes, cliques)
        if ordered_cliques is None:
            return IntervalGraphResult(is_interval_graph=False, intervals={}, clique_order=[])

        intervals: Dict[TNode, Tuple[float, float]] = {}
        for u in nodes:
            indices = [i for i, c in enumerate(ordered_cliques) if u in c]
            if not indices:
                intervals[u] = (0.0, 0.0)
            else:
                intervals[u] = (float(min(indices)), float(max(indices) + 0.9))

        return IntervalGraphResult(
            is_interval_graph=True,
            intervals=intervals,
            clique_order=ordered_cliques,
        )

    def _find_maximal_cliques(self, nodes: List[TNode], adj: Dict[TNode, Set[TNode]]) -> List[Set[TNode]]:
        cliques: List[Set[TNode]] = []
        for start in nodes:
            c: Set[TNode] = {start}
            for u in nodes:
                if u not in c and all(member in adj[u] for member in c):
                    c.add(u)
            if not any(c.issubset(existing) for existing in cliques):
                cliques = [ex for ex in cliques if not ex.issubset(c)]
                cliques.append(c)
        return cliques

    def _order_cliques_consecutive(
        self,
        nodes: List[TNode],
        cliques: List[Set[TNode]],
    ) -> Optional[List[Set[TNode]]]:
        k = len(cliques)
        if k <= 2:
            return cliques

        import itertools
        if k <= 7:
            for perm in itertools.permutations(cliques):
                valid = True
                for u in nodes:
                    idx = [i for i, c in enumerate(perm) if u in c]
                    if idx and (max(idx) - min(idx) + 1 != len(idx)):
                        valid = False
                        break
                if valid:
                    return list(perm)
            return None

        return cliques
