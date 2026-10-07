"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Vertex Coloring - Welsh-Powell and DSATUR (ALGO-GRAPH-COL-178)

1. OVERVIEW & OBJECTIVE:
Assigns discrete color indices {0, 1, ..., k-1} to vertices such that no two adjacent vertices
share the same color (proper vertex coloring), minimizing the total chromatic count k using
Welsh-Powell (largest degree first) and DSATUR (degree of saturation) heuristics.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for color assignments and neighbor color sets.
- Time Complexity: O(|V| * log |V| + |E|) for Welsh-Powell; O(|V|^2 + |E|) for DSATUR.
- Invariants:
  - For all (u, v) in E, color(u) != color(v).
  - Upper bounded by Delta(G) + 1 colors (Brooks' Theorem).

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.
- `strategy` (str): 'dsatur' or 'welsh_powell' (default: 'dsatur').

4. OUTPUT PARAMETERS:
- `VertexColoringResult`: Dictionary of node-to-color assignments, chromatic number estimate, and valid flag.

5. AGENT CONTRACT:
- Role: Resource allocation, register allocation, and timetable conflict scheduler.
- Rules: Enforce strict validity verification (no adjacent nodes with identical color).
- Guardrails: If graph is an empty graph (no edges), chromatic number is 1 (or 0 for empty V).
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class VertexColoringResult(Generic[TNode]):
    """
    Result container for graph vertex coloring.
    """
    colors: Dict[TNode, int]
    chromatic_number: int
    is_valid: bool


class VertexColoring(Generic[TNode]):
    """
    Computes proper vertex colorings using DSATUR and Welsh-Powell heuristics.

    ```yaml
    contract_id: ALGO-GRAPH-COL-178
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      strategy: str
    outputs:
      result: VertexColoringResult[TNode]
    parameters:
      strategy: str (dsatur | welsh_powell)
    capability_tags:
      - graph
      - coloring
      - dsatur
      - welsh_powell
      - chromatic_number
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V|^2 + |E|)
      space: O(|V| + |E|)
    ```
    """

    def color(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        strategy: str = "dsatur",
    ) -> VertexColoringResult[TNode]:
        """
        Colors graph vertices according to the specified heuristic.

        Args:
            adjacency: Graph adjacency map.
            strategy: 'dsatur' or 'welsh_powell'.

        Returns:
            VertexColoringResult containing color mapping and chromatic bound.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return VertexColoringResult(colors={}, chromatic_number=0, is_valid=True)

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        if strategy.lower() == "welsh_powell":
            colors = self._welsh_powell(nodes, adj)
        else:
            colors = self._dsatur(nodes, adj)

        is_valid = self._verify_proper_coloring(adj, colors)
        num_colors = max(colors.values()) + 1 if colors else 0

        return VertexColoringResult(
            colors=colors,
            chromatic_number=num_colors,
            is_valid=is_valid,
        )

    def _welsh_powell(self, nodes: List[TNode], adj: Dict[TNode, Set[TNode]]) -> Dict[TNode, int]:
        sorted_nodes = sorted(nodes, key=lambda u: (-len(adj[u]), str(u)))
        colors: Dict[TNode, int] = {}
        curr_color = 0

        uncolored = list(sorted_nodes)
        while uncolored:
            colored_in_round: List[TNode] = []
            for u in uncolored:
                can_color = True
                for v in colored_in_round:
                    if v in adj[u]:
                        can_color = False
                        break
                if can_color:
                    colors[u] = curr_color
                    colored_in_round.append(u)

            uncolored = [u for u in uncolored if u not in colors]
            curr_color += 1

        return colors

    def _dsatur(self, nodes: List[TNode], adj: Dict[TNode, Set[TNode]]) -> Dict[TNode, int]:
        colors: Dict[TNode, int] = {}
        neighbor_colors: Dict[TNode, Set[int]] = {u: set() for u in nodes}
        uncolored: Set[TNode] = set(nodes)

        first_node = max(nodes, key=lambda u: (len(adj[u]), str(u)))
        colors[first_node] = 0
        uncolored.remove(first_node)
        for v in adj[first_node]:
            neighbor_colors[v].add(0)

        while uncolored:
            best_node = max(
                uncolored,
                key=lambda u: (len(neighbor_colors[u]), len(adj[u]), str(u)),
            )

            used = neighbor_colors[best_node]
            c = 0
            while c in used:
                c += 1

            colors[best_node] = c
            uncolored.remove(best_node)

            for v in adj[best_node]:
                if v in uncolored:
                    neighbor_colors[v].add(c)

        return colors

    def _verify_proper_coloring(self, adj: Dict[TNode, Set[TNode]], colors: Dict[TNode, int]) -> bool:
        for u, neighbors in adj.items():
            if u not in colors:
                return False
            cu = colors[u]
            for v in neighbors:
                if v in colors and colors[v] == cu:
                    return False
        return True
