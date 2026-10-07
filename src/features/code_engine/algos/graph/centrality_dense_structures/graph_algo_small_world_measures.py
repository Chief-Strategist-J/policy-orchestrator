"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SMALL-WORLD COEFFICIENTS (ALGO-GRAPH-NET-139)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Small-world network coefficient analyzer (Humphries-Gurney sigma and Telesford omega).
   Evaluates whether a network possesses both high local clustering C and short average path L:
   sigma = (C / C_rand) / (L / L_rand) > 1.0;
   omega = (L_rand / L) - (C / C_lattice) in [-1.0, 1.0] (omega ~ 0 indicates true small-world).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * (V + E)) all-pairs shortest path and clustering benchmark.
   - Space Complexity: O(V + E) network model storage.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Connected undirected graph adjacency.
   - num_random_samples: int - Null model instances generated for C_rand and L_rand (default: 5).
   - rng_seed: int - Random seed for null graph generation (default: 42).

4. OUTPUT PARAMETERS:
   - sigma: float - Humphries-Gurney small-world coefficient (sigma > 1.0 is small-world).
   - omega: float - Telesford small-world index in [-1.0, 1.0].
   - clustering_c: float - Observed average clustering coefficient C.
   - path_length_l: float - Observed average shortest path length L.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected undirected graph.
   - Guardrails: Degree-preserving null models preserve identical vertex degree sequences.
================================================================================
"""

import random
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSmallWorldMeasures(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-139
      name: GraphAlgoSmallWorldMeasures
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, small_world, humphries_gurney, telesford_omega, clustering_path_ratio]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_random_samples: {type: integer, default: 5}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [sigma, omega, clustering_c, path_length_l]
        properties:
          sigma: {type: number}
          omega: {type: number}
          clustering_c: {type: number}
          path_length_l: {type: number}
      parameters:
        num_random_samples: {type: integer, default: 5}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(S * V * (V + E))
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_random_samples: int = 5,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Small-World analyzer.

        Args:
            adjacency: Graph adjacency dictionary.
            num_random_samples: Sample count for null random reference graphs.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._num_samples: int = num_random_samples
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _compute_c_and_l(self, adj: Dict[TNode, Set[TNode]]) -> Tuple[float, float]:
        n = len(self._nodes)
        if n <= 2:
            return 0.0, 1.0

        c_vals = []
        for u in self._nodes:
            nbrs = list(adj.get(u, set()))
            deg = len(nbrs)
            if deg < 2:
                c_vals.append(0.0)
            else:
                triangles = sum(1 for i in range(deg) for j in range(i + 1, deg) if nbrs[j] in adj.get(nbrs[i], set()))
                c_vals.append(2.0 * float(triangles) / float(deg * (deg - 1)))
        avg_c = sum(c_vals) / float(n)

        total_dist = 0
        pair_count = 0
        for u in self._nodes:
            dist: Dict[TNode, int] = {u: 0}
            q: Deque[TNode] = deque([u])
            while q:
                curr = q.popleft()
                d = dist[curr]
                for v in adj.get(curr, set()):
                    if v not in dist:
                        dist[v] = d + 1
                        q.append(v)
            for v, d in dist.items():
                if str(u) < str(v):
                    total_dist += d
                    pair_count += 1

        avg_l = float(total_dist) / float(pair_count) if pair_count > 0 else 1.0
        return avg_c, avg_l

    def compute_small_world(self) -> Tuple[float, float, float, float]:
        """
        Compute sigma and omega small-world indices against null random models.

        Returns:
            Tuple of (sigma, omega, clustering_c, path_length_l).
        """
        c_real, l_real = self._compute_c_and_l(self._adj)

        rng = random.Random(self._rng_seed)
        all_edges: List[Tuple[TNode, TNode]] = []
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    all_edges.append((u, v))

        null_c_list = []
        null_l_list = []

        for _ in range(self._num_samples):
            rewired = list(all_edges)
            for _ in range(2 * len(rewired)):
                if len(rewired) < 2:
                    break
                i1, i2 = rng.sample(range(len(rewired)), 2)
                u1, v1 = rewired[i1]
                u2, v2 = rewired[i2]
                if u1 != u2 and v1 != v2 and u1 != v2 and u2 != v1:
                    rewired[i1] = (u1, v2)
                    rewired[i2] = (u2, v1)

            n_adj: Dict[TNode, Set[TNode]] = {u: set() for u in self._nodes}
            for u, v in rewired:
                n_adj[u].add(v)
                n_adj[v].add(u)

            c_null, l_null = self._compute_c_and_l(n_adj)
            null_c_list.append(c_null)
            null_l_list.append(l_null)

        c_rand = sum(null_c_list) / float(len(null_c_list)) if null_c_list else c_real
        l_rand = sum(null_l_list) / float(len(null_l_list)) if null_l_list else l_real

        c_ratio = (c_real / c_rand) if c_rand > 1e-6 else 1.0
        l_ratio = (l_real / l_rand) if l_rand > 1e-6 else 1.0
        sigma = c_ratio / l_ratio if l_ratio > 0 else 1.0

        c_lattice = 0.75
        omega = (l_rand / l_real) - (c_real / c_lattice) if (l_real > 0 and c_lattice > 0) else 0.0

        return sigma, omega, c_real, l_real
