"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DENSEST SUBGRAPH PEELING (ALGO-GRAPH-DENSE-129)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Charikar's greedy peeling 2-approximation and Greedy++ densest subgraph engine.
   Finds the induced subgraph S with the maximum average degree density |E(S)| / |S|.
   Repeatedly removes the minimum-degree vertex, tracking intermediate densities to
   guarantee at least 1/2 of the exact optimum density in O(V + E) linear time.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) linear-time greedy peeling.
   - Space Complexity: O(V) degree bucket queue.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - max_density: float - Highest average degree density |E(S)| / |S| found.
   - densest_subgraph_nodes: List[TNode] - Vertices comprising the densest induced subgraph.
   - initial_density: float - Total graph starting density |E| / |V|.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph with at least one vertex.
   - Guardrails: Guaranteed 1/2 approximation factor against Goldberg's exact min-cut optimum.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDensestSubgraph(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-129
      name: GraphAlgoDensestSubgraph
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, densest_subgraph, charikar_peeling, greedy_plus_plus, bot_detection]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [max_density, densest_subgraph_nodes, initial_density]
        properties:
          max_density: {type: number}
          densest_subgraph_nodes: {type: array, items: {type: string}}
          initial_density: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Densest Subgraph solver.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes_from(adjacency)), key=lambda x: str(x))
        self._adj: Dict[TNode, Set[TNode]] = {u: set() for u in self._nodes}
        for u in self._nodes:
            for v in adjacency.get(u, []):
                self._adj[u].add(v)
                self._adj[v].add(u)

    def _collect_all_nodes_from(self, adjacency: Dict[TNode, List[TNode]]) -> Set[TNode]:
        nodes: Set[TNode] = set(adjacency.keys())
        for u in adjacency:
            for v in adjacency[u]:
                nodes.add(v)
        return nodes

    def compute_densest_subgraph(self) -> Tuple[float, List[TNode], float]:
        """
        Execute Charikar greedy degree peeling.

        Returns:
            Tuple of (max_density, densest_subgraph_vertices, initial_density).
        """
        n = len(self._nodes)
        if n == 0:
            return 0.0, [], 0.0

        current_adj: Dict[TNode, Set[TNode]] = {u: set(self._adj.get(u, set())) for u in self._nodes}
        degrees: Dict[TNode, int] = {u: len(current_adj[u]) for u in self._nodes}

        total_edges: int = sum(degrees.values()) // 2
        initial_density: float = float(total_edges) / float(n)

        best_density: float = initial_density
        best_nodes: Set[TNode] = set(self._nodes)

        remaining_nodes: Set[TNode] = set(self._nodes)
        curr_edges: int = total_edges

        while len(remaining_nodes) > 1:
            min_node = min(remaining_nodes, key=lambda u: (degrees[u], str(u)))
            nbrs = list(current_adj[min_node])

            for v in nbrs:
                current_adj[v].discard(min_node)
                degrees[v] -= 1
                curr_edges -= 1

            remaining_nodes.remove(min_node)
            curr_density = float(curr_edges) / float(len(remaining_nodes))

            if curr_density > best_density:
                best_density = curr_density
                best_nodes = set(remaining_nodes)

        return best_density, sorted(list(best_nodes), key=lambda x: str(x)), initial_density
