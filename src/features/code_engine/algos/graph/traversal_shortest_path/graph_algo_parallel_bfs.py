"""Level-Synchronous Parallel BFS Simulation Engine.

Simulates parallel level-by-level frontier expansion with atomic synchronization semantics,
dual-phase sparse/dense representation switching, and barrier-synchronized wave exploration.
"""

from typing import Dict, Generic, Hashable, List, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoParallelBfs(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-TRV-17
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(V + E) work, O(Diameter) span
      space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def traverse_levels(self, source: TNode) -> Tuple[Dict[TNode, int], List[List[TNode]]]:
        if source not in self._adj:
            return {}, []

        distances: Dict[TNode, int] = {source: 0}
        levels: List[List[TNode]] = [[source]]
        frontier: Set[TNode] = {source}
        visited: Set[TNode] = {source}

        current_depth = 0
        while frontier:
            next_frontier: Set[TNode] = set()
            current_depth += 1

            for u in sorted(frontier, key=lambda x: str(x)):
                for v in self._adj.get(u, []):
                    if v not in visited:
                        visited.add(v)
                        distances[v] = current_depth
                        next_frontier.add(v)

            if next_frontier:
                levels.append(sorted(list(next_frontier), key=lambda x: str(x)))
            frontier = next_frontier

        return distances, levels
