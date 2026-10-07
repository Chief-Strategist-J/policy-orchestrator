"""DAG Shortest and Longest Path Dynamic Programming Algorithm.

Linear-time path optimization on directed acyclic graphs using topological ordering.
Computes single-source shortest paths (with arbitrary real/negative weights) and critical longest paths.
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDagShortestLongestPath(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-28
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(V + E)
      space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: list(edges) for u, edges in adjacency.items()}
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def get_topological_order(self) -> List[TNode]:
        in_degree: Dict[TNode, int] = {u: 0 for u in self._adj}
        for u in self._adj:
            for v, _ in self._adj[u]:
                in_degree[v] = in_degree.get(v, 0) + 1
                
        queue: deque[TNode] = deque(sorted([u for u, deg in in_degree.items() if deg == 0], key=lambda x: str(x)))
        order: List[TNode] = []
        
        while queue:
            u = queue.popleft()
            order.append(u)
            for v, _ in sorted(self._adj.get(u, []), key=lambda item: str(item[0])):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(order) != len(self._adj):
            raise ValueError("Graph contains a cycle; topological sort not possible")
            
        return order

    def compute_shortest_paths(self, source: TNode) -> Tuple[Dict[TNode, float], Dict[TNode, Optional[TNode]]]:
        order = self.get_topological_order()
        dist: Dict[TNode, float] = {u: float("inf") for u in self._adj}
        prev: Dict[TNode, Optional[TNode]] = {u: None for u in self._adj}
        dist[source] = 0.0

        for u in order:
            if dist[u] == float("inf"):
                continue
            for v, weight in self._adj.get(u, []):
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u

        return dist, prev

    def compute_longest_paths(self, source: TNode) -> Tuple[Dict[TNode, float], Dict[TNode, Optional[TNode]]]:
        order = self.get_topological_order()
        dist: Dict[TNode, float] = {u: float("-inf") for u in self._adj}
        prev: Dict[TNode, Optional[TNode]] = {u: None for u in self._adj}
        dist[source] = 0.0

        for u in order:
            if dist[u] == float("-inf"):
                continue
            for v, weight in self._adj.get(u, []):
                if dist[u] + weight > dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u

        return dist, prev

    def reconstruct_path(self, target: TNode, prev: Dict[TNode, Optional[TNode]]) -> List[TNode]:
        path: List[TNode] = []
        curr: Optional[TNode] = target
        while curr is not None:
            path.append(curr)
            curr = prev.get(curr)
        path.reverse()
        return path
