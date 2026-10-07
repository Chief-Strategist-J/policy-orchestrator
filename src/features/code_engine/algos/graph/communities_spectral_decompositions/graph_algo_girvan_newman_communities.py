"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GIRVAN-NEWMAN DIVISIVE COMMUNITIES (ALGO-GRAPH-COMM-153)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Girvan-Newman hierarchical divisive community detection algorithm.
   Iteratively computes edge betweenness centrality and removes the bottleneck edge
   with maximum score until the graph splits into disconnected subgraphs.
   Tracks modularity Q at each split to identify the optimal community dendrogram cut.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m^2 * n) full edge betweenness recomputations.
   - Space Complexity: O(V + E) dendrogram hierarchy.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - target_components: Optional[int] - Desired number of communities before stopping.

4. OUTPUT PARAMETERS:
   - best_partition: Dict[TNode, int] - Optimal community assignment maximizing modularity Q.
   - max_modularity: float - Peak modularity achieved across hierarchical splits.
   - dendrogram_levels: List[List[List[TNode]]] - Sequence of community partitions at each split.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Small or medium connected graph (n <= 1000).
   - Guardrails: Tied highest betweenness edges are removed simultaneously to preserve symmetry.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGirvanNewmanCommunities(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-153
      name: GraphAlgoGirvanNewmanCommunities
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, girvan_newman, edge_betweenness, hierarchical_clustering, dendrogram]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          target_components: {type: integer}
      outputs:
        type: object
        required: [best_partition, max_modularity, dendrogram_levels]
        properties:
          best_partition: {type: object}
          max_modularity: {type: number}
          dendrogram_levels: {type: array, items: {type: array, items: {type: array, items: {type: string}}}}
      parameters:
        target_components: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m^2 * n)
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        target_components: Optional[int] = None,
    ) -> None:
        """
        Initialize the Girvan-Newman community finder.

        Args:
            adjacency: Graph adjacency dictionary.
            target_components: Optional target count of communities.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._target_k: Optional[int] = target_components
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _compute_edge_betweenness(self, curr_adj: Dict[TNode, Set[TNode]]) -> Dict[Tuple[TNode, TNode], float]:
        eb: Dict[Tuple[TNode, TNode], float] = {}
        for s in self._nodes:
            stack: List[TNode] = []
            pred: Dict[TNode, List[TNode]] = {w: [] for w in self._nodes}
            sigma: Dict[TNode, float] = {w: 0.0 for w in self._nodes}
            sigma[s] = 1.0
            dist: Dict[TNode, int] = {w: -1 for w in self._nodes}
            dist[s] = 0

            q: Deque[TNode] = deque([s])
            while q:
                v = q.popleft()
                stack.append(v)
                d = dist[v]
                for w in curr_adj.get(v, set()):
                    if dist[w] < 0:
                        dist[w] = d + 1
                        q.append(w)
                    if dist[w] == d + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta: Dict[TNode, float] = {w: 0.0 for w in self._nodes}
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    if sigma[w] > 0:
                        c = (sigma[v] / sigma[w]) * (1.0 + delta[w])
                        delta[v] += c
                        e = (v, w) if str(v) < str(w) else (w, v)
                        eb[e] = eb.get(e, 0.0) + c

        for e in eb:
            eb[e] *= 0.5
        return eb

    def _get_components(self, curr_adj: Dict[TNode, Set[TNode]]) -> List[List[TNode]]:
        visited: Set[TNode] = set()
        components: List[List[TNode]] = []
        for u in self._nodes:
            if u not in visited:
                comp: List[TNode] = []
                q: Deque[TNode] = deque([u])
                visited.add(u)
                while q:
                    curr = q.popleft()
                    comp.append(curr)
                    for nxt in curr_adj.get(curr, set()):
                        if nxt not in visited:
                            visited.add(nxt)
                            q.append(nxt)
                components.append(sorted(comp, key=lambda x: str(x)))
        return components

    def _compute_modularity(self, components: List[List[TNode]]) -> float:
        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        total_e = sum(degrees.values()) // 2
        if total_e == 0:
            return 0.0
        two_m = float(2 * total_e)
        part = {}
        for c_id, comp in enumerate(components):
            for u in comp:
                part[u] = c_id

        q: float = 0.0
        for comp in components:
            e_c = 0
            k_c = sum(degrees[u] for u in comp)
            for i in range(len(comp)):
                for j in range(i + 1, len(comp)):
                    if comp[j] in self._adj.get(comp[i], set()):
                        e_c += 1
            q += (float(e_c) / float(total_e)) - ((float(k_c) / two_m) ** 2)
        return q

    def find_communities(self) -> Tuple[Dict[TNode, int], float, List[List[List[TNode]]]]:
        """
        Execute Girvan-Newman edge-betweenness peeling.

        Returns:
            Tuple of (best_partition_map, max_modularity_q, dendrogram_hierarchy).
        """
        curr_adj: Dict[TNode, Set[TNode]] = {u: set(self._adj.get(u, set())) for u in self._nodes}
        total_edges = sum(len(curr_adj[u]) for u in self._nodes) // 2

        dendrogram: List[List[List[TNode]]] = []
        best_part: Dict[TNode, int] = {}
        max_q: float = -1.0

        for _ in range(total_edges):
            eb = self._compute_edge_betweenness(curr_adj)
            if not eb:
                break
            max_val = max(eb.values())
            for (u, v), val in list(eb.items()):
                if val == max_val:
                    curr_adj[u].remove(v)
                    curr_adj[v].remove(u)

            comps = self._get_components(curr_adj)
            dendrogram.append(comps)
            q = self._compute_modularity(comps)

            if q > max_q:
                max_q = q
                best_part = {}
                for c_id, comp in enumerate(comps):
                    for u in comp:
                        best_part[u] = c_id

            if self._target_k is not None and len(comps) >= self._target_k:
                break

        if not best_part:
            comps = self._get_components(self._adj)
            for c_id, comp in enumerate(comps):
                for u in comp:
                    best_part[u] = c_id
            max_q = self._compute_modularity(comps)

        return best_part, max_q, dendrogram
