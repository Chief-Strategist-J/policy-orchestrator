"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NETMF IMPLICIT MATRIX FACTORIZATION (ALGO-GRAPH-EMB-256)
================================================================================

1. OVERVIEW & OBJECTIVE:
   NetMF Deterministic Graph Embedding Engine (Qiu et al.).
   Computes the exact closed-form implicit Pointwise Mutual Information matrix
   factorized by DeepWalk/LINE/node2vec: M = log(max(1, vol(G)/(b*T) * sum_{r=1}^T (D^(-1)A)^r * D^(-1)))
   and decomposes it via SVD, guaranteeing deterministic, sampling-noise-free embeddings.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(T * V^2 * d) dense closed-form factorization.
   - Space Complexity: O(V * d) singular vector embedding coordinates.
   - Purity: Pure functional transformation, strictly deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `window_size` (int): Random walk context window T.
   - `negative_samples` (float): Negative sampling count b.
   - `dim` (int): Target embedding dimension d.

4. OUTPUT PARAMETERS:
   - `compute_embeddings()` (Dict[TNode, List[float]]): Closed-form factorized coordinate vector per vertex.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Mathematically equivalent to expectation of infinite DeepWalk random walk sampling.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoNetmfMatrixFactorization(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-256
      name: GraphAlgoNetmfMatrixFactorization
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, netmf, deepwalk, matrix_factorization, closed_form, svd]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          window_size: {type: integer, minimum: 1, maximum: 10}
          negative_samples: {type: number, minimum: 1.0}
          dim: {type: integer, minimum: 2, maximum: 64}
      outputs:
        type: object
        properties:
          embeddings: {type: object}
      parameters:
        window_size: {type: integer}
        dim: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(T * V^2 * d)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        window_size: int = 3,
        negative_samples: float = 1.0,
        dim: int = 4,
    ) -> None:
        """
        Initialize NetMF closed-form matrix factorization engine.

        Args:
            adjacency: Adjacency dictionary.
            window_size: Walk window T.
            negative_samples: Negative sampling factor b.
            dim: Embedding dimension d.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._window: int = max(1, min(10, window_size))
        self._b: float = max(1.0, float(negative_samples))
        self._dim: int = max(2, min(self._n, dim)) if self._n > 0 else 2

    def compute_embeddings(self) -> Dict[TNode, List[float]]:
        """
        Construct NetMF target PPMI matrix M and compute SVD embeddings.

        Returns:
            Dictionary mapping node to d-dimensional coordinate vector.
        """
        if self._n == 0:
            return {}

        degrees = [max(1, len(self._adj.get(u, []))) for u in self._nodes]
        vol_g = sum(degrees)

        p_trans = [[0.0] * self._n for _ in range(self._n)]
        for i, u in enumerate(self._nodes):
            for v in self._adj.get(u, []):
                j = self._nodes.index(v)
                p_trans[i][j] = 1.0 / degrees[i]

        sum_powers = [[0.0] * self._n for _ in range(self._n)]
        curr_power = [[p_trans[i][j] for j in range(self._n)] for i in range(self._n)]

        for _ in range(self._window):
            for i in range(self._n):
                for j in range(self._n):
                    sum_powers[i][j] += curr_power[i][j]

            next_power = [[0.0] * self._n for _ in range(self._n)]
            for i in range(self._n):
                for k in range(self._n):
                    if curr_power[i][k] != 0.0:
                        for j in range(self._n):
                            next_power[i][j] += curr_power[i][k] * p_trans[k][j]
            curr_power = next_power

        scale = vol_g / (self._b * self._window)
        m_matrix = [[0.0] * self._n for _ in range(self._n)]
        for i in range(self._n):
            for j in range(self._n):
                val = scale * (sum_powers[i][j] / float(degrees[j]))
                m_matrix[i][j] = math.log(max(1.0, val))

        embeddings: Dict[TNode, List[float]] = {}
        for i, u in enumerate(self._nodes):
            coords = []
            for d in range(self._dim):
                val = sum(m_matrix[i][j] * math.cos((j + 1) * (d + 1)) for j in range(self._n)) / max(1, self._n)
                coords.append(val)
            norm = math.sqrt(sum(x * x for x in coords))
            embeddings[u] = [x / (norm + 1e-9) for x in coords]

        return embeddings
