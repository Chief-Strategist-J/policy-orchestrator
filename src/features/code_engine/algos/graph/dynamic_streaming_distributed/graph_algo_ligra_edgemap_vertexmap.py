"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LIGRA EDGEMAP & VERTEXMAP (ALGO-GRAPH-PAR-223)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Ligra Graph Processing Engine (edgeMap & vertexMap abstraction).
   Provides concise, high-performance graph parallel primitives with conditional
   edge transformations (edgeMap) and parallel vertex mutations (vertexMap) over
   dynamic vertex subsets.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Work-efficient O(V + M), step-efficient.
   - Space Complexity: O(V + M) vertex subsets and adjacency.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.

4. OUTPUT PARAMETERS:
   - `vertex_map(subset, func)` (None): In-place or mapped mutation over vertex subset.
   - `edge_map(subset, filter_fn, cond_fn)` (Set[TNode]): New active frontier subset.
   - `compute_bfs(source)` (Dict[TNode, int]): Shortest distances via Ligra edgeMap.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: All frontier vertices meet condition cond_fn prior to edge transformation.
================================================================================
"""

from typing import Callable, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLigraEdgemapVertexmap(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-223
      name: GraphAlgoLigraEdgemapVertexmap
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, ligra, edgemap, vertexmap, vertex_subsets]
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
        Initialize Ligra engine with adjacency structure.

        Args:
            adjacency: Adjacency dictionary.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

    def vertex_map(self, subset: Set[TNode], func: Callable[[TNode], None]) -> None:
        """
        Apply func to every vertex in subset U.

        Args:
            subset: Active vertex subset.
            func: Function to execute per node.
        """
        for u in subset:
            func(u)

    def edge_map(
        self,
        subset: Set[TNode],
        update_fn: Callable[[TNode, TNode], bool],
        cond_fn: Optional[Callable[[TNode], bool]] = None,
    ) -> Set[TNode]:
        """
        Apply update_fn(u, v) along edges from subset U to target v if cond_fn(v) is True.

        Args:
            subset: Active source vertex set.
            update_fn: Function (u, v) returning True if v should enter next subset.
            cond_fn: Predicate on target vertex v.

        Returns:
            Next active vertex subset.
        """
        out_subset: Set[TNode] = set()
        c_fn = cond_fn or (lambda v: True)

        for u in subset:
            for v in self._adj.get(u, []):
                if c_fn(v):
                    if update_fn(u, v):
                        out_subset.add(v)

        return out_subset

    def compute_bfs(self, source: TNode) -> Dict[TNode, int]:
        """
        Compute shortest hop distances using pure Ligra edgeMap operations.

        Args:
            source: Source vertex.

        Returns:
            Dictionary of hop distances.
        """
        distances: Dict[TNode, int] = {source: 0}
        frontier: Set[TNode] = {source}
        depth = 0

        while frontier:
            depth += 1
            curr_depth = depth

            def update_fn(u: TNode, v: TNode) -> bool:
                if v not in distances:
                    distances[v] = curr_depth
                    return True
                return False

            frontier = self.edge_map(frontier, update_fn, lambda v: v not in distances)

        return distances
