"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PERCOLATION & ROBUSTNESS (ALGO-GRAPH-MODEL-144)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Percolation and network robustness analysis under random failures vs targeted attacks.
   Implements Newman-Ziff style inverse component tracking with Union-Find to measure
   the giant component collapse curve S(f) as a function of node removal fraction f.
   Computes the Schneider Robustness Index R (area under the giant component curve).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * alpha(V) + E) near-linear component maintenance.
   - Space Complexity: O(V) disjoint set union structure.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - attack_strategy: str - Removal order: 'random', 'degree', or 'betweenness' (default: 'degree').
   - rng_seed: int - Random seed for random failure simulation (default: 42).

4. OUTPUT PARAMETERS:
   - robustness_r: float - Integrated area under the giant component curve in [0.0, 0.5].
   - percolation_threshold_fc: float - Critical fraction f_c at which giant component disintegrates.
   - giant_component_curve: List[float] - Normalized giant component size S(f) at each removal step.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected network.
   - Guardrails: Robustness index normalized by 1 / N.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPercolationRobustness(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-144
      name: GraphAlgoPercolationRobustness
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, percolation, robustness_index, targeted_attack, newman_ziff, resilience]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          attack_strategy: {type: string, default: degree}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [robustness_r, percolation_threshold_fc, giant_component_curve]
        properties:
          robustness_r: {type: number}
          percolation_threshold_fc: {type: number}
          giant_component_curve: {type: array, items: {type: number}}
      parameters:
        attack_strategy: {type: string, default: degree}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * alpha(V) + E)
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        attack_strategy: str = "degree",
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Percolation Robustness analyzer.

        Args:
            adjacency: Graph adjacency dictionary.
            attack_strategy: 'random' or 'degree'.
            rng_seed: Random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._strategy: str = attack_strategy.lower()
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_robustness(self) -> Tuple[float, float, List[float]]:
        """
        Simulate node removals and compute robustness index R and critical threshold.

        Returns:
            Tuple of (robustness_r, critical_threshold_fc, giant_component_curve).
        """
        n = len(self._nodes)
        if n == 0:
            return 0.0, 0.0, []
        if n == 1:
            return 0.5, 1.0, [1.0]

        rng = random.Random(self._rng_seed)
        if self._strategy == "random":
            removal_order = list(self._nodes)
            rng.shuffle(removal_order)
        else:
            degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
            removal_order = sorted(self._nodes, key=lambda u: (-degrees[u], str(u)))

        parent: Dict[TNode, TNode] = {}
        size: Dict[TNode, int] = {}

        def _find(i: TNode) -> TNode:
            path = []
            curr = i
            while parent[curr] != curr:
                path.append(curr)
                curr = parent[curr]
            for node in path:
                parent[node] = curr
            return curr

        def _union(i: TNode, j: TNode) -> int:
            root_i = _find(i)
            root_j = _find(j)
            if root_i != root_j:
                if size[root_i] < size[root_j]:
                    root_i, root_j = root_j, root_i
                parent[root_j] = root_i
                size[root_i] += size[root_j]
                return size[root_i]
            return size[root_i]

        active_nodes: Set[TNode] = set()
        max_size: int = 0
        curve_reverse: List[float] = []

        for u in reversed(removal_order):
            parent[u] = u
            size[u] = 1
            active_nodes.add(u)
            if 1 > max_size:
                max_size = 1

            for v in self._adj.get(u, set()):
                if v in active_nodes:
                    new_sz = _union(u, v)
                    if new_sz > max_size:
                        max_size = new_sz

            curve_reverse.append(float(max_size) / float(n))

        curve = list(reversed(curve_reverse))
        r_area: float = (sum(curve) / float(n)) if n > 0 else 0.0

        fc: float = 1.0
        for idx, s_val in enumerate(curve):
            if s_val < 0.1:
                fc = float(idx) / float(n)
                break

        return r_area, fc, curve
