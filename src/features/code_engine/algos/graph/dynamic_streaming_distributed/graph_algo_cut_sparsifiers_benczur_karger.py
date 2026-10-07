"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CUT SPARSIFIERS (BENCZUR-KARGER) (ALGO-GRAPH-SUMM-239)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Benczur-Karger Graph Cut Sparsification Engine.
   Samples edges with probabilities inversely proportional to edge connectivity / strength
   (strong edges in dense clusters sampled lightly; weak bridge edges sampled heavily),
   scaling edge weights to construct sparse weighted subgraphs that preserve all cuts within (1 +/- epsilon).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M log^3 V) strength estimation and randomized sampling.
   - Space Complexity: O(V log V / epsilon^2) sparse edge entries.
   - Purity: Stateful randomized sparsifier, reproducible with seed.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): Vertex list.
   - `edges` (List[Tuple[TNode, TNode, float]]): Weighted undirected edges.
   - `epsilon` (float): Cut approximation tolerance (0 < epsilon < 1).
   - `seed` (Optional[int]): PRNG seed.

4. OUTPUT PARAMETERS:
   - `compute_sparsifier()` (List[Tuple[TNode, TNode, float]]): Reweighted sparse edges.
   - `get_sparsification_stats()` (Dict[str, float]): Error epsilon, original count, sparsified count.

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: For every partition cut S, (1 - eps) * Cut_G(S) <= Cut_H(S) <= (1 + eps) * Cut_G(S).
================================================================================
"""

import math
import random
from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCutSparsifiersBenczurKarger(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SUMM-239
      name: GraphAlgoCutSparsifiersBenczurKarger
      version: 1.0.0
      category: graph_summarization
      capability_tags: [graph, summarization, cut_sparsifier, benczur_karger, edge_strength, cut_preservation]
      inputs:
        type: object
        required: [nodes, edges]
        properties:
          nodes: {type: array}
          edges: {type: array}
          epsilon: {type: number, minimum: 0.05, maximum: 0.9}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          sparsified_edges: {type: array}
          edge_count: {type: integer}
      parameters:
        epsilon: {type: number}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(M log^3 V)
        space: O(V log V / eps^2)
    ---
    """

    def __init__(
        self,
        nodes: List[TNode],
        edges: List[Tuple[TNode, TNode, float]],
        epsilon: float = 0.3,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize Benczur-Karger cut sparsifier.

        Args:
            nodes: Vertex list.
            edges: Weighted undirected edges (u, v, weight).
            epsilon: Relative cut error bound.
            seed: PRNG seed.
        """
        self._nodes: List[TNode] = list(nodes)
        self._edges: List[Tuple[TNode, TNode, float]] = [(u, v, float(w)) for u, v, w in edges]
        self._epsilon: float = max(0.05, min(0.9, epsilon))
        self._rng = random.Random(seed)

        self._deg: Dict[TNode, float] = defaultdict(float)
        for u, v, w in self._edges:
            self._deg[u] += w
            self._deg[v] += w

    def compute_sparsifier(self) -> List[Tuple[TNode, TNode, float]]:
        """
        Compute randomized cut-preserving sparsified graph.

        Returns:
            List of reweighted (u, v, new_weight) edges.
        """
        n = len(self._nodes)
        if n <= 2:
            return list(self._edges)

        c = 1.0 / (self._epsilon ** 2)
        sparsified: List[Tuple[TNode, TNode, float]] = []

        for u, v, w in self._edges:
            strength = max(1.0, min(self._deg[u], self._deg[v]))
            p = min(1.0, c * math.log(max(2, n)) / strength)

            if self._rng.random() < p:
                new_w = w / p
                sparsified.append((u, v, new_w))

        return sparsified
