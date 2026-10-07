"""Contraction Hierarchies (CH) Preprocessing and Query Engine.

Speedup technique for road networks and large spatial/topological graphs.
Orders nodes by importance, contracts them adding shortcuts via witness search,
and executes bidirectional upward queries with exact recursive shortcut unpacking.
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoContractionHierarchies(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-33
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(V log V + E) query, O(V (V + E)) preprocessing
      space: O(V + E + S)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._nodes: List[TNode] = list(adjacency.keys())
        self._adj: Dict[TNode, Dict[TNode, float]] = {u: {} for u in self._nodes}
        self._rev_adj: Dict[TNode, Dict[TNode, float]] = {u: {} for u in self._nodes}
        
        for u, edges in adjacency.items():
            for v, w in edges:
                if v not in self._adj:
                    self._adj[v] = {}
                    self._rev_adj[v] = {}
                    self._nodes.append(v)
                if v not in self._adj[u] or w < self._adj[u][v]:
                    self._adj[u][v] = w
                if u not in self._rev_adj[v] or w < self._rev_adj[v][u]:
                    self._rev_adj[v][u] = w

        self._rank: Dict[TNode, int] = {}
        self._shortcuts: Dict[Tuple[TNode, TNode], Tuple[float, TNode]] = {}
        self._upward_fwd: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in self._nodes}
        self._upward_bwd: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in self._nodes}
        self._preprocess()

    def _witness_search(
        self,
        u: TNode,
        v: TNode,
        ignore_node: TNode,
        max_weight: float,
        active_nodes: Set[TNode],
    ) -> bool:
        dist: Dict[TNode, float] = {u: 0.0}
        pq: List[Tuple[float, str, TNode]] = [(0.0, str(u), u)]
        settled = 0
        max_hops = 50

        while pq and settled < max_hops:
            d, _, curr = heapq.heappop(pq)
            settled += 1
            if d > dist.get(curr, float("inf")):
                continue
            if curr == v and d <= max_weight:
                return True
            if d > max_weight:
                continue

            for nxt, w in self._adj.get(curr, {}).items():
                if nxt == ignore_node or nxt not in active_nodes:
                    continue
                new_d = d + w
                if new_d < dist.get(nxt, float("inf")):
                    dist[nxt] = new_d
                    heapq.heappush(pq, (new_d, str(nxt), nxt))

        return dist.get(v, float("inf")) <= max_weight

    def _preprocess(self) -> None:
        active_nodes: Set[TNode] = set(self._nodes)
        node_order: List[TNode] = []
        
        while active_nodes:
            best_node: Optional[TNode] = None
            min_score = float("inf")
            candidates = sorted(list(active_nodes), key=lambda x: str(x))[:min(len(active_nodes), 20)]
            
            for u in candidates:
                in_deg = len([x for x in self._rev_adj.get(u, {}) if x in active_nodes])
                out_deg = len([x for x in self._adj.get(u, {}) if x in active_nodes])
                score = in_deg * out_deg - (in_deg + out_deg)
                if score < min_score:
                    min_score = score
                    best_node = u

            if best_node is None:
                best_node = sorted(list(active_nodes), key=lambda x: str(x))[0]

            node = best_node
            rank = len(node_order)
            self._rank[node] = rank
            node_order.append(node)

            in_neighbors = [u for u in self._rev_adj.get(node, {}) if u in active_nodes and u != node]
            out_neighbors = [v for v in self._adj.get(node, {}) if v in active_nodes and v != node]

            for u in in_neighbors:
                w_in = self._rev_adj[node][u]
                for v in out_neighbors:
                    if u == v:
                        continue
                    w_out = self._adj[node][v]
                    path_w = w_in + w_out
                    
                    if not self._witness_search(u, v, node, path_w, active_nodes):
                        if v not in self._adj[u] or path_w < self._adj[u][v]:
                            self._adj[u][v] = path_w
                            self._rev_adj[v][u] = path_w
                            self._shortcuts[(u, v)] = (path_w, node)

            active_nodes.remove(node)

        for u in self._nodes:
            u_rank = self._rank[u]
            for v, w in self._adj.get(u, {}).items():
                if self._rank[v] > u_rank:
                    self._upward_fwd[u].append((v, w))
            for v, w in self._rev_adj.get(u, {}).items():
                if self._rank[v] > u_rank:
                    self._upward_bwd[u].append((v, w))

    def query(self, source: TNode, target: TNode) -> Tuple[float, List[TNode]]:
        if source == target:
            return 0.0, [source]

        dist_fwd: Dict[TNode, float] = {source: 0.0}
        dist_bwd: Dict[TNode, float] = {target: 0.0}
        prev_fwd: Dict[TNode, Optional[TNode]] = {source: None}
        prev_bwd: Dict[TNode, Optional[TNode]] = {target: None}

        pq_fwd: List[Tuple[float, str, TNode]] = [(0.0, str(source), source)]
        pq_bwd: List[Tuple[float, str, TNode]] = [(0.0, str(target), target)]

        mu = float("inf")
        meeting_node: Optional[TNode] = None

        while pq_fwd or pq_bwd:
            if pq_fwd:
                df, _, u = heapq.heappop(pq_fwd)
                if df <= dist_fwd[u]:
                    if u in dist_bwd and df + dist_bwd[u] < mu:
                        mu = df + dist_bwd[u]
                        meeting_node = u
                    for v, w in self._upward_fwd.get(u, []):
                        if df + w < dist_fwd.get(v, float("inf")):
                            dist_fwd[v] = df + w
                            prev_fwd[v] = u
                            heapq.heappush(pq_fwd, (dist_fwd[v], str(v), v))

            if pq_bwd:
                db, _, v = heapq.heappop(pq_bwd)
                if db <= dist_bwd[v]:
                    if v in dist_fwd and db + dist_fwd[v] < mu:
                        mu = db + dist_fwd[v]
                        meeting_node = v
                    for u, w in self._upward_bwd.get(v, []):
                        if db + w < dist_bwd.get(u, float("inf")):
                            dist_bwd[u] = db + w
                            prev_bwd[u] = v
                            heapq.heappush(pq_bwd, (dist_bwd[u], str(u), u))

            min_f = pq_fwd[0][0] if pq_fwd else float("inf")
            min_b = pq_bwd[0][0] if pq_bwd else float("inf")
            if min_f >= mu and min_b >= mu:
                break

        if meeting_node is None or mu == float("inf"):
            return float("inf"), []

        fwd_chain: List[TNode] = []
        curr: Optional[TNode] = meeting_node
        while curr is not None:
            fwd_chain.append(curr)
            curr = prev_fwd.get(curr)
        fwd_chain.reverse()

        bwd_chain: List[TNode] = []
        curr = prev_bwd.get(meeting_node)
        while curr is not None:
            bwd_chain.append(curr)
            curr = prev_bwd.get(curr)

        full_chain = fwd_chain + bwd_chain
        expanded_path: List[TNode] = []
        for i in range(len(full_chain) - 1):
            segment = self._unpack_edge(full_chain[i], full_chain[i + 1])
            if not expanded_path:
                expanded_path.extend(segment)
            else:
                expanded_path.extend(segment[1:])

        return mu, expanded_path

    def _unpack_edge(self, u: TNode, v: TNode) -> List[TNode]:
        if (u, v) in self._shortcuts:
            _, mid = self._shortcuts[(u, v)]
            left = self._unpack_edge(u, mid)
            right = self._unpack_edge(mid, v)
            return left[:-1] + right
        return [u, v]
