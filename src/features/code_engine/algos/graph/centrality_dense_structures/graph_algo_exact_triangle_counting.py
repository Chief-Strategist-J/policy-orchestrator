"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EXACT TRIANGLE COUNTING (ALGO-GRAPH-DENSE-121)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Forward / compact-forward exact triangle listing and counting algorithm.
   Orders vertices by degree (degeneracy orientation) and directs edges from lower
   to higher rank. Enumerates forward intersections in O(m^1.5) time, counting each
   triangle exactly once and attributing counts to all participating vertices.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m^1.5) bounded by degree-degeneracy ordering.
   - Space Complexity: O(V + E) compact forward adjacency.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - total_triangles: int - Total number of unique 3-cliques in the graph.
   - node_triangle_counts: Dict[TNode, int] - Number of incident triangles per vertex.
   - triangles: List[Tuple[TNode, TNode, TNode]] - Full list of enumerated triangles.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Simple undirected graph with no self-loops.
   - Guardrails: Forward edge orientation prevents redundant symmetric counting.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoExactTriangleCounting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-121
      name: GraphAlgoExactTriangleCounting
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, triangles, forward_algorithm, degeneracy_ordering]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [total_triangles, node_triangle_counts, triangles]
        properties:
          total_triangles: {type: integer}
          node_triangle_counts: {type: object}
          triangles: {type: array, items: {type: array, items: {type: string}}}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m^1.5)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the exact triangle counting engine.

        Args:
            adjacency: Undirected graph adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def count_triangles(self) -> Tuple[int, Dict[TNode, int], List[Tuple[TNode, TNode, TNode]]]:
        """
        Execute forward triangle counting with degree ordering.

        Returns:
            Tuple of (total_triangles, node_triangle_counts, triangles_list).
        """
        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        order = sorted(self._nodes, key=lambda u: (degrees[u], str(u)))
        rank = {u: i for i, u in enumerate(order)}

        forward_adj: Dict[TNode, List[TNode]] = {u: [] for u in self._nodes}
        forward_set: Dict[TNode, Set[TNode]] = {u: set() for u in self._nodes}

        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if rank[v] > rank[u]:
                    forward_adj[u].append(v)
                    forward_set[u].add(v)

        total_triangles: int = 0
        node_counts: Dict[TNode, int] = {u: 0 for u in self._nodes}
        triangles: List[Tuple[TNode, TNode, TNode]] = []

        for u in self._nodes:
            f_u = forward_adj[u]
            for v in f_u:
                common = forward_set[u] & forward_set[v]
                for w in common:
                    total_triangles += 1
                    node_counts[u] += 1
                    node_counts[v] += 1
                    node_counts[w] += 1
                    triangles.append((u, v, w))

        return total_triangles, node_counts, triangles
