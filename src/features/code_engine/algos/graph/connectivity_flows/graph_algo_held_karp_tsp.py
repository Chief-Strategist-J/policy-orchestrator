"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HELD-KARP EXACT TSP (ALGO-GRAPH-ROUT-97)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Held-Karp dynamic programming algorithm for the exact Traveling Salesperson Problem (TSP).
   Evaluates optimal sub-paths across subset bitmasks to find the exact minimum-cost Hamiltonian cycle.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N^2 * 2^N) state transitions.
   - Space Complexity: O(N * 2^N) DP table memoization.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guardrails: Capped for graphs with V <= 22 nodes (GX1).
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHeldKarpTsp(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROUT-97
      name: GraphAlgoHeldKarpTsp
      version: 1.0.0
      category: graph_routing
      capability_tags: [graph, tsp, held_karp, dynamic_programming, exact_hamiltonian_cycle]
      inputs:
        type: object
        required: [nodes, distance_matrix]
        properties:
          nodes:
            type: array
            items: {type: string}
          distance_matrix:
            type: array
            items:
              type: array
              items: {type: number}
      outputs:
        type: object
        required: [tour_cost, tour_path]
        properties:
          tour_cost: {type: number}
          tour_path:
            type: array
            items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(N^2 * 2^N)
        space: O(N * 2^N)
    ---
    """

    def __init__(self, nodes: List[TNode], distance_matrix: List[List[float]]) -> None:
        self._nodes: List[TNode] = nodes
        self._dist: List[List[float]] = distance_matrix

    def solve_exact_tsp(self) -> Tuple[float, List[TNode]]:
        n = len(self._nodes)
        if n == 0:
            return 0.0, []
        if n == 1:
            return 0.0, [self._nodes[0], self._nodes[0]]
        if n > 22:
            raise ValueError(f"Held-Karp exact TSP is capped at V <= 22 nodes (requested {n})")

        memo: Dict[Tuple[int, int], Tuple[float, int]] = {}

        for i in range(1, n):
            memo[((1 << i) | 1, i)] = (self._dist[0][i], 0)

        for mask_size in range(3, n + 1):
            for mask in range(1, 1 << n):
                if (mask & 1) == 0:
                    continue
                if bin(mask).count("1") != mask_size:
                    continue

                for j in range(1, n):
                    if (mask & (1 << j)) == 0:
                        continue
                    prev_mask = mask ^ (1 << j)

                    min_cost = float("inf")
                    best_k = -1

                    for k in range(1, n):
                        if (prev_mask & (1 << k)) != 0:
                            prev_res = memo.get((prev_mask, k))
                            if prev_res is not None:
                                cost = prev_res[0] + self._dist[k][j]
                                if cost < min_cost:
                                    min_cost = cost
                                    best_k = k

                    if best_k != -1:
                        memo[(mask, j)] = (min_cost, best_k)

        full_mask = (1 << n) - 1
        opt_cost = float("inf")
        last_node = -1

        for j in range(1, n):
            res = memo.get((full_mask, j))
            if res is not None:
                cost = res[0] + self._dist[j][0]
                if cost < opt_cost:
                    opt_cost = cost
                    last_node = j

        if last_node == -1:
            return float("inf"), []

        tour_indices: List[int] = [0]
        curr_mask = full_mask
        curr_node = last_node

        while curr_node != 0:
            tour_indices.append(curr_node)
            _, prev_node = memo[(curr_mask, curr_node)]
            curr_mask = curr_mask ^ (1 << curr_node)
            curr_node = prev_node

        tour_indices.reverse()
        tour_indices.append(0)

        tour_nodes = [self._nodes[idx] for idx in tour_indices]
        return opt_cost, tour_nodes
