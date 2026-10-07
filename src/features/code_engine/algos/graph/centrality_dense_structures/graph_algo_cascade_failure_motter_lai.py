"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MOTTER-LAI CASCADING FAILURE (ALGO-GRAPH-MODEL-145)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Motter-Lai load redistribution and cascading failure model for infrastructure networks.
   Initializes vertex load L(u) based on shortest-path betweenness or traffic demand,
   with capacity C(u) = (1 + alpha) * L_0(u). Simulates iterative failure propagation
   when failed components cause traffic rerouting that exceeds downstream capacities.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(rounds * V * (V + E)) per cascade propagation stage.
   - Space Complexity: O(V) load and capacity dictionaries.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - initial_failures: List[TNode] - Seed vertices experiencing initial failure/attack.
   - tolerance_alpha: float - Headroom capacity parameter alpha >= 0.0 (default: 0.2).

4. OUTPUT PARAMETERS:
   - total_failed_nodes: List[TNode] - Complete list of all failed vertices.
   - surviving_ratio: float - Ratio of active surviving vertices |V_surv| / |V|.
   - cascade_rounds: int - Number of cascading failure rounds until stabilization.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected undirected graph.
   - Guardrails: Load redistribution recalculated exclusively over surviving active components.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCascadeFailureMotterLai(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-145
      name: GraphAlgoCascadeFailureMotterLai
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, cascading_failure, motter_lai, load_redistribution, resilience]
      inputs:
        type: object
        required: [adjacency, initial_failures]
        properties:
          adjacency: {type: object}
          initial_failures: {type: array, items: {type: string}}
          tolerance_alpha: {type: number, default: 0.2}
      outputs:
        type: object
        required: [total_failed_nodes, surviving_ratio, cascade_rounds]
        properties:
          total_failed_nodes: {type: array, items: {type: string}}
          surviving_ratio: {type: number}
          cascade_rounds: {type: integer}
      parameters:
        tolerance_alpha: {type: number, default: 0.2}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(R * V * (V + E))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        initial_failures: List[TNode],
        tolerance_alpha: float = 0.2,
    ) -> None:
        """
        Initialize the Motter-Lai Cascading Failure simulator.

        Args:
            adjacency: Graph adjacency dictionary.
            initial_failures: List of initial trigger failures.
            tolerance_alpha: Capacity buffer parameter alpha >= 0.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._init_fails: Set[TNode] = set(initial_failures)
        self._alpha: float = tolerance_alpha
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _compute_loads(self, active_nodes: Set[TNode]) -> Dict[TNode, float]:
        loads: Dict[TNode, float] = {u: 0.0 for u in active_nodes}
        for s in active_nodes:
            stack: List[TNode] = []
            pred: Dict[TNode, List[TNode]] = {w: [] for w in active_nodes}
            sigma: Dict[TNode, float] = {w: 0.0 for w in active_nodes}
            sigma[s] = 1.0
            dist: Dict[TNode, int] = {w: -1 for w in active_nodes}
            dist[s] = 0

            q: Deque[TNode] = deque([s])
            while q:
                v = q.popleft()
                stack.append(v)
                d = dist[v]
                for w in self._adj.get(v, set()) & active_nodes:
                    if dist[w] < 0:
                        dist[w] = d + 1
                        q.append(w)
                    if dist[w] == d + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta: Dict[TNode, float] = {w: 0.0 for w in active_nodes}
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    if sigma[w] > 0:
                        delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    loads[w] += delta[w]

        for u in loads:
            loads[u] *= 0.5
        return loads

    def simulate_cascade(self) -> Tuple[List[TNode], float, int]:
        """
        Simulate iterative overload cascading failure rounds.

        Returns:
            Tuple of (total_failed_nodes_list, surviving_nodes_ratio, cascade_rounds_count).
        """
        n = len(self._nodes)
        if n == 0:
            return [], 1.0, 0

        initial_loads = self._compute_loads(set(self._nodes))
        capacities: Dict[TNode, float] = {u: (1.0 + self._alpha) * (initial_loads[u] + 1.0) for u in self._nodes}

        active: Set[TNode] = set(self._nodes) - self._init_fails
        failed: Set[TNode] = set(self._init_fails)
        rounds: int = 0

        while True:
            rounds += 1
            if not active:
                break

            current_loads = self._compute_loads(active)
            new_fails: Set[TNode] = set()

            for u in active:
                if current_loads.get(u, 0.0) > capacities[u]:
                    new_fails.add(u)

            if not new_fails:
                break

            for u in new_fails:
                active.remove(u)
                failed.add(u)

        surviving_ratio = float(len(active)) / float(n)
        return sorted(list(failed), key=lambda x: str(x)), surviving_ratio, rounds
