"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MAXIMUM CLIQUE BRANCH & BOUND (ALGO-GRAPH-DENSE-126)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Exact Maximum Clique solver using branch-and-bound with greedy vertex coloring bounds.
   Prunes recursion branches when (current_clique_size + color_bound) <= max_clique_found.
   Computes the globally maximum complete subgraph and its exact chromatic upper bound.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(2^V) worst-case, fast in practice with coloring pruning.
   - Space Complexity: O(V) recursion branch memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - max_clique_size: int - Size of the largest complete subgraph.
   - max_clique: List[TNode] - Vertices forming the maximum clique.
   - nodes_searched: int - Total recursive branch exploration states.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph.
   - Guardrails: Greedy vertex coloring provides a valid upper bound on the maximum clique size.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMaximumClique(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-126
      name: GraphAlgoMaximumClique
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, maximum_clique, branch_and_bound, vertex_coloring_bound]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [max_clique_size, max_clique, nodes_searched]
        properties:
          max_clique_size: {type: integer}
          max_clique: {type: array, items: {type: string}}
          nodes_searched: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(2^V)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Maximum Clique branch-and-bound solver.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _greedy_color(self, candidates: List[TNode]) -> Tuple[List[TNode], List[int]]:
        colors: Dict[TNode, int] = {}
        for u in candidates:
            nbr_colors = {colors[v] for v in self._adj.get(u, set()) if v in colors}
            c = 1
            while c in nbr_colors:
                c += 1
            colors[u] = c

        sorted_cand = sorted(candidates, key=lambda u: colors[u])
        color_bounds = [colors[u] for u in sorted_cand]
        return sorted_cand, color_bounds

    def find_maximum_clique(self) -> Tuple[int, List[TNode], int]:
        """
        Execute branch and bound with greedy coloring pruning.

        Returns:
            Tuple of (max_clique_size, max_clique_vertices, branch_evaluations_count).
        """
        if not self._nodes:
            return 0, [], 0

        best_clique: List[TNode] = []
        nodes_searched: int = 0

        def _search(current: List[TNode], candidates: List[TNode]) -> None:
            nonlocal best_clique, nodes_searched
            nodes_searched += 1

            if not candidates:
                if len(current) > len(best_clique):
                    best_clique = list(current)
                return

            sorted_cand, color_bounds = self._greedy_color(candidates)

            for i in range(len(sorted_cand) - 1, -1, -1):
                u = sorted_cand[i]
                c_bound = color_bounds[i]

                if len(current) + c_bound <= len(best_clique):
                    return

                nbrs_u = self._adj.get(u, set())
                next_cand = [v for v in sorted_cand[:i] if v in nbrs_u]
                current.append(u)
                _search(current, next_cand)
                current.pop()

        _search([], list(self._nodes))
        return len(best_clique), sorted(best_clique, key=lambda x: str(x)), nodes_searched
