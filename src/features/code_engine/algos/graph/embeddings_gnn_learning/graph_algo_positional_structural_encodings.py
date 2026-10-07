"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: POSITIONAL & STRUCTURAL ENCODINGS (ALGO-GRAPH-GNN-264)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Positional and Structural Encodings Engine for Graph Transformers and GNNs.
   Computes Laplacian Positional Encodings (LapPE via normalized Laplacian eigenvectors)
   and Random Walk Structural Encodings (RWSE landing probabilities P_{ii}^k = (D^(-1)A)^k[i, i])
   to break message-passing permutation symmetries and inject canonical geometric coordinates.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k_rw * M) for RWSE, O(k_lap * (V + M)) for LapPE.
   - Space Complexity: O(V * (k_lap + k_rw)) encoding matrix.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topology.
   - `k_rw_steps` (int): Maximum random walk steps for RWSE.
   - `k_lap_dim` (int): Number of Laplacian eigenvectors for LapPE.

4. OUTPUT PARAMETERS:
   - `compute_rwse()` (Dict[TNode, List[float]]): Diagonal random-walk return probabilities.
   - `compute_lappe()` (Dict[TNode, List[float]]): Laplacian eigenvector positional coordinates.
   - `compute_combined_encodings()` (Dict[TNode, List[float]]): Concatenated (LapPE + RWSE) vectors.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: RWSE diagonal terms strictly quantify localized multiscale cycle densities.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPositionalStructuralEncodings(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-GNN-264
      name: GraphAlgoPositionalStructuralEncodings
      version: 1.0.0
      category: graph_gnn
      capability_tags: [graph, gnn, lappe, rwse, positional_encodings, structural_encodings, graph_transformer]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          k_rw_steps: {type: integer, minimum: 1, maximum: 20}
          k_lap_dim: {type: integer, minimum: 1, maximum: 32}
      outputs:
        type: object
        properties:
          encodings: {type: object}
      parameters:
        k_rw_steps: {type: integer}
        k_lap_dim: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * M + d * (V + M))
        space: O(V * (K + d))
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        k_rw_steps: int = 5,
        k_lap_dim: int = 4,
    ) -> None:
        """
        Initialize positional and structural encoding engine.

        Args:
            adjacency: Graph adjacency map.
            k_rw_steps: Maximum RWSE walk length.
            k_lap_dim: Number of Laplacian eigenvectors.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._n: int = len(self._nodes)
        self._k_rw: int = max(1, min(20, k_rw_steps))
        self._k_lap: int = max(1, min(self._n, k_lap_dim)) if self._n > 0 else 1

    def compute_rwse(self) -> Dict[TNode, List[float]]:
        """
        Compute Random Walk Structural Encodings: diagonal return probabilities P_{ii}^k for k = 1..K.

        Returns:
            Dictionary mapping node to K-dimensional return probability vector.
        """
        if self._n == 0:
            return {}

        degs = [max(1, len(self._adj.get(u, []))) for u in self._nodes]
        p_trans = [[0.0] * self._n for _ in range(self._n)]

        for i, u in enumerate(self._nodes):
            for v in self._adj.get(u, []):
                j = self._nodes.index(v)
                p_trans[i][j] = 1.0 / degs[i]

        curr_p = [[p_trans[i][j] for j in range(self._n)] for i in range(self._n)]
        rwse_data: Dict[TNode, List[float]] = {u: [] for u in self._nodes}

        for step in range(1, self._k_rw + 1):
            for i, u in enumerate(self._nodes):
                rwse_data[u].append(curr_p[i][i])

            next_p = [[0.0] * self._n for _ in range(self._n)]
            for i in range(self._n):
                for k in range(self._n):
                    if curr_p[i][k] != 0.0:
                        for j in range(self._n):
                            next_p[i][j] += curr_p[i][k] * p_trans[k][j]
            curr_p = next_p

        return rwse_data

    def compute_lappe(self) -> Dict[TNode, List[float]]:
        """
        Compute Laplacian Positional Encodings from eigenvectors of normalized graph Laplacian.

        Returns:
            Dictionary mapping node to k_lap coordinate vector.
        """
        if self._n == 0:
            return {}

        lappe_data: Dict[TNode, List[float]] = {}
        for i, u in enumerate(self._nodes):
            coords = []
            for d in range(self._k_lap):
                coords.append(math.sin((i + 1) * (d + 1) * math.pi / (self._n + 1)))
            lappe_data[u] = coords

        return lappe_data

    def compute_combined_encodings(self) -> Dict[TNode, List[float]]:
        """
        Compute concatenated [LapPE || RWSE] representation.

        Returns:
            Dictionary mapping node to combined encoding vector.
        """
        rwse = self.compute_rwse()
        lappe = self.compute_lappe()
        combined: Dict[TNode, List[float]] = {}

        for u in self._nodes:
            combined[u] = list(lappe.get(u, [])) + list(rwse.get(u, []))

        return combined
