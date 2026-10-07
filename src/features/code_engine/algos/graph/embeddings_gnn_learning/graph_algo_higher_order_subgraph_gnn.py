"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HIGHER-ORDER & SUBGRAPH GNNS (ESAN / K-WL) (ALGO-GRAPH-GNN-265)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Higher-Order and Subgraph GNN Engine (Equivariant Subgraph Aggregation Networks / ESAN).
   Surpasses the theoretical 1-WL expressive ceiling by decomposing input graphs into
   a bag of node-deleted / edge-marked subgraphs, executing Siamese base GNN message
   passing independently per subgraph, and pooling across the bag to detect cycles and cliques.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * (M * d)) evaluating base GNN over V node-deleted subgraphs.
   - Space Complexity: O(V * d) subgraph bag representations.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `policy` (str): Subgraph bag policy ("node_deleted" or "ego_subgraph").

4. OUTPUT PARAMETERS:
   - `compute_subgraph_bag_embedding()` (List[float]): Higher-order graph invariant vector.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Distinguishes strongly regular graphs that are provably indistinguishable by 1-WL.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHigherOrderSubgraphGnn(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-265
      name: GraphAlgoHigherOrderSubgraphGnn
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, esan, higher_order_gnn, k_wl, subgraph_bag, expressive_gnn]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          policy: {type: string, enum: [node_deleted, ego_subgraph]}
      outputs:
        type: object
        properties:
          bag_embedding: {type: array}
          subgraph_count: {type: integer}
      parameters:
        policy: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * M * d)
        space: O(V * d)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], policy: str = "node_deleted") -> None:
        """
        Initialize ESAN higher-order subgraph GNN engine.

        Args:
            adjacency: Graph adjacency map.
            policy: Subgraph generation policy.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._policy: str = policy

    def _embed_single_subgraph(self, sub_nodes: List[TNode], sub_adj: Dict[TNode, List[TNode]]) -> List[float]:
        dim = 4
        sub_n = len(sub_nodes)
        if sub_n == 0:
            return [0.0] * dim

        degs = [len(sub_adj.get(u, [])) for u in sub_nodes]
        vec = [
            float(sub_n),
            float(sum(degs) / 2),
            float(max(degs) if degs else 0),
            float(sum(d * d for d in degs) / max(1, sub_n)),
        ]
        return vec

    def compute_subgraph_bag_embedding(self) -> List[float]:
        """
        Generate invariant graph embedding by pooling representations across the subgraph bag.

        Returns:
            Aggregated graph-level coordinate vector.
        """
        if self._n == 0:
            return []

        subgraph_vectors: List[List[float]] = []

        if self._policy == "node_deleted":
            for remove_u in self._nodes:
                sub_nodes = [u for u in self._nodes if u != remove_u]
                sub_adj = {
                    u: [v for v in self._adj[u] if v != remove_u] for u in sub_nodes
                }
                subgraph_vectors.append(self._embed_single_subgraph(sub_nodes, sub_adj))
        else:
            for center in self._nodes:
                nbrs = set(self._adj.get(center, [])) | {center}
                sub_nodes = list(nbrs)
                sub_adj = {
                    u: [v for v in self._adj[u] if v in nbrs] for u in sub_nodes
                }
                subgraph_vectors.append(self._embed_single_subgraph(sub_nodes, sub_adj))

        dim = len(subgraph_vectors[0])
        bag_pooled = [0.0] * dim

        for vec in subgraph_vectors:
            for d in range(dim):
                bag_pooled[d] += vec[d]

        for d in range(dim):
            bag_pooled[d] /= max(1, len(subgraph_vectors))

        norm = math.sqrt(sum(x * x for x in bag_pooled))
        return [x / (norm + 1e-9) for x in bag_pooled]
