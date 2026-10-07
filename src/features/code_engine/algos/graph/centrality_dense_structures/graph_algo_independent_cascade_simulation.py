"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DIFFUSION IC & LT SIMULATION (ALGO-GRAPH-MODEL-147)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Monte Carlo diffusion spread simulator under Independent Cascade (IC) and
   Linear Threshold (LT) information propagation models.
   Simulates probabilistic cascade activations from seed sets across directed weighted edges,
   aggregating final cascade sizes, reach probability vectors, and step-by-step cascades.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(num_runs * (V + E)) Monte Carlo rollouts.
   - Space Complexity: O(V) activation arrays.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[Tuple[TNode, float]]] - Directed graph with edge activation weights.
   - seeds: List[TNode] - Initial activated seed nodes.
   - model: str - Diffusion model ('IC' for independent cascade, 'LT' for linear threshold).
   - num_runs: int - Monte Carlo simulation iterations (default: 100).
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - mean_spread: float - Average total number of activated vertices across runs.
   - activation_probabilities: Dict[TNode, float] - Empirical probability of activation per vertex.
   - spread_distribution: List[int] - Raw list of final cascade sizes across all simulation runs.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Edge probabilities and LT weights in [0.0, 1.0].
   - Guardrails: LT node thresholds drawn uniformly from (0, 1] per rollout.
================================================================================
"""

import random
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoIndependentCascadeSimulation(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-147
      name: GraphAlgoIndependentCascadeSimulation
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, diffusion_simulation, independent_cascade, linear_threshold, monte_carlo]
      inputs:
        type: object
        required: [adjacency, seeds]
        properties:
          adjacency: {type: object}
          seeds: {type: array, items: {type: string}}
          model: {type: string, default: IC}
          num_runs: {type: integer, default: 100}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [mean_spread, activation_probabilities, spread_distribution]
        properties:
          mean_spread: {type: number}
          activation_probabilities: {type: object}
          spread_distribution: {type: array, items: {type: integer}}
      parameters:
        model: {type: string, default: IC}
        num_runs: {type: integer, default: 100}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(N * (V + E))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[Tuple[TNode, float]]],
        seeds: List[TNode],
        model: str = "IC",
        num_runs: int = 100,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Diffusion Simulator.

        Args:
            adjacency: Graph adjacency mapping each node to (target, weight) tuples.
            seeds: Initial activated seed nodes.
            model: 'IC' or 'LT'.
            num_runs: Number of Monte Carlo runs.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = adjacency
        self._seeds: Set[TNode] = set(seeds)
        self._model: str = model.upper()
        self._runs: int = num_runs
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v, _ in self._adj[u]:
                nodes.add(v)
        return nodes

    def simulate(self) -> Tuple[float, Dict[TNode, float], List[int]]:
        """
        Run Monte Carlo simulations of the diffusion process.

        Returns:
            Tuple of (mean_spread_float, activation_probabilities_map, spread_distribution_list).
        """
        rng = random.Random(self._rng_seed)
        hit_counts: Dict[TNode, int] = {u: 0 for u in self._nodes}
        spreads: List[int] = []

        for _ in range(self._runs):
            active: Set[TNode] = set(self._seeds)

            if self._model == "IC":
                q: Deque[TNode] = deque(list(self._seeds))
                while q:
                    u = q.popleft()
                    for v, p in self._adj.get(u, []):
                        if v not in active:
                            if rng.random() <= p:
                                active.add(v)
                                q.append(v)

            elif self._model == "LT":
                thresholds: Dict[TNode, float] = {u: rng.random() for u in self._nodes}
                newly_active = set(self._seeds)
                while newly_active:
                    curr_active = set(newly_active)
                    newly_active = set()
                    for u in self._nodes:
                        if u not in active:
                            in_weight = 0.0
                            for in_v in self._nodes:
                                for out_w, w in self._adj.get(in_v, []):
                                    if out_w == u and in_v in active:
                                        in_weight += w
                            if in_weight >= thresholds[u] and thresholds[u] > 0:
                                active.add(u)
                                newly_active.add(u)

            spreads.append(len(active))
            for u in active:
                hit_counts[u] += 1

        mean_spread = sum(spreads) / float(self._runs) if self._runs > 0 else 0.0
        act_probs = {u: float(count) / float(self._runs) for u, count in hit_counts.items()}

        return mean_spread, act_probs, spreads
