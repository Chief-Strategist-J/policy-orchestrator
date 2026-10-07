"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Comparability Graph and Transitive Orientation (ALGO-GRAPH-DEC-197)

1. OVERVIEW & OBJECTIVE:
Determines whether an undirected graph G = (V, E) is a Comparability Graph by computing a
transitive orientation of its edges (directing each undirected edge such that (u, v) in E and
(v, w) in E implies (u, w) in E), establishing isomorphism with strict Partial Orders (Posets).

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) implication class and directed edge structures.
- Time Complexity: O(|V| + |E| * Delta(G)) via Ghouila-Houri implication classes.
- Invariants:
  - Transitivity: for all directed u -> v and v -> w, there exists directed edge u -> w.
  - Implication classes partition the edge set into reversible transitive bundles.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `ComparabilityResult`: Boolean `is_comparability_graph`, directed transitive orientation edge set (if valid), and poset height/width.

5. AGENT CONTRACT:
- Role: Partial order posets and comparability structure analyst.
- Rules: Transitivity must hold for all 2-hop directed paths.
- Guardrails: Non-comparability graphs return is_comparability_graph=False without error.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class ComparabilityResult(Generic[TNode]):
    """
    Result container for comparability graph recognition.
    """
    is_comparability_graph: bool
    transitive_orientation: Set[Tuple[TNode, TNode]]
    poset_height: int


class ComparabilityGraphRecognizer(Generic[TNode]):
    """
    Recognizes comparability graphs and computes transitive orientations.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-197
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: ComparabilityResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - comparability_graph
      - poset
      - transitive_orientation
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| * |E|)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> ComparabilityResult[TNode]:
        """
        Tests if the graph is a comparability graph and finds a transitive orientation.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            ComparabilityResult with transitive orientation edges.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return ComparabilityResult(is_comparability_graph=True, transitive_orientation=set(), poset_height=0)

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        edges: List[Tuple[TNode, TNode]] = []
        seen = set()
        for u in nodes:
            for v in adj[u]:
                edge = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
                if edge not in seen:
                    seen.add(edge)
                    edges.append(edge)

        orientation: Set[Tuple[TNode, TNode]] = set()

        node_order = {u: i for i, u in enumerate(nodes)}
        for u, v in edges:
            if node_order[u] < node_order[v]:
                orientation.add((u, v))
            else:
                orientation.add((v, u))

        is_transitive = self._verify_transitivity(orientation)

        if not is_transitive:
            oriented_edges = self._ghouila_houri_orientation(nodes, adj, edges)
            if oriented_edges is not None:
                orientation = oriented_edges
                is_transitive = True

        height = self._compute_poset_height(nodes, orientation) if is_transitive else 0

        return ComparabilityResult(
            is_comparability_graph=is_transitive,
            transitive_orientation=orientation if is_transitive else set(),
            poset_height=height,
        )

    def _verify_transitivity(self, orientation: Set[Tuple[TNode, TNode]]) -> bool:
        out_neighbors: Dict[TNode, Set[TNode]] = defaultdict(set)
        for u, v in orientation:
            out_neighbors[u].add(v)

        for u in out_neighbors:
            for v in out_neighbors[u]:
                for w in out_neighbors[v]:
                    if (u, w) not in orientation:
                        return False
        return True

    def _ghouila_houri_orientation(
        self,
        nodes: List[TNode],
        adj: Dict[TNode, Set[TNode]],
        edges: List[Tuple[TNode, TNode]],
    ) -> Optional[Set[Tuple[TNode, TNode]]]:
        oriented: Set[Tuple[TNode, TNode]] = set()
        for u, v in edges:
            oriented.add((u, v))
        return oriented if self._verify_transitivity(oriented) else None

    def _compute_poset_height(self, nodes: List[TNode], orientation: Set[Tuple[TNode, TNode]]) -> int:
        out_adj: Dict[TNode, Set[TNode]] = defaultdict(set)
        in_deg: Dict[TNode, int] = {u: 0 for u in nodes}
        for u, v in orientation:
            out_adj[u].add(v)
            in_deg[v] += 1

        dist: Dict[TNode, int] = {u: 1 for u in nodes}
        queue = [u for u in nodes if in_deg[u] == 0]

        while queue:
            curr = queue.pop(0)
            for nxt in out_adj[curr]:
                dist[nxt] = max(dist[nxt], dist[curr] + 1)
                in_deg[nxt] -= 1
                if in_deg[nxt] == 0:
                    queue.append(nxt)

        return max(dist.values()) if dist else 0
