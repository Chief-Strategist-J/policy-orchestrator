"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Incremental Topological Sort - Pearce-Kelly (ALGO-GRAPH-DYN-202)

1. OVERVIEW & OBJECTIVE:
Maintains an exact topological ordering of a Directed Acyclic Graph (DAG) incrementally as
edges are added in real-time, detecting and certifying directed cycles instantaneously via
Pearce-Kelly bounded DFS exploration without re-sorting the entire graph.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for node-order mappings and graph edges.
- Time Complexity: O(|delta_V| + |delta_E|) proportional to the affected topological index window.
- Invariants:
  - For all existing directed edges (u, v), ord(u) < ord(v).
  - If adding (u, v) creates a cycle, the edge is rejected and the exact cycle certificate is returned.

3. INPUT PARAMETERS:
- `nodes` (Iterable[TNode]): Initial set of graph vertices.

4. OUTPUT PARAMETERS:
- `IncrementalTopoResult`: Boolean `added`, updated topological ordering dictionary `{node: ord}`, and `cycle_certificate` (if rejected).

5. AGENT CONTRACT:
- Role: Real-time dependency acyclicity verifier and task scheduler.
- Rules: Enforce strict cycle rejection with verifiable directed cycle path.
- Guardrails: Non-existent vertices are automatically initialized and placed at the end of the order.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class IncrementalTopoResult(Generic[TNode]):
    """
    Result container for incremental topological edge insertion.
    """
    added: bool
    topological_order: Dict[TNode, int]
    cycle_certificate: Optional[List[TNode]]


class GraphAlgoIncrementalTopologicalSortPearceKelly(Generic[TNode]):
    """
    Maintains dynamic topological order via Pearce-Kelly online reordering.

    ```yaml
    contract_id: ALGO-GRAPH-DYN-202
    inputs:
      nodes: Iterable[TNode]
    outputs:
      result: IncrementalTopoResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - dynamic
      - topological_sort
      - pearce_kelly
      - cycle_detection
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|delta_V| + |delta_E|)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, nodes: Optional[Iterable[TNode]] = None) -> None:
        """
        Args:
            nodes: Optional initial set of graph nodes.
        """
        self._adj: Dict[TNode, Set[TNode]] = defaultdict(set)
        self._rev_adj: Dict[TNode, Set[TNode]] = defaultdict(set)
        self._ord: Dict[TNode, int] = {}

        if nodes is not None:
            sorted_nodes = sorted(list(nodes), key=lambda x: str(x))
            for i, u in enumerate(sorted_nodes):
                self._ord[u] = i

    def add_edge(self, u: TNode, v: TNode) -> IncrementalTopoResult[TNode]:
        """
        Attempts to add directed edge u -> v, maintaining topological order or detecting cycle.

        Args:
            u: Source vertex.
            v: Target vertex.

        Returns:
            IncrementalTopoResult with success status and cycle certificate if rejected.
        """
        if u not in self._ord:
            self._ord[u] = len(self._ord)
        if v not in self._ord:
            self._ord[v] = len(self._ord)

        if v in self._adj[u]:
            return IncrementalTopoResult(added=True, topological_order=dict(self._ord), cycle_certificate=None)

        if u == v:
            return IncrementalTopoResult(added=False, topological_order=dict(self._ord), cycle_certificate=[u, v])

        ord_u = self._ord[u]
        ord_v = self._ord[v]

        if ord_u < ord_v:
            self._adj[u].add(v)
            self._rev_adj[v].add(u)
            return IncrementalTopoResult(added=True, topological_order=dict(self._ord), cycle_certificate=None)

        forward_visited: List[TNode] = []
        forward_set: Set[TNode] = set()
        parent_map: Dict[TNode, TNode] = {}

        cycle_found = self._dfs_forward(v, u, ord_u, forward_visited, forward_set, parent_map)
        if cycle_found:
            cycle = [u]
            curr = u
            while curr != v:
                curr = parent_map[curr]
                cycle.append(curr)
            cycle.reverse()
            cycle.append(u)
            return IncrementalTopoResult(added=False, topological_order=dict(self._ord), cycle_certificate=cycle)

        backward_visited: List[TNode] = []
        backward_set: Set[TNode] = set()
        self._dfs_backward(u, ord_v, backward_visited, backward_set)

        affected_slots = sorted([self._ord[node] for node in backward_visited + forward_visited])
        new_order_nodes = backward_visited + forward_visited

        for idx, node in enumerate(new_order_nodes):
            self._ord[node] = affected_slots[idx]

        self._adj[u].add(v)
        self._rev_adj[v].add(u)

        return IncrementalTopoResult(added=True, topological_order=dict(self._ord), cycle_certificate=None)

    def _dfs_forward(
        self,
        curr: TNode,
        target: TNode,
        upper_bound_ord: int,
        visited: List[TNode],
        visited_set: Set[TNode],
        parent_map: Dict[TNode, TNode],
    ) -> bool:
        visited_set.add(curr)
        visited.append(curr)

        for nxt in sorted(self._adj[curr], key=lambda x: str(x)):
            if nxt == target:
                parent_map[nxt] = curr
                return True
            if self._ord[nxt] <= upper_bound_ord and nxt not in visited_set:
                parent_map[nxt] = curr
                if self._dfs_forward(nxt, target, upper_bound_ord, visited, visited_set, parent_map):
                    return True
        return False

    def _dfs_backward(
        self,
        curr: TNode,
        lower_bound_ord: int,
        visited: List[TNode],
        visited_set: Set[TNode],
    ) -> None:
        visited_set.add(curr)
        for prev in sorted(self._rev_adj[curr], key=lambda x: str(x)):
            if self._ord[prev] >= lower_bound_ord and prev not in visited_set:
                self._dfs_backward(prev, lower_bound_ord, visited, visited_set)
        visited.append(curr)

    def get_order(self) -> Dict[TNode, int]:
        """
        Returns the current topological position map.

        Returns:
            Dictionary mapping node to topological integer index.
        """
        return dict(self._ord)

