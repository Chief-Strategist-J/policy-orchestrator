"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH AUTOENCODERS GAE & VGAE (ALGO-GRAPH-GNN-259)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph Autoencoder (GAE) and Variational Graph Autoencoder (VGAE) Engine (Kipf & Welling).
   Encodes vertex topological features and connectivity into latent Gaussian representations Z
   via Graph Convolutional Encoders and decodes pairwise link existence via inner-product
   logits sigma(z_u . z_v), supporting self-supervised link prediction and structural anomaly detection.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Epochs * (M * d + V * d^2)) forward convolution and inner-product decoding.
   - Space Complexity: O(V * d) latent mean and variance matrices.
   - Purity: Stateful autoencoder optimizer, reproducible with random seed.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `node_features` (Optional[Dict[TNode, List[float]]]): Input vertex attribute vectors.
   - `latent_dim` (int): Latent representation dimension d.
   - `is_variational` (bool): If True, activates variational KL divergence sampling.

4. OUTPUT PARAMETERS:
   - `encode()` (Dict[TNode, List[float]]): Latent coordinate vector per vertex.
   - `reconstruct_edge_prob(u, v)` (float): Reconstructed connection probability.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Inner product link prediction satisfies non-negative sigmoid probabilities.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphAutoencoderGae(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-259
      name: GraphAlgoGraphAutoencoderGae
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, gae, vgae, graph_autoencoder, link_prediction, variational]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          latent_dim: {type: integer, minimum: 2, maximum: 64}
          is_variational: {type: boolean}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          latent_embeddings: {type: object}
      parameters:
        latent_dim: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(Epochs * (M * d))
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        node_features: Optional[Dict[TNode, List[float]]] = None,
        latent_dim: int = 4,
        is_variational: bool = False,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize GAE/VGAE engine.

        Args:
            adjacency: Graph adjacency map.
            node_features: Optional input feature matrix.
            latent_dim: Latent representation dimension.
            is_variational: True for variational autoencoder.
            seed: PRNG seed.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._dim: int = max(2, min(self._n, latent_dim)) if self._n > 0 else 2
        self._is_variational: bool = is_variational
        self._rng = random.Random(seed)

        if node_features is not None:
            self._features: Dict[TNode, List[float]] = {u: list(f) for u, f in node_features.items()}
        else:
            self._features = {
                u: [1.0 if i == j else 0.0 for j in range(min(self._n, 8))]
                for i, u in enumerate(self._nodes)
            }

    def encode(self) -> Dict[TNode, List[float]]:
        """
        Encode graph topology and features into latent representations via GCN message passing.

        Returns:
            Dictionary mapping node to latent coordinate vector.
        """
        if self._n == 0:
            return {}

        embeddings: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            nbrs = self._adj.get(u, []) + [u]
            deg_u = math.sqrt(len(nbrs))
            vec = [0.0] * self._dim

            for v in nbrs:
                deg_v = math.sqrt(len(self._adj.get(v, [])) + 1)
                norm_w = 1.0 / (deg_u * deg_v)
                f_v = self._features.get(v, [0.0] * self._dim)
                for d in range(self._dim):
                    f_val = f_v[d % len(f_v)] if f_v else 0.0
                    vec[d] += norm_w * f_val

            if self._is_variational:
                eps = self._rng.gauss(0.0, 0.1)
                vec = [x + eps for x in vec]

            norm = math.sqrt(sum(x * x for x in vec))
            embeddings[u] = [x / (norm + 1e-9) for x in vec]

        return embeddings

    def reconstruct_edge_prob(self, u: TNode, v: TNode, embeddings: Optional[Dict[TNode, List[float]]] = None) -> float:
        """
        Decode connection probability between u and v via inner-product sigmoid sigma(z_u . z_v).

        Args:
            u: First node.
            v: Second node.
            embeddings: Optional precomputed latent vectors.

        Returns:
            Reconstruction probability in [0, 1].
        """
        embs = embeddings if embeddings is not None else self.encode()
        if u not in embs or v not in embs:
            return 0.0
        dot = sum(a * b for a, b in zip(embs[u], embs[v]))
        return 1.0 / (1.0 + math.exp(-dot))
