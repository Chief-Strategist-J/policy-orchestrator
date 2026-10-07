"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EQUIVARIANT GEOMETRIC GNN (E(N)-EQUIVARIANCE) (ALGO-GRAPH-GNN-266)
================================================================================

1. OVERVIEW & OBJECTIVE:
   E(n)-Equivariant Graph Neural Network (EGNN) Engine (Satorras et al.).
   Processes graphs embedded in continuous spatial geometry (molecules, sensor grids, point clouds)
   where scalar node features h_v are E(n)-invariant (invariant under 3D rotation and translation)
   and spatial node coordinates x_v are E(n)-equivariant (rotating input rotates output coordinates).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Layers * M * (d_feat + d_coord)) message passing.
   - Space Complexity: O(V * (d_feat + d_coord)) coordinate and invariant feature buffers.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Spatial graph connectivity.
   - `coordinates` (Dict[TNode, List[float]]): Physical coordinates x_v in R^D.
   - `features` (Optional[Dict[TNode, List[float]]]): Invariant node features h_v.

4. OUTPUT PARAMETERS:
   - `forward_layer()` (Tuple[Dict[TNode, List[float]], Dict[TNode, List[float]]]): (Updated features h_v, Updated coordinates x_v).

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Global rotations and translations of coordinates commute strictly with network updates.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEquivariantGeometricGnn(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-266
      name: GraphAlgoEquivariantGeometricGnn
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, egnn, equivariant, geometric_graphs, physical_coordinates, rotation_invariance]
      inputs:
        type: object
        required: [adjacency, coordinates]
        properties:
          adjacency: {type: object}
          coordinates: {type: object}
          features: {type: object}
      outputs:
        type: object
        properties:
          updated_features: {type: object}
          updated_coordinates: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(L * M * d)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        coordinates: Dict[TNode, List[float]],
        features: Optional[Dict[TNode, List[float]]] = None,
    ) -> None:
        """
        Initialize Equivariant Geometric GNN engine.

        Args:
            adjacency: Spatial graph adjacency map.
            coordinates: Node coordinate mapping in R^D.
            features: Optional invariant scalar features.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._coords: Dict[TNode, List[float]] = {u: list(coordinates.get(u, [0.0, 0.0, 0.0])) for u in self._nodes}
        self._coord_dim: int = len(next(iter(self._coords.values()))) if self._coords else 3

        if features is not None:
            self._features: Dict[TNode, List[float]] = {u: list(features.get(u, [1.0])) for u in self._nodes}
        else:
            self._features = {u: [1.0] for u in self._nodes}
        self._feat_dim: int = len(next(iter(self._features.values()))) if self._features else 1

    def forward_layer(self) -> Tuple[Dict[TNode, List[float]], Dict[TNode, List[float]]]:
        """
        Execute one layer of E(n)-equivariant message passing on coordinates and features.

        Returns:
            Tuple of (new_features, new_coordinates).
        """
        new_feats: Dict[TNode, List[float]] = {}
        new_coords: Dict[TNode, List[float]] = {}

        for u in self._nodes:
            nbrs = self._adj.get(u, [])
            deg = max(1, len(nbrs))
            coord_u = self._coords[u]
            feat_u = self._features[u]

            coord_shift = [0.0] * self._coord_dim
            msg_agg = [0.0] * self._feat_dim

            for v in nbrs:
                coord_v = self._coords[v]
                feat_v = self._features[v]

                dist_sq = sum((coord_u[d] - coord_v[d]) ** 2 for d in range(self._coord_dim))
                phi_x = 1.0 / (1.0 + dist_sq)

                for d in range(self._coord_dim):
                    coord_shift[d] += (coord_u[d] - coord_v[d]) * phi_x / deg

                for d in range(self._feat_dim):
                    msg_agg[d] += (feat_v[d] * phi_x) / deg

            new_coords[u] = [coord_u[d] + coord_shift[d] for d in range(self._coord_dim)]
            new_feats[u] = [feat_u[d] + msg_agg[d] for d in range(self._feat_dim)]

        return new_feats, new_coords
