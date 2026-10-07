"""ALT (A*, Landmarks, Triangle Inequality) Shortest Path Algorithm.

Fast exact point-to-point shortest paths using landmark precomputation and
triangle-inequality-derived admissible heuristics for goal-directed A* search.
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAltShortestPath(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-32
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O((V + E) log V) worst-case, sub-Dijkstra in practice
      space: O(K * V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[Tuple[TNode, float]]],
        landmarks: Optional[List[TNode]] = None,
        num_landmarks: int = 4,
    ) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: list(edges) for u, edges in adjacency.items()}
        self._rev_adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in self._adj}
        
        for u in list(self._adj.keys()):
            for v, w in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []
                if v not in self._rev_adj:
                    self._rev_adj[v] = []
                self._rev_adj[v].append((u, w))

        self._nodes: List[TNode] = list(self._adj.keys())
        if landmarks is not None:
            self._landmarks: List[TNode] = landmarks
        else:
            self._landmarks = self._select_landmarks_farthest(num_landmarks)

        self._dist_from_landmark: Dict[TNode, Dict[TNode, float]] = {}
        self._dist_to_landmark: Dict[TNode, Dict[TNode, float]] = {}
        self._precompute_landmark_distances()

    def _select_landmarks_farthest(self, k: int) -> List[TNode]:
        if not self._nodes:
            return []
        if k >= len(self._nodes):
            return list(self._nodes)
            
        landmarks: List[TNode] = [sorted(self._nodes, key=lambda x: str(x))[0]]
        min_dist: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
        
        while len(landmarks) < k:
            last_lm = landmarks[-1]
            dist = self._dijkstra_dist(last_lm, self._adj)
            for u in self._nodes:
                min_dist[u] = min(min_dist[u], dist.get(u, float("inf")))
            farthest = max(self._nodes, key=lambda u: (min_dist[u] if min_dist[u] != float("inf") else -1, str(u)))
            landmarks.append(farthest)
            
        return landmarks

    def _dijkstra_dist(self, src: TNode, graph: Dict[TNode, List[Tuple[TNode, float]]]) -> Dict[TNode, float]:
        dist: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
        dist[src] = 0.0
        pq: List[Tuple[float, str, TNode]] = [(0.0, str(src), src)]
        
        while pq:
            d, _, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in graph.get(u, []):
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(pq, (dist[v], str(v), v))
        return dist

    def _precompute_landmark_distances(self) -> None:
        for lm in self._landmarks:
            self._dist_from_landmark[lm] = self._dijkstra_dist(lm, self._adj)
            self._dist_to_landmark[lm] = self._dijkstra_dist(lm, self._rev_adj)

    def heuristic(self, u: TNode, target: TNode) -> float:
        h = 0.0
        for lm in self._landmarks:
            d_lm_u = self._dist_from_landmark[lm].get(u, float("inf"))
            d_lm_t = self._dist_from_landmark[lm].get(target, float("inf"))
            if d_lm_u != float("inf") and d_lm_t != float("inf"):
                h = max(h, d_lm_t - d_lm_u)
                
            d_u_lm = self._dist_to_landmark[lm].get(u, float("inf"))
            d_t_lm = self._dist_to_landmark[lm].get(target, float("inf"))
            if d_u_lm != float("inf") and d_t_lm != float("inf"):
                h = max(h, d_u_lm - d_t_lm)
        return max(0.0, h)

    def find_shortest_path(self, source: TNode, target: TNode) -> Tuple[float, List[TNode]]:
        if source == target:
            return 0.0, [source]
            
        g_score: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
        g_score[source] = 0.0
        parent: Dict[TNode, Optional[TNode]] = {u: None for u in self._nodes}
        
        pq: List[Tuple[float, float, str, TNode]] = [(self.heuristic(source, target), 0.0, str(source), source)]
        visited: Dict[TNode, bool] = {}
        
        while pq:
            f, g, _, u = heapq.heappop(pq)
            if visited.get(u, False):
                continue
            visited[u] = True
            
            if u == target:
                path: List[TNode] = []
                curr: Optional[TNode] = target
                while curr is not None:
                    path.append(curr)
                    curr = parent[curr]
                path.reverse()
                return g_score[target], path
                
            for v, w in self._adj.get(u, []):
                tentative_g = g_score[u] + w
                if tentative_g < g_score.get(v, float("inf")):
                    g_score[v] = tentative_g
                    parent[v] = u
                    f_score = tentative_g + self.heuristic(v, target)
                    heapq.heappush(pq, (f_score, tentative_g, str(v), v))
                    
        return float("inf"), []
