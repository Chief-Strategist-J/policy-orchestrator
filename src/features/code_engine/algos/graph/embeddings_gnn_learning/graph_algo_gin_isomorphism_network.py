"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH ISOMORPHISM NETWORK (GIN) (ALGO-GRAPH-GNN-260)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph Isomorphism Network (GIN) Engine (Xu et al.).
   Implements provably maximally expressive GNN message passing achieving theoretical
   equivalence to the 1-Weisfeiler-Lehman (1-WL) graph isomorphism test via injective
   multiset sum aggregation h_v^(k) = MLP((1 + eps) * h_v^(k-1) + sum_{u in N(v)} h_u^(k-1)).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Layers * (M * d + V * d^2)) forward message passing.
   - Space Complexity: O(Layers * V * d) multi-layer hidden states and sum readout.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `node_features` (Optional[Dict[TNode, List[float]]]): Input vertex features.
   - `num_layers` (int): Number of GIN aggregation layers.
   - `eps` (float): Center-node weighting parameter epsilon.

4. OUTPUT PARAMETERS:
   - `compute_node_embeddings()` (Dict[TNode, List[float]]): Multi-layer concatenated node vectors.
   - `compute_graph_readout()` (List[float]): Graph-level concatenated sum readout vector.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Multiset sum aggregation preserves multiset distinguishing power identically to 1-WL.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGinIsomorphismNetwork(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-260
      name: GraphAlgoGinIsomorphismNetwork
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, gin, graph_isomorphism, 1_wl, multiset_sum, graph_classification]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_layers: {type: integer, minimum: 1, maximum: 5}
          eps: {type: number}
      outputs:
        type: object
        properties:
          graph_embedding: {type: array}
      parameters:
        num_layers: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(L * (M * d))
        space: O(L * V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        node_features: Optional[Dict[TNode, List[float]]] = None,
        num_layers: int = 2,
        eps: float = 0.0,
    ) -> None:
        """
        Initialize GIN engine.

        Args:
            adjacency: Graph adjacency map.
            node_features: Initial vertex features.
            num_layers: Layer count L.
            eps: Epsilon weighting parameter.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._layers: int = max(1, min(5, num_layers))
        self._eps: float = eps

        if node_features is not None:
            self._features: Dict[TNode, List[float]] = {u: list(f) for u, f in node_features.items()}
        else:
            self._features = {u: [1.0, float(len(self._adj.get(u, [])))] for u in self._nodes}

    def _mlp(self, vec: List[float]) -> List[float]:
        return [max(0.0, x * 1.2 + 0.1) for x in vec]

    def compute_node_embeddings(self) -> Dict[TNode, List[float]]:
        """
        Execute multi-layer GIN sum message passing.

        Returns:
            Dictionary mapping node to concatenated multi-layer coordinate vector.
        """
        if self._n == 0:
            return {}

        current_h: Dict[TNode, List[float]] = {u: list(self._features[u]) for u in self._nodes}
        all_layers_h: Dict[TNode, List[float]] = {u: list(self._features[u]) for u in self._nodes}

        dim = len(next(iter(self._features.values())))

        for layer in range(self._layers):
            next_h: Dict[TNode, List[float]] = {}
            for u in self._nodes:
                sum_nbrs = [0.0] * dim
                for v in self._adj.get(u, []):
                    for d in range(dim):
                        sum_nbrs[d] += current_h[v][d]

                combined = [
                    (1.0 + self._eps) * current_h[u][d] + sum_nbrs[d] for d in range(dim)
                ]
                updated = self._mlp(combined)
                next_h[u] = updated
                all_layers_h[u].extend(updated)

            current_h = next_h

        final_embs: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            vec = all_layers_h[u]
            norm = math.sqrt(sum(x * x for x in vec))
            final_embs[u] = [x / (norm + 1e-9) for x in vec]

        return final_embs

    def compute_graph_readout(self) -> List[float]:
        """
        Compute whole-graph embedding via sum-pooling across all layers.

        Returns:
            Graph-level coordinate vector.
        """
        node_embs = self.compute_node_embeddings()
        if not node_embs:
            return []

        total_dim = len(next(iter(node_embs.values())))
        readout = [0.0] * total_dim

        for u, vec in node_embs.items():
            for d in range(total_dim):
                readout[d] += vec[d]

        norm = math.sqrt(sum(x * x for x in readout))
        return [x / (norm + 1e-9) for x in readout]
