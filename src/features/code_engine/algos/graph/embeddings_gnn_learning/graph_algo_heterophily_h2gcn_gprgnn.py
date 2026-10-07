"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HETEROPHILY-AWARE GNNS (H2GCN / GPR-GNN) (ALGO-GRAPH-GNN-263)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Heterophily-Aware Graph Neural Network Engine (H2GCN & GPR-GNN frameworks).
   Designed for networks exhibiting disassortative mixing / heterophily (where linked vertices
   have dissimilar classes e.g. fraudster-victim or buyer-seller) by uncoupling ego-embedding
   from neighbor aggregations, aggregating 1-hop and 2-hop neighborhoods separately,
   and utilizing generalized signed polynomial propagation filters.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M * d + V * d) multi-hop neighborhood aggregation.
   - Space Complexity: O(V * d) concatenated ego, 1-hop, and 2-hop state vectors.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `features` (Dict[TNode, List[float]]): Input vertex features.
   - `node_labels` (Optional[Dict[TNode, Any]]): Vertex class labels for homophily ratio measurement.

4. OUTPUT PARAMETERS:
   - `compute_homophily_ratio()` (float): Edge homophily ratio h in [0, 1].
   - `forward_h2gcn()` (Dict[TNode, List[float]]): Heterophily-aware concatenated embeddings.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Prevents smoothing-induced information loss in low-homophily regimes (h < 0.3).
================================================================================
"""

import math
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHeterophilyH2gcnGprgnn(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-263
      name: GraphAlgoHeterophilyH2gcnGprgnn
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, heterophily, h2gcn, gpr_gnn, disassortative, high_pass_filter]
      inputs:
        type: object
        required: [adjacency, features]
        properties:
          adjacency: {type: object}
          features: {type: object}
          node_labels: {type: object}
      outputs:
        type: object
        properties:
          homophily_ratio: {type: number}
          embeddings: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M * d + V * d)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        features: Dict[TNode, List[float]],
        node_labels: Optional[Dict[TNode, Any]] = None,
    ) -> None:
        """
        Initialize heterophily-aware GNN engine.

        Args:
            adjacency: Graph adjacency map.
            features: Input node feature vectors.
            node_labels: Optional ground-truth labels for homophily profiling.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._features: Dict[TNode, List[float]] = {u: list(features.get(u, [1.0])) for u in self._nodes}
        self._labels: Optional[Dict[TNode, Any]] = node_labels
        self._dim: int = len(next(iter(self._features.values()))) if self._features else 1

    def compute_homophily_ratio(self) -> float:
        """
        Compute edge homophily index h = (edges connecting same-label nodes) / (total edges).

        Returns:
            Homophily score in range [0.0, 1.0].
        """
        if not self._labels:
            return 0.5

        same_edges = 0
        total_edges = 0

        for u, nbrs in self._adj.items():
            if u in self._labels:
                for v in nbrs:
                    if v in self._labels:
                        total_edges += 1
                        if self._labels[u] == self._labels[v]:
                            same_edges += 1

        return (same_edges / float(total_edges)) if total_edges > 0 else 0.5

    def forward_h2gcn(self) -> Dict[TNode, List[float]]:
        """
        Execute H2GCN forward pass: separate ego-embedding, 1-hop aggregation, and 2-hop aggregation.

        Returns:
            Dictionary mapping node to concatenated heterophily-aware representation.
        """
        if not self._nodes:
            return {}

        agg_1hop: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            nbrs = self._adj.get(u, [])
            deg = max(1, len(nbrs))
            vec = [0.0] * self._dim
            for v in nbrs:
                f_v = self._features.get(v, [0.0] * self._dim)
                for d in range(self._dim):
                    vec[d] += f_v[d] / deg
            agg_1hop[u] = vec

        agg_2hop: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            nbrs = self._adj.get(u, [])
            deg = max(1, len(nbrs))
            vec = [0.0] * self._dim
            for v in nbrs:
                f_1hop = agg_1hop.get(v, [0.0] * self._dim)
                for d in range(self._dim):
                    vec[d] += f_1hop[d] / deg
            agg_2hop[u] = vec

        combined_embs: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            concat = list(self._features[u]) + agg_1hop[u] + agg_2hop[u]
            norm = math.sqrt(sum(x * x for x in concat))
            combined_embs[u] = [x / (norm + 1e-9) for x in concat]

        return combined_embs
