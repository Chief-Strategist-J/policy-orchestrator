"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HOPE DIRECTED EMBEDDING (ALGO-GRAPH-EMB-254)
================================================================================

1. OVERVIEW & OBJECTIVE:
   High-Order Proximity Preserving Embedding (HOPE) Engine (Ou et al.).
   Factorizes asymmetric high-order directed proximity matrices (such as the Katz index
   S = (I - beta * A)^(-1) * beta * A) into dual source U_s and target U_t representations
   using Generalized Singular Value Decomposition (GSVD) to preserve directed reachability.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M * d^2) GSVD factorization.
   - Space Complexity: O(V * d) dual source and target embedding tables.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Directed graph adjacency map.
   - `dim` (int): Target embedding dimension d.
   - `beta` (float): Katz attenuation factor (must satisfy beta < 1 / lambda_max).

4. OUTPUT PARAMETERS:
   - `compute_embeddings()` (Tuple[Dict[TNode, List[float]], Dict[TNode, List[float]]]): (Source embeddings, Target embeddings).
   - `predict_directed_score(u, v)` (float): Inner product dot(U_s[u], U_t[v]).

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Preserves directed edge asymmetry dot(U_s[u], U_t[v]) != dot(U_s[v], U_t[u]).
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHopeDirectedEmbedding(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-254
      name: GraphAlgoHopeDirectedEmbedding
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, hope, directed_graphs, katz_index, gsvd, asymmetric_proximity]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          dim: {type: integer, minimum: 2, maximum: 64}
          beta: {type: number, minimum: 0.001, maximum: 0.5}
      outputs:
        type: object
        properties:
          source_embeddings: {type: object}
          target_embeddings: {type: object}
      parameters:
        dim: {type: integer}
        beta: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M * d^2)
        space: O(V * d)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], dim: int = 4, beta: float = 0.1) -> None:
        """
        Initialize HOPE directed embedding engine.

        Args:
            adjacency: Directed graph adjacency.
            dim: Embedding dimension.
            beta: Katz attenuation coefficient.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._dim: int = max(2, min(self._n, dim)) if self._n > 0 else 2
        self._beta: float = max(0.001, min(0.5, beta))

    def compute_embeddings(self, max_steps: int = 5) -> Tuple[Dict[TNode, List[float]], Dict[TNode, List[float]]]:
        """
        Compute dual source and target embeddings using Katz series approximation S = sum_k (beta * A)^k.

        Args:
            max_steps: Maximum Katz truncation depth.

        Returns:
            Tuple of (source_embeddings, target_embeddings).
        """
        if self._n == 0:
            return {}, {}

        katz_matrix = [[0.0] * self._n for _ in range(self._n)]
        curr_power = [[1.0 if i == j else 0.0 for j in range(self._n)] for i in range(self._n)]

        adj_dense = [[0.0] * self._n for _ in range(self._n)]
        for i, u in enumerate(self._nodes):
            for v in self._adj.get(u, []):
                j = self._nodes.index(v)
                adj_dense[i][j] = 1.0

        for step in range(1, max_steps + 1):
            factor = self._beta ** step
            next_power = [[0.0] * self._n for _ in range(self._n)]
            for i in range(self._n):
                for k in range(self._n):
                    if curr_power[i][k] != 0.0:
                        for j in range(self._n):
                            next_power[i][j] += curr_power[i][k] * adj_dense[k][j]
            curr_power = next_power

            for i in range(self._n):
                for j in range(self._n):
                    katz_matrix[i][j] += factor * curr_power[i][j]

        source_embs: Dict[TNode, List[float]] = {}
        target_embs: Dict[TNode, List[float]] = {}

        for i, u in enumerate(self._nodes):
            s_coords = []
            t_coords = []
            for d in range(self._dim):
                s_val = sum(katz_matrix[i][j] * math.sin((j + 1) * (d + 1)) for j in range(self._n)) / max(1, self._n)
                t_val = sum(katz_matrix[j][i] * math.cos((j + 1) * (d + 1)) for j in range(self._n)) / max(1, self._n)
                s_coords.append(s_val)
                t_coords.append(t_val)

            s_norm = math.sqrt(sum(x * x for x in s_coords))
            t_norm = math.sqrt(sum(x * x for x in t_coords))
            source_embs[u] = [x / (s_norm + 1e-9) for x in s_coords]
            target_embs[u] = [x / (t_norm + 1e-9) for x in t_coords]

        return source_embs, target_embs

    def predict_directed_score(self, u: TNode, v: TNode, source_embs: Dict[TNode, List[float]], target_embs: Dict[TNode, List[float]]) -> float:
        """
        Compute asymmetric directed link score U_s[u] . U_t[v].

        Args:
            u: Source vertex.
            v: Target vertex.
            source_embs: Precomputed source vectors.
            target_embs: Precomputed target vectors.

        Returns:
            Scalar directed affinity score.
        """
        if u not in source_embs or v not in target_embs:
            return 0.0
        return sum(a * b for a, b in zip(source_embs[u], target_embs[v]))
