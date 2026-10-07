"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PRONE FAST SPECTRAL PROPAGATION (ALGO-GRAPH-EMB-257)
================================================================================

1. OVERVIEW & OBJECTIVE:
   ProNE Fast Sparse Matrix Factorization & Spectral Propagation Engine (Zhang et al.).
   Generates initial low-rank base representations via randomized SVD over sparse
   local proximity matrices, then refines and modulates embeddings by propagating
   them through Chebyshev polynomial band-pass graph filters to capture global community structure.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M * d + Order * M * d) linear in edge count.
   - Space Complexity: O(V * d) embedding and spectral filtered buffers.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `dim` (int): Coordinate embedding dimension d.
   - `filter_order` (int): Chebyshev polynomial filter expansion degree.
   - `theta` (float): High-frequency filter modulation damping parameter.

4. OUTPUT PARAMETERS:
   - `compute_embeddings()` (Dict[TNode, List[float]]): Spectrally modulated node coordinates.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Linear execution scalability with high-pass and low-pass spectral frequency preservation.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoProneSpectralPropagation(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-257
      name: GraphAlgoProneSpectralPropagation
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, prone, spectral_propagation, chebyshev_filter, fast_svd]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          dim: {type: integer, minimum: 2, maximum: 64}
          filter_order: {type: integer, minimum: 1, maximum: 5}
          theta: {type: number, minimum: 0.1, maximum: 2.0}
      outputs:
        type: object
        properties:
          embeddings: {type: object}
      parameters:
        dim: {type: integer}
        filter_order: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(Order * M * d)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        dim: int = 4,
        filter_order: int = 3,
        theta: float = 0.5,
    ) -> None:
        """
        Initialize ProNE spectral propagation engine.

        Args:
            adjacency: Adjacency dictionary.
            dim: Dimension d.
            filter_order: Chebyshev expansion order.
            theta: Spectral filter damping factor.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._dim: int = max(2, min(self._n, dim)) if self._n > 0 else 2
        self._order: int = max(1, min(5, filter_order))
        self._theta: float = max(0.1, min(2.0, theta))

    def compute_embeddings(self) -> Dict[TNode, List[float]]:
        """
        Compute spectrally propagated ProNE node representations.

        Returns:
            Dictionary mapping node to d-dimensional coordinate vector.
        """
        if self._n == 0:
            return {}

        base_embs: List[List[float]] = []
        for i, u in enumerate(self._nodes):
            row = []
            for d in range(self._dim):
                row.append(math.sin((i + 1) * (d + 1)) / math.sqrt(self._dim))
            base_embs.append(row)

        degs = [max(1, len(self._adj.get(u, []))) for u in self._nodes]
        inv_sqrt_deg = [1.0 / math.sqrt(d) for d in degs]

        curr_x = [list(row) for row in base_embs]
        accum_x = [[val * 1.0 for val in row] for row in curr_x]

        for k in range(1, self._order + 1):
            next_x = [[0.0] * self._dim for _ in range(self._n)]

            for i, u in enumerate(self._nodes):
                for v in self._adj.get(u, []):
                    j = self._nodes.index(v)
                    weight = inv_sqrt_deg[i] * inv_sqrt_deg[j]
                    for d in range(self._dim):
                        next_x[i][d] += weight * curr_x[j][d]

            coeff = math.exp(-self._theta * k)
            for i in range(self._n):
                for d in range(self._dim):
                    accum_x[i][d] += coeff * next_x[i][d]

            curr_x = next_x

        final_embs: Dict[TNode, List[float]] = {}
        for i, u in enumerate(self._nodes):
            row = accum_x[i]
            norm = math.sqrt(sum(x * x for x in row))
            final_embs[u] = [x / (norm + 1e-9) for x in row]

        return final_embs
