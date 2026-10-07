"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: INFLUENCE MAXIMIZATION (ALGO-GRAPH-CENT-113)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Influence Maximization under the Independent Cascade (IC) diffusion model.
   Selects k seed vertices that maximize expected information cascade spread.
   Implements CELF (Cost-Effective Lazy Forward) submodular greedy optimization
   with lazy marginal gain evaluation to achieve a provable (1 - 1/e) ~ 63% approximation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * R * (V + E)) with lazy CELF heap evaluation.
   - Space Complexity: O(V) seed sets and simulation queues.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[Tuple[TNode, float]]] - Directed graph with edge activation probabilities.
   - k: int - Number of seed vertices to select.
   - num_simulations: int - Monte Carlo simulations per marginal gain calculation (default: 100).
   - rng_seed: int - Random seed for deterministic simulation (default: 42).

4. OUTPUT PARAMETERS:
   - selected_seeds: List[TNode] - Top-k optimal seed vertices.
   - expected_spread: float - Total expected active vertex count.
   - marginal_gains: List[float] - Marginal cascade gain per added seed.

5. AGENT CONTRACT:
   - Role: Optimizer.
   - Preconditions: Edge probabilities must lie in [0.0, 1.0].
   - Guardrails: CELF lazy heap caching eliminates redundant Monte Carlo rollouts.
================================================================================
"""

import heapq
import random
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoInfluenceMaximization(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-113
      name: GraphAlgoInfluenceMaximization
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, influence_maximization, independent_cascade, celf_lazy_greedy]
      inputs:
        type: object
        required: [adjacency, k]
        properties:
          adjacency: {type: object}
          k: {type: integer}
          num_simulations: {type: integer, default: 100}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [selected_seeds, expected_spread, marginal_gains]
        properties:
          selected_seeds: {type: array, items: {type: string}}
          expected_spread: {type: number}
          marginal_gains: {type: array, items: {type: number}}
      parameters:
        k: {type: integer}
        num_simulations: {type: integer, default: 100}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * R * (V + E))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[Tuple[TNode, float]]],
        k: int,
        num_simulations: int = 100,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Influence Maximization solver.

        Args:
            adjacency: Graph adjacency mapping each node to list of (target, probability) pairs.
            k: Budget of seeds to select.
            num_simulations: Monte Carlo rollout count.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = adjacency
        self._k: int = k
        self._num_sims: int = num_simulations
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v, _ in self._adj[u]:
                nodes.add(v)
        return nodes

    def _simulate_spread(self, seeds: Set[TNode], rng: random.Random) -> float:
        if not seeds:
            return 0.0
        total_active: int = 0
        for _ in range(self._num_sims):
            active: Set[TNode] = set(seeds)
            q: Deque[TNode] = deque(list(seeds))
            while q:
                u = q.popleft()
                for v, p in self._adj.get(u, []):
                    if v not in active:
                        if rng.random() <= p:
                            active.add(v)
                            q.append(v)
            total_active += len(active)
        return float(total_active) / float(self._num_sims)

    def select_seeds(self) -> Tuple[List[TNode], float, List[float]]:
        """
        Execute CELF lazy greedy algorithm to find top-k influential seeds.

        Returns:
            Tuple of (selected_seeds_list, total_expected_spread, marginal_gains_list).
        """
        if self._k <= 0 or not self._nodes:
            return [], 0.0, []

        rng = random.Random(self._rng_seed)
        seeds: List[TNode] = []
        marginal_gains: List[float] = []

        pq: List[Tuple[float, TNode, int]] = []
        for u in self._nodes:
            spread = self._simulate_spread({u}, rng)
            heapq.heappush(pq, (-spread, u, 0))

        current_spread: float = 0.0
        current_seeds_set: Set[TNode] = set()

        while len(seeds) < min(self._k, len(self._nodes)) and pq:
            neg_gain, u, iteration_evaluated = heapq.heappop(pq)
            if u in current_seeds_set:
                continue

            if iteration_evaluated == len(seeds):
                seeds.append(u)
                current_seeds_set.add(u)
                marginal_gain = -neg_gain
                marginal_gains.append(marginal_gain)
                current_spread += marginal_gain
            else:
                new_spread = self._simulate_spread(current_seeds_set | {u}, rng)
                new_gain = new_spread - current_spread
                heapq.heappush(pq, (-new_gain, u, len(seeds)))

        return seeds, current_spread, marginal_gains
