"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BRANDES BETWEENNESS CENTRALITY (ALGO-GRAPH-CENT-109)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Brandes exact vertex and edge betweenness centrality algorithm.
   Accumulates pair-dependencies sigma(s, v)/sigma(s, w) in backward topological order
   from all source shortest-path trees (BFS for unweighted, Dijkstra for weighted graphs).
   Supports directed/undirected and normalized edge and vertex betweenness metrics.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E) unweighted, O(V * E + V^2 log V) weighted graphs.
   - Space Complexity: O(V + E) predecessor stacks and distance structures.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[Tuple[TNode, float]]] - Graph adjacency with non-negative weights.
   - is_directed: bool - Directed flag (default: False).
   - normalized: bool - Whether to normalize scores by 1/((V-1)(V-2)) (default: True).

4. OUTPUT PARAMETERS:
   - vertex_betweenness: Dict[TNode, float] - Betweenness centrality score per vertex.
   - edge_betweenness: Dict[Tuple[TNode, TNode], float] - Betweenness centrality score per directed/undirected edge.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Edge weights must be strictly non-negative.
   - Guardrails: Normalization denominator adjusts for directedness and small graph sizes (V <= 2).
================================================================================
"""

import heapq
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBrandesBetweenness(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-109
      name: GraphAlgoBrandesBetweenness
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, betweenness, brandes, shortest_path_dependency, broker_identification]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          is_directed: {type: boolean, default: false}
          normalized: {type: boolean, default: true}
      outputs:
        type: object
        required: [vertex_betweenness, edge_betweenness]
        properties:
          vertex_betweenness: {type: object}
          edge_betweenness: {type: object}
      parameters:
        is_directed: {type: boolean, default: false}
        normalized: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * E + V^2 log V)
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[Tuple[TNode, float]]],
        is_directed: bool = False,
        normalized: bool = True,
    ) -> None:
        """
        Initialize the Brandes betweenness solver.

        Args:
            adjacency: Graph adjacency mapping each node to list of (target, weight) pairs.
            is_directed: Whether the graph is directed.
            normalized: Whether to scale scores by total possible vertex pairs.
        """
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = adjacency
        self._is_directed: bool = is_directed
        self._normalized: bool = normalized
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v, _ in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_betweenness(self) -> Tuple[Dict[TNode, float], Dict[Tuple[TNode, TNode], float]]:
        """
        Compute exact vertex and edge betweenness centrality for all elements.

        Returns:
            Tuple of (vertex_betweenness_dict, edge_betweenness_dict).
        """
        cb: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
        eb: Dict[Tuple[TNode, TNode], float] = {}

        for s in self._nodes:
            stack: List[TNode] = []
            pred: Dict[TNode, List[TNode]] = {w: [] for w in self._nodes}
            sigma: Dict[TNode, float] = {w: 0.0 for w in self._nodes}
            sigma[s] = 1.0
            dist: Dict[TNode, float] = {w: float("inf") for w in self._nodes}
            dist[s] = 0.0

            pq: List[Tuple[float, TNode]] = [(0.0, s)]
            while pq:
                d, v = heapq.heappop(pq)
                if d > dist[v]:
                    continue
                stack.append(v)

                for w, weight in self._adj.get(v, []):
                    c = d + weight
                    if c < dist[w]:
                        dist[w] = c
                        heapq.heappush(pq, (c, w))
                        sigma[w] = sigma[v]
                        pred[w] = [v]
                    elif c == dist[w]:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta: Dict[TNode, float] = {w: 0.0 for w in self._nodes}
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    if sigma[w] > 0:
                        c = (sigma[v] / sigma[w]) * (1.0 + delta[w])
                        delta[v] += c
                        edge_key = (v, w)
                        eb[edge_key] = eb.get(edge_key, 0.0) + c
                if w != s:
                    cb[w] += delta[w]

        n = len(self._nodes)
        if not self._is_directed:
            for u in cb:
                cb[u] *= 0.5
            for e in eb:
                eb[e] *= 0.5

        if self._normalized and n > 2:
            scale = 1.0 / ((n - 1) * (n - 2)) if self._is_directed else 2.0 / ((n - 1) * (n - 2))
            cb = {u: val * scale for u, val in cb.items()}
            scale_e = 1.0 / (n * (n - 1)) if self._is_directed else 2.0 / (n * (n - 1))
            eb = {e: val * scale_e for e, val in eb.items()}

        return cb, eb
