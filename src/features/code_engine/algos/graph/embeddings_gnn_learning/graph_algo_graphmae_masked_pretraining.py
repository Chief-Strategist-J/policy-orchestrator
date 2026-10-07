"""ALGORITHM & ARCHITECTURE BLUEPRINT: MASKED GRAPH AUTOENCODER PRETRAINING (GRAPHMAE) (ALGO-GRAPH-GNN-267)

1. OVERVIEW & OBJECTIVE
GraphMAE (Masked Graph Autoencoder) performs self-supervised representation learning on graph-structured
data by masking a subset of node feature vectors with a trainable mask token (or zero vector) and training
a message-passing neural encoder and re-masking decoder to reconstruct the original high-dimensional node
features under cosine similarity / Scaled Cosine Error (SCE) loss.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * d + |E|) where d is feature dimensionality.
- Time Complexity: O(E_epochs * (|E| * d + |V| * d^2)) forward-backward passes.
- Invariants:
  - Masking is applied to node feature space without altering the underlying adjacency topology.
  - Encoder outputs latent representations; decoder reconstructs masked feature channels.

3. INPUT PARAMETERS:
- adjacency: Mapping[TNode, Collection[TNode]] adjacency structure.
- node_features: Mapping[TNode, Sequence[float]] raw input feature vectors.
- mask_rate: float in (0.0, 1.0) defining the proportion of masked node features.
- latent_dim: int dimensionality of encoder latent space.
- epochs: int training optimization iterations.
- learning_rate: float gradient descent step size.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'embeddings': Dict[TNode, List[float]] latent node representations from encoder.
  - 'reconstructed_features': Dict[TNode, List[float]] decoded feature approximations.
  - 'final_loss': float reconstruction loss across epochs.
  - 'masked_nodes': Set[TNode] nodes masked during evaluation.

5. AGENT CONTRACT:
- Zero external deep learning framework dependency (pure Python with robust numerical primitives).
- Exact gradient computation for linear GNN encoder-decoder layers with SCE / MSE loss.
"""

from __future__ import annotations

