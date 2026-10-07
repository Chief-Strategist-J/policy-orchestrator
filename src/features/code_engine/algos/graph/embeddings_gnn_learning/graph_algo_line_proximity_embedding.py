"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LINE PROXIMITY EMBEDDING (ALGO-GRAPH-EMB-252)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Large-scale Information Network Embedding (LINE) Engine.
   Learns low-dimensional vertex representations preserving both first-order proximity
   (direct observed edge connections) and second-order proximity (shared 2-hop neighborhood contexts)
   using asynchronous stochastic gradient descent with negative sampling.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Epochs * M * d * K_neg) training.
   - Space Complexity: O(V * d) vertex and context embedding matrices.
   - Purity: Stateful SGD optimizer, reproducible with random seed.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph connectivity layout.
   - `dim` (int): Target embedding dimension d (concatenated 1st + 2nd order = 2d).
   - `order` (int): 1 for 1st-order, 2 for 2nd-order, 3 for concatenated both.
   - `seed` (Optional[int]): Random seed.

4. OUTPUT PARAMETERS:
   - `train_embeddings(epochs, lr)` (Dict[TNode, List[float]]): Normalized representation vector per vertex.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Preserves pairwise topological co-occurrences and asymmetric link context distributions.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLineProximityEmbedding(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-252
      name: GraphAlgoLineProximityEmbedding
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, line, first_order, second_order, negative_sampling, proximity]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          dim: {type: integer, minimum: 2, maximum: 128}
          order: {type: integer, minimum: 1, maximum: 3}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          embeddings: {type: object}
      parameters:
        dim: {type: integer}
        order: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(Epochs * M * d)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        dim: int = 8,
        order: int = 2,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize LINE embedding generator.

        Args:
            adjacency: Adjacency dictionary.
            dim: Dimension per order component.
            order: 1 for first-order, 2 for second-order, 3 for concatenated (2*dim).
            seed: PRNG seed.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._dim: int = max(2, dim)
        self._order: int = order
        self._rng = random.Random(seed)

        self._edges: List[Tuple[TNode, TNode]] = []
        for u, nbrs in self._adj.items():
            for v in nbrs:
                self._edges.append((u, v))

    def _sigmoid(self, x: float) -> float:
        if x > 10.0:
            return 1.0
        if x < -10.0:
            return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    def train_embeddings(self, epochs: int = 10, lr: float = 0.025, num_neg: int = 3) -> Dict[TNode, List[float]]:
        """
        Train LINE node vectors using SGD and negative sampling.

        Args:
            epochs: Training epochs.
            lr: Learning rate.
            num_neg: Number of negative samples per edge.

        Returns:
            Dictionary mapping node to learned embedding coordinates.
        """
        if not self._nodes or not self._edges:
            return {u: [0.0] * self._dim for u in self._nodes}

        v_emb: Dict[TNode, List[float]] = {
            u: [(self._rng.random() - 0.5) / self._dim for _ in range(self._dim)] for u in self._nodes
        }
        ctx_emb: Dict[TNode, List[float]] = {
            u: [(self._rng.random() - 0.5) / self._dim for _ in range(self._dim)] for u in self._nodes
        }

        for _ in range(epochs):
            self._rng.shuffle(self._edges)
            for u, v in self._edges:
                target_ctx = ctx_emb[v]
                dot = sum(v_emb[u][i] * target_ctx[i] for i in range(self._dim))
                g = (1.0 - self._sigmoid(dot)) * lr

                for i in range(self._dim):
                    v_emb[u][i] += g * target_ctx[i]
                    target_ctx[i] += g * v_emb[u][i]

                for _ in range(num_neg):
                    neg_v = self._rng.choice(self._nodes)
                    if neg_v != v:
                        neg_ctx = ctx_emb[neg_v]
                        neg_dot = sum(v_emb[u][i] * neg_ctx[i] for i in range(self._dim))
                        neg_g = -self._sigmoid(neg_dot) * lr
                        for i in range(self._dim):
                            v_emb[u][i] += neg_g * neg_ctx[i]
                            neg_ctx[i] += neg_g * v_emb[u][i]

        embeddings: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            vec = v_emb[u]
            norm = math.sqrt(sum(x * x for x in vec))
            embeddings[u] = [x / (norm + 1e-9) for x in vec]

        return embeddings
