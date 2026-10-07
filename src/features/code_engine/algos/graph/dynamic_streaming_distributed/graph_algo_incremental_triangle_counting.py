"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Incremental Triangle Counting (ALGO-GRAPH-DYN-205)

1. OVERVIEW & OBJECTIVE:
Maintains exact global and per-vertex triangle counts dynamically as edges are inserted or
deleted in real-time, executing fast hash-set / bitmap neighborhood intersections O(min(deg(u), deg(v)))
per edge update.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for adjacency sets and triangle counts.
- Time Complexity: O(min(deg(u), deg(v))) per edge addition or deletion.
- Invariants:
  - Global triangle count == (1/3) * sum_{v in V} local_triangles(v).
  - Adding edge (u, v) creates exactly |N(u) intersect N(v)| new triangles.

3. INPUT PARAMETERS:
- None for initialization.

4. OUTPUT PARAMETERS:
- `IncrementalTriangleResult`: Total global triangles, per-node triangle counts, and triangles created/destroyed in the update.

5. AGENT CONTRACT:
- Role: Real-time network clustering and dense subgraph monitor.
- Rules: Zero inline comments in method bodies.
- Guardrails: Duplicate edge insertions are handled idempotently.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class IncrementalTriangleResult(Generic[TNode]):
    """
    Result container for incremental triangle updates.
    """
    total_triangles: int
    local_triangles: Dict[TNode, int]
    delta_triangles: int


class GraphAlgoIncrementalTriangleCounting(Generic[TNode]):
    """
    Maintains exact global and local triangle counts under dynamic edge streams.

    ```yaml
    contract_id: ALGO-GRAPH-DYN-205
    inputs: {}
    outputs:
      result: IncrementalTriangleResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - dynamic
      - triangle_counting
      - clustering_coefficient
      - streaming
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(min(deg(u), deg(v)))
      space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        self._adj: Dict[TNode, Set[TNode]] = defaultdict(set)
        self._local_counts: Dict[TNode, int] = defaultdict(int)
        self._total_triangles: int = 0

    def add_edge(self, u: TNode, v: TNode) -> IncrementalTriangleResult[TNode]:
        """
        Inserts an edge and updates triangle counts.

        Args:
            u: First endpoint.
            v: Second endpoint.

        Returns:
            IncrementalTriangleResult with updated counts and new triangles formed.
        """
        if u == v or v in self._adj[u]:
            return self.get_counts(delta=0)

        common_neighbors = self._adj[u] & self._adj[v]
        k = len(common_neighbors)

        self._adj[u].add(v)
        self._adj[v].add(u)

        self._total_triangles += k
        self._local_counts[u] += k
        self._local_counts[v] += k
        for w in common_neighbors:
            self._local_counts[w] += 1

        return self.get_counts(delta=k)

    def remove_edge(self, u: TNode, v: TNode) -> IncrementalTriangleResult[TNode]:
        """
        Deletes an edge and subtracts destroyed triangles.

        Args:
            u: First endpoint.
            v: Second endpoint.

        Returns:
            IncrementalTriangleResult with updated counts.
        """
        if u not in self._adj or v not in self._adj[u]:
            return self.get_counts(delta=0)

        self._adj[u].remove(v)
        self._adj[v].remove(u)

        common_neighbors = self._adj[u] & self._adj[v]
        k = len(common_neighbors)

        self._total_triangles -= k
        self._local_counts[u] -= k
        self._local_counts[v] -= k
        for w in common_neighbors:
            self._local_counts[w] -= 1

        return self.get_counts(delta=-k)

    def get_counts(self, delta: int = 0) -> IncrementalTriangleResult[TNode]:
        """
        Returns current triangle counts.

        Args:
            delta: Change in triangle count from last operation.

        Returns:
            IncrementalTriangleResult container.
        """
        return IncrementalTriangleResult(
            total_triangles=self._total_triangles,
            local_triangles=dict(self._local_counts),
            delta_triangles=delta,
        )
