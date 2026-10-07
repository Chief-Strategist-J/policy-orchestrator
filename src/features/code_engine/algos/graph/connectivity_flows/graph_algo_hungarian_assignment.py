"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HUNGARIAN ASSIGNMENT (ALGO-GRAPH-MATCH-85)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hungarian algorithm (Kuhn-Munkres) for minimum-cost perfect bipartite matching.
   Maintains dual potentials u_i and v_j, repeatedly augmenting along zero-slack edges
   with potential adjustments to ensure optimal one-to-one assignment.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N^3) optimal potential dual adjustment.
   - Space Complexity: O(N^2) cost matrix and dual potentials.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Complementary slackness certificates exact optimality.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TLeft = TypeVar("TLeft", bound=Hashable)
TRight = TypeVar("TRight", bound=Hashable)


class GraphAlgoHungarianAssignment(Generic[TLeft, TRight]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MATCH-85
      name: GraphAlgoHungarianAssignment
      version: 1.0.0
      category: graph_matching
      capability_tags: [graph, assignment_problem, hungarian_algorithm, kuhn_munkres, min_cost_matching]
      inputs:
        type: object
        required: [left_nodes, right_nodes, cost_matrix]
        properties:
          left_nodes:
            type: array
            items: {type: string}
          right_nodes:
            type: array
            items: {type: string}
          cost_matrix:
            type: array
            items:
              type: array
              items: {type: number}
      outputs:
        type: object
        required: [total_cost, assignments]
        properties:
          total_cost: {type: number}
          assignments:
            type: object
            additionalProperties: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(N^3)
        space: O(N^2)
    ---
    """

    def __init__(
        self,
        left_nodes: List[TLeft],
        right_nodes: List[TRight],
        cost_matrix: List[List[float]],
    ) -> None:
        self._left: List[TLeft] = left_nodes
        self._right: List[TRight] = right_nodes
        self._cost: List[List[float]] = cost_matrix

    def compute_min_cost_assignment(self) -> Tuple[float, Dict[TLeft, TRight]]:
        n = max(len(self._left), len(self._right))
        if n == 0:
            return 0.0, {}

        matrix = [[0.0] * (n + 1) for _ in range(n + 1)]
        for i in range(len(self._left)):
            for j in range(len(self._right)):
                matrix[i + 1][j + 1] = self._cost[i][j]

        u = [0.0] * (n + 1)
        v = [0.0] * (n + 1)
        p = [0] * (n + 1)
        way = [0] * (n + 1)

        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [float("inf")] * (n + 1)
            used = [False] * (n + 1)

            while True:
                used[j0] = True
                i0 = p[j0]
                delta = float("inf")
                j1 = 0

                for j in range(1, n + 1):
                    if not used[j]:
                        cur = matrix[i0][j] - u[i0] - v[j]
                        if cur < minv[j]:
                            minv[j] = cur
                            way[j] = j0
                        if minv[j] < delta:
                            delta = minv[j]
                            j1 = j

                for j in range(0, n + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta

                j0 = j1
                if p[j0] == 0:
                    break

            while True:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1
                if j0 == 0:
                    break

        assignment: Dict[TLeft, TRight] = {}
        total_cost = -v[0]

        for j in range(1, n + 1):
            i = p[j]
            if 1 <= i <= len(self._left) and 1 <= j <= len(self._right):
                assignment[self._left[i - 1]] = self._right[j - 1]

        actual_cost = 0.0
        for l_node, r_node in assignment.items():
            l_idx = self._left.index(l_node)
            r_idx = self._right.index(r_node)
            actual_cost += self._cost[l_idx][r_idx]

        return actual_cost, assignment
