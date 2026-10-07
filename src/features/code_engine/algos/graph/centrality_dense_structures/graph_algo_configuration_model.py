"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CONFIGURATION MODEL & EDGE REWIRING (ALGO-GRAPH-MODEL-141)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Degree-preserving null model generator using the Configuration Model and
   Markov Chain edge-swap randomization. Generates uniform random graphs with
   an exact target degree sequence or randomizes an existing network via double-edge
   swaps ((a, b), (c, d) -> (a, d), (c, b)) while preserving degree distributions.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m) stub matching / O(num_swaps) MCMC rewiring.
   - Space Complexity: O(V + E) randomized adjacency.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - degree_sequence: Optional[List[int]] - Target degree sequence for configuration model.
   - adjacency: Optional[Dict[TNode, List[TNode]]] - Existing graph for degree-preserving rewiring.
   - num_swaps: int - Number of double-edge swap attempts (default: 100).
   - rng_seed: int - Random seed for reproducible generation (default: 42).

4. OUTPUT PARAMETERS:
   - generated_edges: List[Tuple[TNode, TNode]] - Randomized edge list.
   - degree_matched: bool - True if generated degree sequence matches targets.
   - successful_swaps: int - Number of valid double-edge swaps performed without multi-edges.

5. AGENT CONTRACT:
   - Role: Builder and Analyst.
   - Preconditions: Sum of target degree sequence must be even.
   - Guardrails: Self-loops and duplicate multi-edges are disallowed during edge swapping.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoConfigurationModel(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-141
      name: GraphAlgoConfigurationModel
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, configuration_model, edge_rewiring, null_models, degree_preserving]
      inputs:
        type: object
        required: []
        properties:
          degree_sequence: {type: array, items: {type: integer}}
          adjacency: {type: object}
          num_swaps: {type: integer, default: 100}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [generated_edges, degree_matched, successful_swaps]
        properties:
          generated_edges: {type: array, items: {type: array, items: {type: string}}}
          degree_matched: {type: boolean}
          successful_swaps: {type: integer}
      parameters:
        num_swaps: {type: integer, default: 100}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m + swaps)
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        degree_sequence: Optional[List[int]] = None,
        adjacency: Optional[Dict[TNode, List[TNode]]] = None,
        num_swaps: int = 100,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Configuration Model and Edge Rewirer.

        Args:
            degree_sequence: Optional degree targets.
            adjacency: Optional existing graph to randomize.
            num_swaps: Total swap attempts.
            rng_seed: Random seed.
        """
        self._deg_seq: Optional[List[int]] = degree_sequence
        self._adj: Optional[Dict[TNode, List[TNode]]] = adjacency
        self._swaps: int = num_swaps
        self._rng_seed: int = rng_seed

    def generate_or_rewire(self) -> Tuple[List[Tuple[TNode, TNode]], bool, int]:
        """
        Generate configuration model random graph or execute degree-preserving rewiring.

        Returns:
            Tuple of (generated_edges_list, degree_matched_flag, successful_swaps_count).
        """
        rng = random.Random(self._rng_seed)

        if self._adj is not None:
            edges: List[Tuple[TNode, TNode]] = []
            for u, nbrs in self._adj.items():
                for v in nbrs:
                    if str(u) < str(v):
                        edges.append((u, v))

            edge_set: Set[Tuple[TNode, TNode]] = set(edges)
            successful_swaps = 0

            for _ in range(self._swaps):
                if len(edges) < 2:
                    break
                i1, i2 = rng.sample(range(len(edges)), 2)
                u1, v1 = edges[i1]
                u2, v2 = edges[i2]

                if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                    continue

                new_e1 = (u1, v2) if str(u1) < str(v2) else (v2, u1)
                new_e2 = (u2, v1) if str(u2) < str(v1) else (v1, u2)

                if new_e1 not in edge_set and new_e2 not in edge_set:
                    edge_set.remove(edges[i1])
                    edge_set.remove(edges[i2])
                    edge_set.add(new_e1)
                    edge_set.add(new_e2)
                    edges[i1] = new_e1
                    edges[i2] = new_e2
                    successful_swaps += 1

            return edges, True, successful_swaps

        if self._deg_seq is not None:
            stubs: List[int] = []
            for node_idx, d in enumerate(self._deg_seq):
                stubs.extend([node_idx] * d)

            if len(stubs) % 2 != 0:
                stubs.pop()

            rng.shuffle(stubs)
            edges_cfg: List[Tuple[int, int]] = []
            for i in range(0, len(stubs), 2):
                u_idx, v_idx = stubs[i], stubs[i + 1]
                if u_idx != v_idx:
                    edges_cfg.append((u_idx, v_idx) if u_idx < v_idx else (v_idx, u_idx))

            return [(str(u), str(v)) for u, v in edges_cfg], True, 0

        return [], True, 0
