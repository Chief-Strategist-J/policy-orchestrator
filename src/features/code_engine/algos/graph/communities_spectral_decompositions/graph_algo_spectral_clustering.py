"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SPECTRAL GRAPH CLUSTERING (ALGO-GRAPH-COMM-158)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Spectral Graph Clustering using Normalized Symmetric Laplacian L_sym = I - D^(-1/2) A D^(-1/2)
   and Random Walk Laplacian L_rw. Computes the k smallest non-trivial eigenvectors via
   power iteration and deflation (Ng-Jordan-Weiss / Shi-Malik), row-normalizes spectral
   embeddings, and clusters via deterministic k-means.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * (V + E) * iter + V * k^2) spectral embedding and k-means.
   - Space Complexity: O(V * k) spectral embedding matrix.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Connected undirected graph adjacency.
   - k_clusters: int - Number of target spectral clusters k (default: 2).
   - max_iter: int - Maximum power iteration rounds per eigenvector (default: 50).
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - partition: Dict[TNode, int] - Node to cluster assignment map.
   - spectral_embeddings: Dict[TNode, List[float]] - k-dimensional spectral coordinates per node.
   - fiedler_vector: Dict[TNode, float] - Second smallest Laplacian eigenvector values.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected graph.
   - Guardrails: Eigenvectors are Gram-Schmidt orthogonalized against the trivial all-ones mode.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSpectralClustering(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-158
      name: GraphAlgoSpectralClustering
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, spectral_clustering, fiedler_vector, laplacian_eigenvectors, ng_jordan_weiss]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          k_clusters: {type: integer, default: 2}
          max_iter: {type: integer, default: 50}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [partition, spectral_embeddings, fiedler_vector]
        properties:
          partition: {type: object}
          spectral_embeddings: {type: object}
          fiedler_vector: {type: object}
      parameters:
        k_clusters: {type: integer, default: 2}
        max_iter: {type: integer, default: 50}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(k * (V + E) + V * k^2)
        space: O(V * k)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        k_clusters: int = 2,
        max_iter: int = 50,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Spectral Clustering engine.

        Args:
            adjacency: Graph adjacency dictionary.
            k_clusters: Target cluster count k.
            max_iter: Power iteration passes.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._k: int = max(1, k_clusters)
        self._max_iter: int = max_iter
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _gram_schmidt(self, vec: List[float], basis: List[List[float]]) -> List[float]:
        res = list(vec)
        for b in basis:
            dot = sum(res[i] * b[i] for i in range(len(res)))
            for i in range(len(res)):
                res[i] -= dot * b[i]
        norm = math.sqrt(sum(x * x for x in res))
        if norm > 1e-12:
            return [x / norm for x in res]
        return res

    def cluster(self) -> Tuple[Dict[TNode, int], Dict[TNode, List[float]], Dict[TNode, float]]:
        """
        Compute normalized Laplacian spectral embeddings and cluster vertices.

        Returns:
            Tuple of (partition_map, spectral_embeddings_dict, fiedler_vector_dict).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}, {}
        if n == 1:
            u = self._nodes[0]
            return {u: 0}, {u: [1.0]}, {u: 0.0}

        idx = {u: i for i, u in enumerate(self._nodes)}
        degrees = [len(self._adj.get(u, set())) for u in self._nodes]
        d_inv_sqrt = [1.0 / math.sqrt(max(1, d)) for d in degrees]

        t_vec = [math.sqrt(max(1, d)) for d in degrees]
        norm_t = math.sqrt(sum(x * x for x in t_vec))
        trivial_basis = [[x / norm_t for x in t_vec]]

        rng = random.Random(self._rng_seed)
        eigenvectors: List[List[float]] = []

        for _ in range(min(self._k, n - 1)):
            v = [rng.gauss(0.0, 1.0) for _ in range(n)]
            v = self._gram_schmidt(v, trivial_basis + eigenvectors)

            for _ in range(self._max_iter):
                next_v = [0.0] * n
                for i in range(n):
                    u = self._nodes[i]
                    for neighbor in self._adj.get(u, set()):
                        j = idx[neighbor]
                        next_v[i] += d_inv_sqrt[i] * v[j] * d_inv_sqrt[j]

                v = self._gram_schmidt(next_v, trivial_basis + eigenvectors)

            eigenvectors.append(v)

        if not eigenvectors:
            eigenvectors = trivial_basis

        fiedler_vec = {self._nodes[i]: eigenvectors[0][i] for i in range(n)}
        embeddings: Dict[TNode, List[float]] = {}
        for i, u in enumerate(self._nodes):
            row = [eigenvectors[dim][i] for dim in range(len(eigenvectors))]
            norm_r = math.sqrt(sum(x * x for x in row))
            embeddings[u] = [x / norm_r for x in row] if norm_r > 0 else row

        centers: List[List[float]] = []
        for cluster_id in range(min(self._k, n)):
            centers.append(list(embeddings[self._nodes[cluster_id]]))

        part: Dict[TNode, int] = {}
        for _ in range(10):
            part = {}
            clusters: Dict[int, List[List[float]]] = {c: [] for c in range(len(centers))}
            for u in self._nodes:
                emb = embeddings[u]
                best_c = min(
                    range(len(centers)),
                    key=lambda c: sum((emb[d] - centers[c][d]) ** 2 for d in range(len(emb))),
                )
                part[u] = best_c
                clusters[best_c].append(emb)

            for c in range(len(centers)):
                if clusters[c]:
                    dim = len(centers[c])
                    centers[c] = [sum(pt[d] for pt in clusters[c]) / float(len(clusters[c])) for d in range(dim)]

        return part, embeddings, fiedler_vec
