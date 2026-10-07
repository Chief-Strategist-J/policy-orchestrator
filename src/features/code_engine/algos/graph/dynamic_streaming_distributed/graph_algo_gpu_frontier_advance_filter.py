"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GPU FRONTIER ADVANCE & FILTER (ALGO-GRAPH-PAR-219)
================================================================================

1. OVERVIEW & OBJECTIVE:
   GPU Frontier Processing Engine (Gunrock Advance-Filter abstraction).
   Implements high-throughput frontier expansion (advance along outgoing edges)
   and conditional stream compaction (filter/predicate pruning) with load-balanced chunking.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|Frontier_edges|) per advance step, O(|Frontier_nodes|) per filter.
   - Space Complexity: O(V + M) frontier queues and visited bitmaps.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.

4. OUTPUT PARAMETERS:
   - `advance(frontier)` (List[TNode]): Expanded successor frontier along outgoing edges.
   - `filter(frontier, predicate)` (List[TNode]): Compaction of frontier matching predicate.
   - `run_bfs(source)` (Dict[TNode, int]): Complete multi-step advance-filter BFS distances.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Zero duplicate vertex visits when paired with bitmap filtering.
================================================================================
"""

from typing import Callable, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGpuFrontierAdvanceFilter(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-219
      name: GraphAlgoGpuFrontierAdvanceFilter
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, gpu, gunrock, frontier_advance, filter_compaction]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        properties:
          distances: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + M)
        space: O(V + M)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize Gunrock-style advance-filter engine.

        Args:
            adjacency: Adjacency dictionary.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

    def advance(self, frontier: List[TNode]) -> List[TNode]:
        """
        Advance frontier: expand all outgoing edges from current frontier nodes.

        Args:
            frontier: Current active vertex subset.

        Returns:
            Successor vertex candidate list.
        """
        out: List[TNode] = []
        for u in frontier:
            out.extend(self._adj.get(u, []))
        return out

    def filter(self, frontier: List[TNode], predicate: Callable[[TNode], bool]) -> List[TNode]:
        """
        Filter frontier: retain unique vertices satisfying predicate.

        Args:
            frontier: Input candidate vertices.
            predicate: Boolean acceptance condition.

        Returns:
            Deduplicated, filtered vertex subset.
        """
        seen: Set[TNode] = set()
        out: List[TNode] = []
        for v in frontier:
            if v not in seen:
                seen.add(v)
                if predicate(v):
                    out.append(v)
        return out

    def run_bfs(self, source: TNode) -> Dict[TNode, int]:
        """
        Execute complete BFS traversal via alternating Advance and Filter kernels.

        Args:
            source: Root node.

        Returns:
            Dictionary of shortest hop distances.
        """
        distances: Dict[TNode, int] = {source: 0}
        frontier: List[TNode] = [source]
        depth = 0

        while frontier:
            depth += 1
            candidates = self.advance(frontier)
            frontier = self.filter(candidates, lambda v: v not in distances)
            for v in frontier:
                distances[v] = depth

        return distances
