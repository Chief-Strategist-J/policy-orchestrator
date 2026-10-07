"""Bipartiteness Testing and 2-Coloring Algorithm.

Validates whether an undirected or directed graph is bipartite via BFS 2-coloring,
returning either the partition certificate (coloring map) or the odd-length cycle certificate proving non-bipartiteness.
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBipartiteTest(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-TRV-22
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(V + E)
      space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in list(self._adj.keys()):
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def is_bipartite(self) -> bool:
        is_bip, _, _ = self.analyze()
        return is_bip

    def analyze(self) -> Tuple[bool, Optional[Dict[TNode, int]], Optional[List[TNode]]]:
        color: Dict[TNode, int] = {}
        parent: Dict[TNode, Optional[TNode]] = {}
        
        for root in sorted(self._adj.keys(), key=lambda x: str(x)):
            if root in color:
                continue
                
            color[root] = 0
            parent[root] = None
            queue: deque[TNode] = deque([root])
            
            while queue:
                u = queue.popleft()
                current_color = color[u]
                next_color = 1 - current_color
                
                for v in self._adj.get(u, []):
                    if v not in color:
                        color[v] = next_color
                        parent[v] = u
                        queue.append(v)
                    elif color[v] == current_color:
                        odd_cycle = self._extract_odd_cycle(u, v, parent)
                        return False, None, odd_cycle

        return True, color, None

    def _extract_odd_cycle(
        self,
        u: TNode,
        v: TNode,
        parent: Dict[TNode, Optional[TNode]],
    ) -> List[TNode]:
        path_u: List[TNode] = []
        curr: Optional[TNode] = u
        while curr is not None:
            path_u.append(curr)
            curr = parent[curr]
            
        path_v: List[TNode] = []
        curr = v
        while curr is not None:
            path_v.append(curr)
            curr = parent[curr]
            
        set_v: Set[TNode] = set(path_v)
        lca: Optional[TNode] = None
        for node in path_u:
            if node in set_v:
                lca = node
                break
                
        cycle: List[TNode] = []
        curr = u
        while curr != lca and curr is not None:
            cycle.append(curr)
            curr = parent[curr]
        if lca is not None:
            cycle.append(lca)
            
        v_subpath: List[TNode] = []
        curr = v
        while curr != lca and curr is not None:
            v_subpath.append(curr)
            curr = parent[curr]
            
        cycle.extend(reversed(v_subpath))
        cycle.append(u)
        return cycle
