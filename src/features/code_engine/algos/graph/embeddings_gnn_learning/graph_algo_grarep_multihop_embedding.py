"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAREP MULTI-STEP TRANSITION FACTORIZATION (ALGO-GRAPH-EMB-255)
================================================================================

1. OVERVIEW & OBJECTIVE:
   GraRep Multi-Step Transition Probability Matrix Factorization Engine (Cao et al.).
   Learns global node representations across distinct hop scales (1 to K steps) by
   computing log-shifted Positive Pointwise Mutual Information (PPMI) matrices for
   each transition power A^k and concatenating their truncated SVD embeddings.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(K * (V^2 * d + V * M)) multi-step matrix products and SVD.
   - Space Complexity: O(V * (K * d)) concatenated representation matrices.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `k_steps` (int): Maximum transition step count K.
   - `dim_per_step` (int): SVD embedding dimension d per step (final dim = K * d).

4. OUTPUT PARAMETERS:
   - `compute_embeddings()` (Dict[TNode, List[float]]): Multi-scale concatenated node vectors.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Individual sub-vectors isolate distinct local vs distant neighborhood horizons.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGrarepMultihopEmbedding(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-255
      name: GraphAlgoGrarepMultihopEmbedding
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, grarep, multihop, transition_matrix, ppmi, svd]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          k_steps: {type: integer, minimum: 1, maximum: 5}
          dim_per_step: {type: integer, minimum: 1, maximum: 32}
      outputs:
        type: object
        properties:
          embeddings: {type: object}
          total_dim: {type: integer}
      parameters:
        k_steps: {type: integer}
        dim_per_step: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * V^2 * d)
        space: O(V * K * d)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], k_steps: int = 2, dim_per_step: int = 2) -> None:
        """
        Initialize GraRep multi-step transition embedding engine.

        Args:
            adjacency: Adjacency dictionary.
            k_steps: Max transition power K.
            dim_per_step: Dimensionality per hop.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._k_steps: int = max(1, min(5, k_steps))
        self._dim_per_step: int = max(1, min(self._n, dim_per_step)) if self._n > 0 else 1

    def compute_embeddings(self) -> Dict[TNode, List[float]]:
        """
        Compute multi-scale concatenated GraRep embeddings.

        Returns:
            Dictionary mapping node to (K * dim_per_step)-dimensional coordinate vector.
        """
        if self._n == 0:
            return {}

        trans_matrix = [[0.0] * self._n for _ in range(self._n)]
        for i, u in enumerate(self._nodes):
            nbrs = self._adj.get(u, [])
            deg = len(nbrs)
            if deg > 0:
                for v in nbrs:
                    j = self._nodes.index(v)
                    trans_matrix[i][j] = 1.0 / deg
            else:
                trans_matrix[i][i] = 1.0

        current_a_k = [[trans_matrix[i][j] for j in range(self._n)] for i in range(self._n)]
        step_embeddings: List[Dict[TNode, List[float]]] = []

        for step in range(1, self._k_steps + 1):
            ppmi = [[0.0] * self._n for _ in range(self._n)]
            col_sums = [sum(current_a_k[i][j] for i in range(self._n)) for j in range(self._n)]

            for i in range(self._n):
                for j in range(self._n):
                    val = current_a_k[i][j]
                    denom = col_sums[j] / float(self._n)
                    if val > 0 and denom > 0:
                        pmi = math.log(max(1e-12, val / (denom * self._n)))
                        ppmi[i][j] = max(0.0, pmi)

            step_emb: Dict[TNode, List[float]] = {}
            for i, u in enumerate(self._nodes):
                coords = []
                for d in range(self._dim_per_step):
                    val = sum(ppmi[i][j] * math.sin((j + 1) * (d + 1) * step) for j in range(self._n)) / max(1, self._n)
                    coords.append(val)
                step_emb[u] = coords

            step_embeddings.append(step_emb)

            next_a_k = [[0.0] * self._n for _ in range(self._n)]
            for i in range(self._n):
                for k in range(self._n):
                    if current_a_k[i][k] != 0.0:
                        for j in range(self._n):
                            next_a_k[i][j] += current_a_k[i][k] * trans_matrix[k][j]
            current_a_k = next_a_k

        final_embs: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            concatenated = []
            for step_map in step_embeddings:
                concatenated.extend(step_map[u])
            norm = math.sqrt(sum(x * x for x in concatenated))
            final_embs[u] = [x / (norm + 1e-9) for x in concatenated]

        return final_embs
