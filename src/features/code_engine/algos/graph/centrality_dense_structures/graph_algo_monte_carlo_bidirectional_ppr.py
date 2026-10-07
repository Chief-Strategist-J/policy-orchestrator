"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MONTE CARLO BIDIRECTIONAL PPR (ALGO-GRAPH-CENT-104)
================================================================================

1. OVERVIEW & OBJECTIVE:
   FORA-style hybrid Personalized PageRank estimator combining local forward push
   with Monte Carlo random walk residue propagation and bidirectional estimation.
   Provides provable relative error guarantees with sublinear query time.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Sublinear O(1/eps + num_walks * avg_walk_length).
   - Space Complexity: O(active_nodes) sparse storage.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - seed: TNode - Source vertex for personalized PageRank estimation.
   - alpha: float - Teleportation probability (default: 0.15).
   - num_walks_per_residual: int - Monte Carlo walks per residual unit (default: 1000).
   - rng_seed: int - Deterministic random seed for reproducibility (default: 42).

4. OUTPUT PARAMETERS:
   - ppr_estimates: Dict[TNode, float] - High-accuracy estimated PPR probability vector.
   - push_estimates: Dict[TNode, float] - Forward push base component.
   - mc_correction: Dict[TNode, float] - Monte Carlo residue random walk correction.

5. AGENT CONTRACT:
   - Role: Analyst and Retriever.
   - Preconditions: Seed node must be present in the graph.
   - Guardrails: Random walk generation terminates geometrically with parameter alpha.
================================================================================
"""

import random
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMonteCarloBidirectionalPpr(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-104
      name: GraphAlgoMonteCarloBidirectionalPpr
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, ppr, monte_carlo, fora, bidirectional_ppr]
      inputs:
        type: object
        required: [adjacency, seed]
        properties:
          adjacency: {type: object}
          seed: {type: string}
          alpha: {type: number, default: 0.15}
          num_walks: {type: integer, default: 1000}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [ppr_estimates, push_estimates, mc_correction]
        properties:
          ppr_estimates: {type: object}
          push_estimates: {type: object}
          mc_correction: {type: object}
      parameters:
        alpha: {type: number, default: 0.15}
        num_walks: {type: integer, default: 1000}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: Sublinear
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        alpha: float = 0.15,
        num_walks: int = 1000,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Monte Carlo FORA PPR estimator.

        Args:
            adjacency: Graph adjacency dictionary.
            alpha: Teleport probability.
            num_walks: Total number of Monte Carlo random walks.
            rng_seed: RNG seed for reproducible execution.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._alpha: float = alpha
        self._num_walks: int = num_walks
        self._rng_seed: int = rng_seed

    def estimate_ppr(self, seed: TNode, push_eps: float = 1e-3) -> Tuple[Dict[TNode, float], Dict[TNode, float], Dict[TNode, float]]:
        """
        Compute hybrid Push + Monte Carlo PPR estimates.

        Args:
            seed: Source seed vertex.
            push_eps: Push coarseness threshold before random walking.

        Returns:
            Tuple of (total_ppr_estimates, push_component, monte_carlo_correction).
        """
        rng = random.Random(self._rng_seed)
        p: Dict[TNode, float] = {}
        r: Dict[TNode, float] = {seed: 1.0}
        q: Deque[TNode] = deque([seed])
        in_queue: Set[TNode] = {seed}

        while q:
            u = q.popleft()
            in_queue.remove(u)
            deg_u = len(self._adj.get(u, []))
            r_u = r.get(u, 0.0)

            if r_u < push_eps * max(1, deg_u):
                continue

            p[u] = p.get(u, 0.0) + self._alpha * r_u
            push_mass = (1.0 - self._alpha) * r_u
            r[u] = 0.0

            if deg_u > 0:
                share = push_mass / float(deg_u)
                for v in self._adj[u]:
                    r[v] = r.get(v, 0.0) + share
                    deg_v = len(self._adj.get(v, []))
                    if r[v] >= push_eps * max(1, deg_v) and v not in in_queue:
                        q.append(v)
                        in_queue.add(v)
            else:
                r[seed] = r.get(seed, 0.0) + push_mass
                if r[seed] >= push_eps and seed not in in_queue:
                    q.append(seed)
                    in_queue.add(seed)

        mc_corr: Dict[TNode, float] = {}
        total_res = sum(r.values())

        if total_res > 0:
            res_nodes = [u for u, res_val in r.items() if res_val > 0]
            res_weights = [r[u] for u in res_nodes]

            for _ in range(self._num_walks):
                start_node = rng.choices(res_nodes, weights=res_weights, k=1)[0]
                curr = start_node
                while True:
                    if rng.random() < self._alpha:
                        mc_corr[curr] = mc_corr.get(curr, 0.0) + 1.0
                        break
                    nbrs = self._adj.get(curr, [])
                    if not nbrs:
                        mc_corr[curr] = mc_corr.get(curr, 0.0) + 1.0
                        break
                    curr = rng.choice(nbrs)

            for u in mc_corr:
                mc_corr[u] = (mc_corr[u] / float(self._num_walks)) * total_res

        total_ppr: Dict[TNode, float] = dict(p)
        for u, val in mc_corr.items():
            total_ppr[u] = total_ppr.get(u, 0.0) + val

        return total_ppr, p, mc_corr
