"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LOCAL S-T MIN-CUT CLUSTERING (ALGO-GRAPH-COMM-162)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Local Max-Flow / Min-Cut community expansion around target seed vertices (Local Flow Improvement).
   Connects source s to seeds with infinite capacity, connects background candidate
   nodes to sink t with parameter capacity gamma * deg(v), and solves maximum flow
   via Dinic's blocking flow to identify the minimal conductance local community cut.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V_local^2 * E_local) Dinic flow on localized subgraph.
   - Space Complexity: O(V_local + E_local) residual flow network.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - seed_nodes: List[TNode] - Initial seed cluster vertices.
   - gamma_penalty: float - Penalty parameter gamma for background cut volume (default: 0.5).

4. OUTPUT PARAMETERS:
   - local_community: List[TNode] - Nodes on the source side of the minimum cut.
   - cut_capacity: float - Capacity of the bounding s-t cut.
   - expansion_size: int - Total vertices in the extracted community.

5. AGENT CONTRACT:
   - Role: Analyst and Retriever.
   - Preconditions: Seeds must be in the graph.
   - Guardrails: Source capacity infinity ensures seeds strictly remain in the output community.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLocalMaxFlowClustering(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-162
      name: GraphAlgoLocalMaxFlowClustering
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, local_clustering, min_cut, dinic_flow, local_expansion]
      inputs:
        type: object
        required: [adjacency, seed_nodes]
        properties:
          adjacency: {type: object}
          seed_nodes: {type: array, items: {type: string}}
          gamma_penalty: {type: number, default: 0.5}
      outputs:
        type: object
        required: [local_community, cut_capacity, expansion_size]
        properties:
          local_community: {type: array, items: {type: string}}
          cut_capacity: {type: number}
          expansion_size: {type: integer}
      parameters:
        gamma_penalty: {type: number, default: 0.5}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V_local^2 * E_local)
        space: O(V_local + E_local)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        seed_nodes: List[TNode],
        gamma_penalty: float = 0.5,
    ) -> None:
        """
        Initialize the Local Max-Flow Clustering engine.

        Args:
            adjacency: Graph adjacency dictionary.
            seed_nodes: Target seed cluster.
            gamma_penalty: Volume penalty parameter gamma.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._seeds: Set[TNode] = set(seed_nodes)
        self._gamma: float = gamma_penalty
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def extract_community(self) -> Tuple[List[TNode], float, int]:
        """
        Solve localized s-t min-cut to extract the seed-rooted community.

        Returns:
            Tuple of (local_community_nodes, min_cut_capacity, community_size).
        """
        if not self._seeds:
            return [], 0.0, 0

        source = "__SOURCE__"
        sink = "__SINK__"

        cap: Dict[Tuple[str, str], float] = {}
        flow: Dict[Tuple[str, str], float] = {}
        flow_adj: Dict[str, Set[str]] = {source: set(), sink: set()}

        for u in self._nodes:
            u_str = str(u)
            flow_adj[u_str] = set()

        for u in self._nodes:
            u_str = str(u)
            if u in self._seeds:
                cap[(source, u_str)] = float("inf")
                cap[(u_str, source)] = 0.0
                flow_adj[source].add(u_str)
                flow_adj[u_str].add(source)
            else:
                deg_u = len(self._adj.get(u, set()))
                c_val = self._gamma * float(max(1, deg_u))
                cap[(u_str, sink)] = c_val
                cap[(sink, u_str)] = 0.0
                flow_adj[u_str].add(sink)
                flow_adj[sink].add(u_str)

            for v in self._adj.get(u, set()):
                v_str = str(v)
                if (u_str, v_str) not in cap:
                    cap[(u_str, v_str)] = 1.0
                    cap[(v_str, u_str)] = 1.0
                    flow_adj[u_str].add(v_str)
                    flow_adj[v_str].add(u_str)

        for e in cap:
            flow[e] = 0.0

        def _bfs_level() -> Optional[Dict[str, int]]:
            level: Dict[str, int] = {source: 0}
            q: Deque[str] = deque([source])
            while q:
                curr = q.popleft()
                for nxt in flow_adj[curr]:
                    residual = cap.get((curr, nxt), 0.0) - flow.get((curr, nxt), 0.0)
                    if residual > 1e-6 and nxt not in level:
                        level[nxt] = level[curr] + 1
                        q.append(nxt)
            return level if sink in level else None

        def _dfs_push(curr: str, pushed: float, level: Dict[str, int], ptr: Dict[str, int]) -> float:
            if curr == sink or pushed <= 0:
                return pushed
            nbrs = list(flow_adj[curr])
            while ptr[curr] < len(nbrs):
                nxt = nbrs[ptr[curr]]
                residual = cap.get((curr, nxt), 0.0) - flow.get((curr, nxt), 0.0)
                if level.get(nxt, -1) == level[curr] + 1 and residual > 1e-6:
                    tr = _dfs_push(nxt, min(pushed, residual), level, ptr)
                    if tr > 1e-6:
                        flow[(curr, nxt)] += tr
                        flow[(nxt, curr)] -= tr
                        return tr
                ptr[curr] += 1
            return 0.0

        total_flow = 0.0
        while True:
            level = _bfs_level()
            if level is None:
                break
            ptr = {node: 0 for node in flow_adj}
            while True:
                pushed = _dfs_push(source, float("inf"), level, ptr)
                if pushed <= 1e-6:
                    break
                total_flow += pushed

        visited_source_side: Set[str] = set()
        q_src: Deque[str] = deque([source])
        visited_source_side.add(source)

        while q_src:
            curr = q_src.popleft()
            for nxt in flow_adj[curr]:
                res = cap.get((curr, nxt), 0.0) - flow.get((curr, nxt), 0.0)
                if res > 1e-6 and nxt not in visited_source_side:
                    visited_source_side.add(nxt)
                    q_src.append(nxt)

        comm_nodes = [u for u in self._nodes if str(u) in visited_source_side]
        return sorted(comm_nodes, key=lambda x: str(x)), total_flow, len(comm_nodes)
