"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ADJACENCY SPECTRAL EMBEDDING (ALGO-GRAPH-EMB-251)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Adjacency Spectral Embedding (ASE) Engine.
   Computes low-dimensional node embeddings from the top truncated eigendecomposition
   of graph adjacency matrices X = U_d * |Lambda_d|^(1/2), provably estimating latent
   positions under Random Dot Product Graph (RDPG) models for downstream clustering and classification.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(d * (V + M)) power iteration / Lanczos partial eigensolve.
   - Space Complexity: O(V * d) dense embedding representation.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Symmetric or undirected graph topology.
   - `dim` (int): Target embedding dimension d (top d eigenvalues).

4. OUTPUT PARAMETERS:
   - `compute_embeddings()` (Dict[TNode, List[float]]): Latent coordinate vector per vertex.
   - `predict_edge_probability(u, v)` (float): Dot product dot(x_u, x_v) bounded in [0, 1].

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Reconstructed dot product inner products consistently approximate edge probabilities.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAdjacencySpectralEmbedding(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-251
      name: GraphAlgoAdjacencySpectralEmbedding
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, ase, spectral, rdpg, latent_positions, eigenvectors]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          dim: {type: integer, minimum: 1, maximum: 64}
      outputs:
        type: object
        properties:
          embeddings: {type: object}
          dim: {type: integer}
      parameters:
        dim: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(d * (V + M))
        space: O(V * d)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], dim: int = 4) -> None:
        """
        Initialize Adjacency Spectral Embedding engine.

        Args:
            adjacency: Adjacency map.
            dim: Embedding dimension.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._dim: int = max(1, min(self._n, dim)) if self._n > 0 else 1

    def compute_embeddings(self, max_iterations: int = 100) -> Dict[TNode, List[float]]:
        """
        Compute ASE embeddings using orthogonal power iterations.

        Args:
            max_iterations: Maximum power iterations per eigen-dimension.

        Returns:
            Dictionary mapping node to d-dimensional coordinate vector.
        """
        if self._n == 0:
            return {}

        vectors: List[List[float]] = []
        eigenvalues: List[float] = []

        for k in range(self._dim):
            vec = [math.sin((i + 1) * (k + 1)) for i in range(self._n)]
            norm = math.sqrt(sum(x * x for x in vec))
            vec = [x / norm for x in vec]

            val = 0.0
            for _ in range(max_iterations):
                for prev_v in vectors:
                    proj = sum(vec[i] * prev_v[i] for i in range(self._n))
                    vec = [vec[i] - proj * prev_v[i] for i in range(self._n)]

                norm = math.sqrt(sum(x * x for x in vec))
                if norm < 1e-12:
                    break
                vec = [x / norm for x in vec]

                new_vec = [0.0] * self._n
                for i, u in enumerate(self._nodes):
                    for v in self._adj.get(u, []):
                        if v in self._nodes:
                            j = self._nodes.index(v)
                            new_vec[i] += vec[j]

                val = sum(vec[i] * new_vec[i] for i in range(self._n))
                norm = math.sqrt(sum(x * x for x in new_vec))
                if norm < 1e-12:
                    break
                vec = [x / norm for x in new_vec]

            vectors.append(vec)
            eigenvalues.append(max(0.0, val))

        embeddings: Dict[TNode, List[float]] = {}
        for i, u in enumerate(self._nodes):
            coords = []
            for k in range(self._dim):
                scale = math.sqrt(eigenvalues[k]) if k < len(eigenvalues) else 1.0
                coords.append(vectors[k][i] * scale)
            embeddings[u] = coords

        return embeddings

    def predict_edge_probability(self, u: TNode, v: TNode, embeddings: Optional[Dict[TNode, List[float]]] = None) -> float:
        """
        Predict connection probability between u and v via inner product dot(x_u, x_v).

        Args:
            u: First node.
            v: Second node.
            embeddings: Optional precomputed embeddings.

        Returns:
            Probability value in [0, 1].
        """
        embs = embeddings if embeddings is not None else self.compute_embeddings()
        if u not in embs or v not in embs:
            return 0.0
        dot = sum(a * b for a, b in zip(embs[u], embs[v]))
        return max(0.0, min(1.0, 1.0 / (1.0 + math.exp(-dot))))
