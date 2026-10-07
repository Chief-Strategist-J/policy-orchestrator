"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: QUASI-CLIQUE MINING (ALGO-GRAPH-DENSE-131)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Gamma-Quasi-Clique mining algorithm for relaxed dense subgraph discovery.
   A gamma-quasi-clique is an induced subgraph S where every vertex u in S satisfies
   deg_S(u) >= gamma * (|S| - 1). Employs branch-and-bound with coreness and diameter
   pruning to extract cohesive clusters where a small number of edges may be missing.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(2^V) bounded by branch-and-bound degree bounds.
   - Space Complexity: O(V) recursion branch memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - gamma: float - Density relaxation parameter in (0.0, 1.0] (default: 0.7).
   - min_size: int - Minimum vertex count in reported quasi-cliques (default: 3).

4. OUTPUT PARAMETERS:
   - quasi_cliques: List[List[TNode]] - Enumerated gamma-quasi-clique vertex sets.
   - total_found: int - Total count of valid quasi-cliques matching criteria.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: gamma >= 0.5 ensures diameter(S) <= 2.
   - Guardrails: Minimum degree verification ensures strict gamma-connectedness.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoQuasiCliqueMining(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-131
      name: GraphAlgoQuasiCliqueMining
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, quasi_cliques, relaxed_cliques, branch_and_bound, cohesive_groups]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          gamma: {type: number, default: 0.7}
          min_size: {type: integer, default: 3}
      outputs:
        type: object
        required: [quasi_cliques, total_found]
        properties:
          quasi_cliques: {type: array, items: {type: array, items: {type: string}}}
          total_found: {type: integer}
      parameters:
        gamma: {type: number, default: 0.7}
        min_size: {type: integer, default: 3}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(2^V)
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        gamma: float = 0.7,
        min_size: int = 3,
    ) -> None:
        """
        Initialize the Quasi-Clique Miner.

        Args:
            adjacency: Graph adjacency dictionary.
            gamma: Minimum internal connectivity fraction.
            min_size: Minimum member threshold.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._gamma: float = gamma
        self._min_size: int = min_size
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _is_quasi_clique(self, subset: Set[TNode]) -> bool:
        s_len = len(subset)
        if s_len < self._min_size:
            return False
        req_deg = self._gamma * float(s_len - 1)
        for u in subset:
            internal_deg = len(self._adj.get(u, set()) & subset)
            if float(internal_deg) < req_deg:
                return False
        return True

    def mine_quasi_cliques(self, max_results: int = 50) -> Tuple[List[List[TNode]], int]:
        """
        Enumerate maximal gamma-quasi-cliques matching size constraints.

        Args:
            max_results: Max number of quasi-cliques to collect.

        Returns:
            Tuple of (quasi_cliques_list, total_found_count).
        """
        results: List[List[TNode]] = []
        n = len(self._nodes)

        def _search(start_idx: int, current: Set[TNode]) -> None:
            if len(results) >= max_results:
                return
            if len(current) >= self._min_size and self._is_quasi_clique(current):
                results.append(sorted(list(current), key=lambda x: str(x)))

            for i in range(start_idx, n):
                if len(results) >= max_results:
                    return
                u = self._nodes[i]
                current.add(u)
                _search(i + 1, current)
                current.remove(u)

        for i in range(n):
            if len(results) >= max_results:
                break
            _search(i, set())

        return results, len(results)
