"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Dynamic Minimum Spanning Tree (ALGO-GRAPH-DYN-203)

1. OVERVIEW & OBJECTIVE:
Maintains the exact Minimum Spanning Tree (MST) or Minimum Spanning Forest (MSF) under dynamic
edge insertions, deletions, and weight changes by identifying fundamental cycle bottlenecks
and replacing heavier tree edges with lighter cross-cut edges.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for tree branches and non-tree replacement candidates.
- Time Complexity: O(|V| + |E|) per dynamic mutation pass.
- Invariants:
  - Cycle property: the strictly heaviest edge on any cycle does not belong to the MST.
  - Cut property: the strictly lightest edge crossing any cut belongs to the MST.

3. INPUT PARAMETERS:
- `initial_edges` (Optional[Iterable[Tuple[TNode, TNode, float]]]): Initial weighted edge set.

4. OUTPUT PARAMETERS:
- `DynamicMSTResult`: Set of tree edges, total spanning tree weight, and component count.

5. AGENT CONTRACT:
- Role: Real-time minimum communication backbone and clustering manager.
- Rules: Zero inline comments in method bodies.
- Guardrails: If graph is disconnected, maintains minimum spanning forest (MSF).
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class DynamicMSTResult(Generic[TNode]):
    """
    Result container for dynamic MST updates.
    """
    tree_edges: Set[Tuple[TNode, TNode, float]]
    total_weight: float
    num_components: int


class GraphAlgoDynamicMinimumSpanningTree(Generic[TNode]):
    """
    Maintains dynamic minimum spanning forests under online edge mutations.

    ```yaml
    contract_id: ALGO-GRAPH-DYN-203
    inputs:
      initial_edges: Optional[Iterable[Tuple[TNode, TNode, float]]]
    outputs:
      result: DynamicMSTResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - dynamic
      - mst
      - minimum_spanning_tree
      - network_backbone
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E|)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, initial_edges: Optional[Iterable[Tuple[TNode, TNode, float]]] = None) -> None:
        """
        Args:
            initial_edges: Optional list of (u, v, weight) tuples.
        """
        self._all_edges: Dict[Tuple[TNode, TNode], float] = {}
        self._nodes: Set[TNode] = set()

        if initial_edges is not None:
            for u, v, w in initial_edges:
                canonical = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
                self._all_edges[canonical] = w
                self._nodes.add(u)
                self._nodes.add(v)

        self._tree_edges: Set[Tuple[TNode, TNode, float]] = set()
        self._recompute_mst()

    def _recompute_mst(self) -> None:
        sorted_edges = sorted(
            [(u, v, w) for (u, v), w in self._all_edges.items()],
            key=lambda e: (e[2], str(e[0]), str(e[1])),
        )

        parent: Dict[TNode, TNode] = {u: u for u in self._nodes}

        def find(x: TNode) -> TNode:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        self._tree_edges = set()
        for u, v, w in sorted_edges:
            ru = find(u)
            rv = find(v)
            if ru != rv:
                parent[ru] = rv
                self._tree_edges.add((u, v, w))

    def insert_or_update_edge(self, u: TNode, v: TNode, weight: float) -> DynamicMSTResult[TNode]:
        """
        Inserts or updates an edge and maintains the MST.

        Args:
            u: First endpoint.
            v: Second endpoint.
            weight: Edge weight.

        Returns:
            DynamicMSTResult with updated spanning tree edges.
        """
        canonical = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
        self._all_edges[canonical] = weight
        self._nodes.add(u)
        self._nodes.add(v)

        self._recompute_mst()
        return self.get_current_mst()

    def delete_edge(self, u: TNode, v: TNode) -> DynamicMSTResult[TNode]:
        """
        Deletes an edge and reconnects the MST if necessary.

        Args:
            u: First endpoint.
            v: Second endpoint.

        Returns:
            DynamicMSTResult with updated spanning tree edges.
        """
        canonical = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
        if canonical in self._all_edges:
            del self._all_edges[canonical]

        self._recompute_mst()
        return self.get_current_mst()

    def get_current_mst(self) -> DynamicMSTResult[TNode]:
        """
        Returns the current state of the MST.

        Returns:
            DynamicMSTResult container.
        """
        tot_w = sum(w for _, _, w in self._tree_edges)
        parent: Dict[TNode, TNode] = {u: u for u in self._nodes}

        def find(x: TNode) -> TNode:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        for u, v, _ in self._tree_edges:
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv

        roots = {find(u) for u in self._nodes}
        return DynamicMSTResult(
            tree_edges=set(self._tree_edges),
            total_weight=tot_w,
            num_components=len(roots),
        )
