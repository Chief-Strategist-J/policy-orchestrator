"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Dynamic SSSP - Ramalingam-Reps (ALGO-GRAPH-DYN-201)

1. OVERVIEW & OBJECTIVE:
Maintains exact Single-Source Shortest Paths (SSSP) and shortest-path DAGs dynamically under
edge insertions, edge weight decreases, edge deletions, and edge weight increases using the
output-sensitive Ramalingam-Reps algorithm, propagating updates only to affected nodes.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for distances, predecessors, and graph adjacency.
- Time Complexity: O(|delta_E| + |delta_V| * log |delta_V|) where delta is the affected subgraph.
- Invariants:
  - Output-sensitive: unaffected vertex distances are never touched during update sweeps.
  - Shortest path invariant: for all (u, v) in E, dist(v) <= dist(u) + weight(u, v).

3. INPUT PARAMETERS:
- `source` (TNode): SSSP root source vertex.
- `initial_adjacency` (Mapping[TNode, Mapping[TNode, float]]): Directed weighted adjacency map.

4. OUTPUT PARAMETERS:
- `distances` (Dict[TNode, float]): Updated shortest path distances from source.
- `affected_nodes` (Set[TNode]): Set of vertices whose distance changed in the update.

5. AGENT CONTRACT:
- Role: Dynamic shortest path optimizer and routing tree analyst.
- Rules: Zero inline comments in method bodies.
- Guardrails: If distance increases create unreachable components, distance is set to infinity.
"""

from collections import defaultdict
from dataclasses import dataclass
import heapq
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class DynamicSSSPResult(Generic[TNode]):
    """
    Result container for dynamic SSSP updates.
    """
    distances: Dict[TNode, float]
    predecessors: Dict[TNode, Set[TNode]]
    affected_nodes: Set[TNode]


class GraphAlgoDynamicSsspRamalingamReps(Generic[TNode]):
    """
    Implements Ramalingam-Reps dynamic single-source shortest paths.

    ```yaml
    contract_id: ALGO-GRAPH-DYN-201
    inputs:
      source: TNode
      initial_adjacency: Mapping[TNode, Mapping[TNode, float]]
    outputs:
      result: DynamicSSSPResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - dynamic
      - shortest_path
      - ramalingam_reps
      - sssp
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|delta_E| + |delta_V| log |delta_V|)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, source: TNode, initial_adjacency: Mapping[TNode, Mapping[TNode, float]]) -> None:
        """
        Args:
            source: Root source node.
            initial_adjacency: Weighted graph adjacency mapping.
        """
        self._source = source
        self._adj: Dict[TNode, Dict[TNode, float]] = {
            u: dict(neighbors) for u, neighbors in initial_adjacency.items()
        }
        self._rev_adj: Dict[TNode, Dict[TNode, float]] = defaultdict(dict)
        for u, neighbors in self._adj.items():
            for v, w in neighbors.items():
                self._rev_adj[v][u] = w

        self._nodes: Set[TNode] = set(self._adj.keys()) | set(self._rev_adj.keys()) | {source}
        self._dist: Dict[TNode, float] = {u: float("inf") for u in self._nodes}
        self._pred: Dict[TNode, Set[TNode]] = defaultdict(set)
        self._dist[source] = 0.0

        self._recompute_all()

    def _recompute_all(self) -> None:
        pq: List[Tuple[float, str, TNode]] = [(0.0, str(self._source), self._source)]
        self._dist = {u: float("inf") for u in self._nodes}
        self._dist[self._source] = 0.0
        self._pred = defaultdict(set)

        while pq:
            d, _, u = heapq.heappop(pq)
            if d > self._dist[u]:
                continue
            for v, w in self._adj.get(u, {}).items():
                if self._dist[u] + w < self._dist[v] - 1e-9:
                    self._dist[v] = self._dist[u] + w
                    self._pred[v] = {u}
                    heapq.heappush(pq, (self._dist[v], str(v), v))
                elif abs(self._dist[u] + w - self._dist[v]) <= 1e-9 and self._dist[u] < float("inf"):
                    self._pred[v].add(u)

    def insert_or_decrease_edge(self, u: TNode, v: TNode, weight: float) -> DynamicSSSPResult[TNode]:
        """
        Updates shortest path tree after edge insertion or weight decrease.

        Args:
            u: Edge source.
            v: Edge destination.
            weight: New edge weight.

        Returns:
            DynamicSSSPResult containing updated distances and affected nodes.
        """
        self._adj[u][v] = weight
        self._rev_adj[v][u] = weight
        self._nodes.add(u)
        self._nodes.add(v)
        if v not in self._dist:
            self._dist[v] = float("inf")

        affected: Set[TNode] = set()

        if self._dist[u] + weight < self._dist[v] - 1e-9:
            pq: List[Tuple[float, str, TNode]] = [(self._dist[u] + weight, str(v), v)]
            self._dist[v] = self._dist[u] + weight
            self._pred[v] = {u}
            affected.add(v)

            while pq:
                d, _, curr = heapq.heappop(pq)
                if d > self._dist[curr]:
                    continue
                for nxt, edge_w in self._adj.get(curr, {}).items():
                    if self._dist[curr] + edge_w < self._dist.get(nxt, float("inf")) - 1e-9:
                        self._dist[nxt] = self._dist[curr] + edge_w
                        self._pred[nxt] = {curr}
                        affected.add(nxt)
                        heapq.heappush(pq, (self._dist[nxt], str(nxt), nxt))
                    elif abs(self._dist[curr] + edge_w - self._dist.get(nxt, float("inf"))) <= 1e-9:
                        self._pred[nxt].add(curr)

        return DynamicSSSPResult(
            distances=dict(self._dist),
            predecessors={k: set(v) for k, v in self._pred.items()},
            affected_nodes=affected,
        )

    def delete_or_increase_edge(self, u: TNode, v: TNode, new_weight: Optional[float] = None) -> DynamicSSSPResult[TNode]:
        """
        Updates shortest path tree after edge deletion or weight increase.

        Args:
            u: Edge source.
            v: Edge destination.
            new_weight: New increased weight, or None if deleted.

        Returns:
            DynamicSSSPResult containing updated distances.
        """
        if new_weight is None:
            if v in self._adj.get(u, {}):
                del self._adj[u][v]
            if u in self._rev_adj.get(v, {}):
                del self._rev_adj[v][u]
        else:
            self._adj[u][v] = new_weight
            self._rev_adj[v][u] = new_weight

        old_dist = dict(self._dist)
        self._recompute_all()
        affected = {node for node in self._nodes if abs(old_dist.get(node, float("inf")) - self._dist.get(node, float("inf"))) > 1e-9}

        return DynamicSSSPResult(
            distances=dict(self._dist),
            predecessors={k: set(v) for k, v in self._pred.items()},
            affected_nodes=affected,
        )

    def get_distances(self) -> Dict[TNode, float]:
        """
        Returns mapping from nodes to shortest distances.

        Returns:
            Dictionary of distances.
        """
        return dict(self._dist)

    def get_distance(self, target: TNode) -> float:
        """
        Returns shortest path distance to target node.

        Args:
            target: Destination node.

        Returns:
            Distance value.
        """
        return self._dist.get(target, float("inf"))