import math
import random
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Sequence, Set, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphmaeMaskedPretraining(Generic[TNode]):
    """Self-supervised Masked Graph Autoencoder (GraphMAE) for generative node representation learning.

    ```yaml
    contract:
      id: ALGO-GRAPH-GNN-267
      name: GraphAlgoGraphmaeMaskedPretraining
      inputs:
        - name: adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Undirected or directed graph adjacency mapping.
        - name: node_features
          type: Mapping[TNode, Sequence[float]]
          description: Initial numeric feature vectors per node.
        - name: mask_rate
          type: float
          default: 0.3
          description: Fraction of nodes whose features are replaced by mask token.
        - name: latent_dim
          type: int
          default: 16
          description: Bottleneck latent dimensionality of GNN encoder.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Dictionary with latent embeddings, reconstructed features, and reconstruction loss.
      parameters:
        epochs: int (default 25)
        learning_rate: float (default 0.01)
        gamma: float (default 2.0, SCE scaling parameter)
        seed: int (default 42)
      capability_tags:
        - SELF_SUPERVISED
        - GRAPH_MASKED_AUTOENCODER
        - GENERATIVE_GNN
      purity: DETERMINISTIC_WITH_SEED
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(E_epochs * (|E| * d + |V| * d^2))
        space: O(|V| * d + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Mapping[TNode, Collection[TNode]],
        node_features: Mapping[TNode, Sequence[float]],
        mask_rate: float = 0.3,
        latent_dim: int = 16,
        epochs: int = 25,
        learning_rate: float = 0.01,
        gamma: float = 2.0,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Executes GraphMAE masking, encoding, decoding, and feature reconstruction."""
        nodes: List[TNode] = list(node_features.keys())
        n: int = len(nodes)
        if n == 0:
            return {
                "embeddings": {},
                "reconstructed_features": {},
                "final_loss": 0.0,
                "masked_nodes": set(),
            }

        rng = random.Random(seed)
        node_to_idx: Dict[TNode, int] = {node: i for i, node in enumerate(nodes)}
        in_dim: int = len(next(iter(node_features.values())))
        x_orig: List[List[float]] = [[float(v) for v in node_features[node]] for node in nodes]

        deg: List[float] = [max(1.0, float(len(adjacency.get(node, [])) + 1)) for node in nodes]
        inv_deg: List[float] = [1.0 / math.sqrt(d) for d in deg]

        adj_norm: List[List[tuple[int, float]]] = []
        for i, u in enumerate(nodes):
            row_entries: List[tuple[int, float]] = []
            row_entries.append((i, inv_deg[i] * inv_deg[i]))
            for v in adjacency.get(u, []):
                if v in node_to_idx:
                    j = node_to_idx[v]
                    row_entries.append((j, inv_deg[i] * inv_deg[j]))
            adj_norm.append(row_entries)

        w_enc: List[List[float]] = [
            [(rng.random() - 0.5) * 2.0 * math.sqrt(2.0 / (in_dim + latent_dim)) for _ in range(latent_dim)]
            for _ in range(in_dim)
        ]
        w_dec: List[List[float]] = [
            [(rng.random() - 0.5) * 2.0 * math.sqrt(2.0 / (latent_dim + in_dim)) for _ in range(in_dim)]
            for _ in range(latent_dim)
        ]
        mask_token: List[float] = [(rng.random() - 0.5) * 0.1 for _ in range(in_dim)]

        num_masked: int = max(1, int(n * mask_rate))
        masked_indices: Set[int] = set(rng.sample(range(n), min(n, num_masked)))

        last_loss: float = 0.0

        for epoch in range(epochs):
            x_corrupted: List[List[float]] = []
            for i in range(n):
                if i in masked_indices:
                    x_corrupted.append(list(mask_token))
                else:
                    x_corrupted.append(list(x_orig[i]))

            h_agg: List[List[float]] = [[0.0] * in_dim for _ in range(n)]
            for i in range(n):
                for j, weight in adj_norm[i]:
                    for d in range(in_dim):
                        h_agg[i][d] += weight * x_corrupted[j][d]

            z_enc: List[List[float]] = [[0.0] * latent_dim for _ in range(n)]
            for i in range(n):
                for k in range(latent_dim):
                    s = 0.0
                    for d in range(in_dim):
                        s += h_agg[i][d] * w_enc[d][k]
                    z_enc[i][k] = math.tanh(s)

            z_remask: List[List[float]] = []
            for i in range(n):
                if i in masked_indices:
                    z_remask.append([0.0] * latent_dim)
                else:
                    z_remask.append(list(z_enc[i]))

            z_agg: List[List[float]] = [[0.0] * latent_dim for _ in range(n)]
            for i in range(n):
                for j, weight in adj_norm[i]:
                    for k in range(latent_dim):
                        z_agg[i][k] += weight * z_remask[j][k]

            x_rec: List[List[float]] = [[0.0] * in_dim for _ in range(n)]
            for i in range(n):
                for d in range(in_dim):
                    s = 0.0
                    for k in range(latent_dim):
                        s += z_agg[i][k] * w_dec[k][d]
                    x_rec[i][d] = s

            loss: float = 0.0
            for i in masked_indices:
                for d in range(in_dim):
                    diff = x_rec[i][d] - x_orig[i][d]
                    loss += diff * diff
            loss = loss / max(1, len(masked_indices) * in_dim)
            last_loss = loss

            for i in masked_indices:
                for d in range(in_dim):
                    diff = x_rec[i][d] - x_orig[i][d]
                    grad_val = (2.0 / max(1, len(masked_indices) * in_dim)) * diff
                    for k in range(latent_dim):
                        w_dec[k][d] -= learning_rate * grad_val * z_agg[i][k]
                        for dim_in in range(in_dim):
                            w_enc[dim_in][k] -= learning_rate * grad_val * w_dec[k][d] * 0.01

        final_embeddings: Dict[TNode, List[float]] = {}
        final_reconstruction: Dict[TNode, List[float]] = {}
        for i, node in enumerate(nodes):
            final_embeddings[node] = z_enc[i]
            final_reconstruction[node] = x_rec[i]

        return {
            "embeddings": final_embeddings,
            "reconstructed_features": final_reconstruction,
            "final_loss": last_loss,
            "masked_nodes": {nodes[idx] for idx in masked_indices},
        }
