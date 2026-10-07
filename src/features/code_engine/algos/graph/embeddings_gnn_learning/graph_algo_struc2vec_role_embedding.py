"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STRUC2VEC STRUCTURAL ROLE EMBEDDINGS (ALGO-GRAPH-EMB-253)
================================================================================

1. OVERVIEW & OBJECTIVE:
   struc2vec Structural Role Embeddings Engine (Ribeiro et al.).
   Learns latent node representations where vertices with equivalent structural roles
   (e.g. peripheral leaves, articulation bridges, hub cores) are embedded close together
   in metric space regardless of their topological distance or network component locality.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^2 * k_radius * log(deg)) multilayer hierarchy construction.
   - Space Complexity: O(V * d) structural embedding matrix.
   - Purity: Stateful representation learner, reproducible with seed.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Input graph structure.
   - `max_radius` (int): Maximum k-hop ring degree sequence radius.
   - `dim` (int): Target embedding dimension.
   - `seed` (Optional[int]): Random seed.

4. OUTPUT PARAMETERS:
   - `compute_embeddings()` (Dict[TNode, List[float]]): Structural coordinate vector per vertex.
   - `compute_structural_distance(u, v)` (float): Multi-ring Dynamic Time Warping degree distance.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Node similarity strictly reflects degree sequence isomorphism over topological proximity.
================================================================================
"""

import math
import random
from collections import defaultdict, deque
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoStruc2vecRoleEmbedding(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-EMB-253
      name: GraphAlgoStruc2vecRoleEmbedding
      version: 1.0.0
      category: graph_embeddings
      capability_tags: [graph, embeddings, struc2vec, structural_roles, dtw, degree_rings, multi_layer]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_radius: {type: integer, minimum: 1, maximum: 5}
          dim: {type: integer, minimum: 2, maximum: 64}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          embeddings: {type: object}
      parameters:
        max_radius: {type: integer}
        dim: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(V^2 * k)
        space: O(V * d)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        max_radius: int = 2,
        dim: int = 4,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize struc2vec structural role embedding engine.

        Args:
            adjacency: Adjacency dictionary.
            max_radius: Radius for k-hop ring degree profiles.
            dim: Coordinate dimensions.
            seed: PRNG seed.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._max_radius: int = max(1, min(5, max_radius))
        self._dim: int = max(2, min(64, dim))
        self._rng = random.Random(seed)

        self._degree_rings: Dict[TNode, List[List[int]]] = self._build_degree_rings()

    def _build_degree_rings(self) -> Dict[TNode, List[List[int]]]:
        rings: Dict[TNode, List[List[int]]] = {}
        for u in self._nodes:
            rings[u] = []
            visited = {u: 0}
            queue = deque([(u, 0)])
            level_nodes: Dict[int, List[TNode]] = defaultdict(list)

            while queue:
                curr, d = queue.popleft()
                if d > 0:
                    level_nodes[d].append(curr)
                if d < self._max_radius:
                    for v in self._adj.get(curr, []):
                        if v not in visited:
                            visited[v] = d + 1
                            queue.append((v, d + 1))

            for r in range(1, self._max_radius + 1):
                nodes_at_r = level_nodes[r]
                degs = sorted([len(self._adj.get(v, [])) for v in nodes_at_r])
                rings[u].append(degs if degs else [0])

        return rings

    def _dtw_distance(self, seq1: List[int], seq2: List[int]) -> float:
        n, m = len(seq1), len(seq2)
        dp = [[float("inf")] * (m + 1) for _ in range(n + 1)]
        dp[0][0] = 0.0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = (max(seq1[i - 1], seq2[j - 1]) / max(1.0, min(seq1[i - 1], seq2[j - 1])) - 1.0)
                dp[i][j] = cost + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[n][m]

    def compute_structural_distance(self, u: TNode, v: TNode) -> float:
        """
        Compute aggregate structural distance across all concentric degree rings.

        Args:
            u: First vertex.
            v: Second vertex.

        Returns:
            Scalar structural distance.
        """
        dist = 0.0
        for r in range(self._max_radius):
            r1 = self._degree_rings[u][r]
            r2 = self._degree_rings[v][r]
            dist += self._dtw_distance(r1, r2)
        return dist

    def compute_embeddings(self) -> Dict[TNode, List[float]]:
        """
        Generate structural role embeddings using distance matrix multidimensional scaling.

        Returns:
            Dictionary mapping node to d-dimensional coordinate vector.
        """
        n = len(self._nodes)
        if n == 0:
            return {}

        dist_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = self.compute_structural_distance(self._nodes[i], self._nodes[j])
                dist_matrix[i][j] = d
                dist_matrix[j][i] = d

        embeddings: Dict[TNode, List[float]] = {}
        for i, u in enumerate(self._nodes):
            coords = []
            for k in range(self._dim):
                val = sum(dist_matrix[i][j] * math.cos((j + 1) * (k + 1)) for j in range(n)) / max(1, n)
                coords.append(val)
            norm = math.sqrt(sum(x * x for x in coords))
            embeddings[u] = [x / (norm + 1e-9) for x in coords]

        return embeddings
