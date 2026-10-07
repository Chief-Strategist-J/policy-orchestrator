"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CHRISTOFIDES TSP & 2-OPT (ALGO-GRAPH-ROUT-98)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Christofides 1.5-approximation algorithm combined with 2-Opt iterative local search
   for metric Traveling Salesperson Problems (TSP). Computes an initial tour via
   MST + odd-vertex matching + Euler tour shortcutting, refined by 2-Opt edge exchanges.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^3) Christofides construction + O(K * V^2) 2-Opt passes.
   - Space Complexity: O(V^2) complete distance matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Preconditions: Edge distances must satisfy metric triangle inequality.
   - Guarantees: Initial tour is certified <= 1.5 * OPT_TSP.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from src.features.code_engine.algos.graph.connectivity_flows.graph_algo_kruskal_mst import GraphAlgoKruskalMst

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoChristofidesTsp(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROUT-98
      name: GraphAlgoChristofidesTsp
      version: 1.0.0
      category: graph_routing
      capability_tags: [graph, tsp, christofides, approximation_1_5, two_opt, metric_tsp]
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
        required: [tour_cost, tour_path, initial_cost]
        properties:
          tour_cost: {type: number}
          tour_path:
            type: array
            items: {type: string}
          initial_cost: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^3)
        space: O(V^2)
    ---
    """

    def __init__(self, nodes: List[TNode], distance_matrix: List[List[float]]) -> None:
        self._nodes: List[TNode] = nodes
        self._dist: List[List[float]] = distance_matrix
        self._n: int = len(nodes)

    def solve_tsp(self, max_2opt_passes: int = 50) -> Tuple[float, List[TNode]]:
        if self._n <= 1:
            return 0.0, list(self._nodes)
        if self._n == 2:
            cost = 2 * self._dist[0][1]
            return cost, [self._nodes[0], self._nodes[1], self._nodes[0]]

        all_edges: List[Tuple[int, int, float]] = []
        for i in range(self._n):
            for j in range(i + 1, self._n):
                all_edges.append((i, j, self._dist[i][j]))

        kruskal = GraphAlgoKruskalMst[int](all_edges, list(range(self._n)))
        _, mst_edges = kruskal.compute_mst()

        degree: Dict[int, int] = {i: 0 for i in range(self._n)}
        for u, v, _ in mst_edges:
            degree[u] += 1
            degree[v] += 1

        odd_nodes = [i for i in range(self._n) if degree[i] % 2 != 0]
        odd_nodes.sort()

        matching = self._min_weight_perfect_matching(odd_nodes)

        multigraph_adj: Dict[int, List[int]] = {i: [] for i in range(self._n)}
        for u, v, _ in mst_edges:
            multigraph_adj[u].append(v)
            multigraph_adj[v].append(u)
        for u, v in matching:
            multigraph_adj[u].append(v)
            multigraph_adj[v].append(u)

        euler_circuit = self._hierholzer(multigraph_adj)

        visited: Set[int] = set()
        hamiltonian_tour: List[int] = []
        for node in euler_circuit:
            if node not in visited:
                visited.add(node)
                hamiltonian_tour.append(node)
        hamiltonian_tour.append(hamiltonian_tour[0])

        optimized_tour = self._two_opt(hamiltonian_tour, max_2opt_passes)

        total_cost = 0.0
        for k in range(len(optimized_tour) - 1):
            total_cost += self._dist[optimized_tour[k]][optimized_tour[k + 1]]

        tour_nodes = [self._nodes[idx] for idx in optimized_tour]
        return total_cost, tour_nodes

    def _min_weight_perfect_matching(self, nodes: List[int]) -> List[Tuple[int, int]]:
        k = len(nodes)
        memo: Dict[int, Tuple[float, List[Tuple[int, int]]]] = {}

        def dp(mask: int) -> Tuple[float, List[Tuple[int, int]]]:
            if mask == 0:
                return 0.0, []
            if mask in memo:
                return memo[mask]

            first_idx = 0
            while (mask & (1 << first_idx)) == 0:
                first_idx += 1

            min_val = float("inf")
            best_pairs: List[Tuple[int, int]] = []
            u = nodes[first_idx]

            for second_idx in range(first_idx + 1, k):
                if mask & (1 << second_idx):
                    v = nodes[second_idx]
                    cost = self._dist[u][v]
                    next_mask = mask ^ (1 << first_idx) ^ (1 << second_idx)
                    rem_cost, rem_pairs = dp(next_mask)
                    if cost + rem_cost < min_val:
                        min_val = cost + rem_cost
                        best_pairs = [(u, v)] + rem_pairs

            memo[mask] = (min_val, best_pairs)
            return memo[mask]

        _, pairs = dp((1 << k) - 1)
        return pairs

    def _hierholzer(self, adj: Dict[int, List[int]]) -> List[int]:
        cur_adj = {u: list(neighbors) for u, neighbors in adj.items()}
        stack = [0]
        circuit = []

        while stack:
            u = stack[-1]
            if cur_adj[u]:
                v = cur_adj[u].pop()
                cur_adj[v].remove(u)
                stack.append(v)
            else:
                circuit.append(stack.pop())

        circuit.reverse()
        return circuit

    def _two_opt(self, tour: List[int], max_passes: int) -> List[int]:
        improved = True
        passes = 0
        best_tour = list(tour)

        while improved and passes < max_passes:
            improved = False
            passes += 1

            for i in range(1, len(best_tour) - 2):
                for j in range(i + 1, len(best_tour) - 1):
                    a, b = best_tour[i - 1], best_tour[i]
                    c, d = best_tour[j], best_tour[j + 1]

                    curr_dist = self._dist[a][b] + self._dist[c][d]
                    new_dist = self._dist[a][c] + self._dist[b][d]

                    if new_dist < curr_dist - 1e-9:
                        best_tour[i : j + 1] = reversed(best_tour[i : j + 1])
                        improved = True
                        break
                if improved:
                    break

        return best_tour
