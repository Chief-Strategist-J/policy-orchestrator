"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: APPROXIMATE & STREAMING TRIANGLES (ALGO-GRAPH-DENSE-122)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Approximate and streaming triangle counting suite incorporating DOULION edge sampling
   and Wedge (2-path) random sampling. Estimates global triangle counts and clustering
   coefficients in sublinear memory and time with provable variance bounds.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(p * E + wedge_samples) sublinear processing.
   - Space Complexity: O(p * E) sparsified graph storage.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - doulion_p: float - Edge sampling retention probability p in (0, 1] (default: 0.5).
   - num_wedge_samples: int - Wedge 2-path sample count (default: 1000).
   - rng_seed: int - Random seed for reproducible sampling (default: 42).

4. OUTPUT PARAMETERS:
   - doulion_estimate: float - Triangle count estimated via DOULION (exact_sampled / p^3).
   - wedge_estimate: float - Triangle count estimated via wedge closure (total_wedges * closure_fraction / 3).
   - global_clustering_estimate: float - Estimated transitivity ratio (3 * triangles / wedges).

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph with at least one 2-path wedge.
   - Guardrails: p^3 scaling factor corrects for edge-triple joint Bernoulli probability.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoApproxTriangleCounting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-122
      name: GraphAlgoApproxTriangleCounting
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, triangles, doulion, wedge_sampling, approximate_counting]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          doulion_p: {type: number, default: 0.5}
          num_wedge_samples: {type: integer, default: 1000}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [doulion_estimate, wedge_estimate, global_clustering_estimate]
        properties:
          doulion_estimate: {type: number}
          wedge_estimate: {type: number}
          global_clustering_estimate: {type: number}
      parameters:
        doulion_p: {type: number, default: 0.5}
        num_wedge_samples: {type: integer, default: 1000}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(p * E + W)
        space: O(p * E)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        doulion_p: float = 0.5,
        num_wedge_samples: int = 1000,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Approximate Triangle counter.

        Args:
            adjacency: Graph adjacency dictionary.
            doulion_p: DOULION edge keep probability.
            num_wedge_samples: Wedge sampling count.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._p: float = max(0.01, min(1.0, doulion_p))
        self._num_wedges: int = num_wedge_samples
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def estimate_triangles(self) -> Tuple[float, float, float]:
        """
        Execute DOULION and Wedge Sampling to estimate triangle counts and clustering.

        Returns:
            Tuple of (doulion_estimate, wedge_estimate, global_clustering_estimate).
        """
        rng = random.Random(self._rng_seed)
        edges: Set[Tuple[TNode, TNode]] = set()
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    edges.add((u, v))

        sampled_adj: Dict[TNode, Set[TNode]] = {u: set() for u in self._nodes}
        for u, v in edges:
            if rng.random() <= self._p:
                sampled_adj[u].add(v)
                sampled_adj[v].add(u)

        sampled_triangles: int = 0
        for u in self._nodes:
            nbrs = sorted(list(sampled_adj.get(u, set())), key=lambda x: str(x))
            for i in range(len(nbrs)):
                v = nbrs[i]
                if str(u) < str(v):
                    for j in range(i + 1, len(nbrs)):
                        w = nbrs[j]
                        if w in sampled_adj.get(v, set()):
                            sampled_triangles += 1

        doulion_est = float(sampled_triangles) / (self._p ** 3)

        wedges_per_node: Dict[TNode, int] = {}
        total_wedges: int = 0
        for u in self._nodes:
            deg = len(self._adj.get(u, set()))
            w_u = (deg * (deg - 1)) // 2
            wedges_per_node[u] = w_u
            total_wedges += w_u

        if total_wedges == 0:
            return doulion_est, 0.0, 0.0

        closed_wedges: int = 0
        actual_samples = min(self._num_wedges, total_wedges)
        node_choices = [u for u, count in wedges_per_node.items() if count > 0]
        node_weights = [wedges_per_node[u] for u in node_choices]

        for _ in range(actual_samples):
            center = rng.choices(node_choices, weights=node_weights, k=1)[0]
            nbrs = list(self._adj.get(center, set()))
            v, w = rng.sample(nbrs, 2)
            if w in self._adj.get(v, set()):
                closed_wedges += 1

        closure_fraction = float(closed_wedges) / float(actual_samples)
        wedge_triangles = (float(total_wedges) * closure_fraction) / 3.0
        global_clustering = closure_fraction

        return doulion_est, wedge_triangles, global_clustering
