"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ROLX STRUCTURAL ROLE DISCOVERY (ALGO-GRAPH-ROLE-118)
================================================================================

1. OVERVIEW & OBJECTIVE:
   RolX (Role eXtraction) unsupervised structural role discovery engine.
   Extracts local structural features (degree, ego-network edge counts) and recursive
   aggregate neighborhood features (mean, sum), followed by non-negative matrix
   factorization (NMF) to discover structural roles independent of graph community location.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E) + V * num_roles * NMF_iters).
   - Space Complexity: O(V * num_features) feature matrix.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - num_roles: int - Number of structural roles to extract (default: 2).
   - num_recursions: int - Recursive feature aggregation hops (default: 1).

4. OUTPUT PARAMETERS:
   - node_role_distributions: Dict[TNode, List[float]] - Soft role membership distribution per node.
   - node_primary_role: Dict[TNode, int] - Dominant assigned role ID (0 to num_roles - 1).
   - node_feature_vectors: Dict[TNode, List[float]] - Extracted structural feature vector per node.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Non-empty graph.
   - Guardrails: Non-negative feature values ensure valid NMF decomposition.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoRolxStructuralRoles(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROLE-118
      name: GraphAlgoRolxStructuralRoles
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, structural_roles, rolx, nmf, recursive_features, role_discovery]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_roles: {type: integer, default: 2}
          num_recursions: {type: integer, default: 1}
      outputs:
        type: object
        required: [node_role_distributions, node_primary_role, node_feature_vectors]
        properties:
          node_role_distributions: {type: object}
          node_primary_role: {type: object}
          node_feature_vectors: {type: object}
      parameters:
        num_roles: {type: integer, default: 2}
        num_recursions: {type: integer, default: 1}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * F * R)
        space: O(V * F)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_roles: int = 2,
        num_recursions: int = 1,
    ) -> None:
        """
        Initialize the RolX structural role engine.

        Args:
            adjacency: Graph adjacency dictionary.
            num_roles: Number of target roles.
            num_recursions: Recursive neighborhood aggregation depth.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._num_roles: int = num_roles
        self._recursions: int = num_recursions
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def extract_roles(self) -> Tuple[Dict[TNode, List[float]], Dict[TNode, int], Dict[TNode, List[float]]]:
        """
        Extract structural features and compute soft role memberships.

        Returns:
            Tuple of (role_distributions_map, primary_role_map, raw_feature_vectors_map).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}, {}

        features: Dict[TNode, List[float]] = {}
        for u in self._nodes:
            nbrs = set(self._adj.get(u, []))
            deg = float(len(nbrs))
            ego_edges = 0.0
            for v in nbrs:
                ego_edges += float(len(set(self._adj.get(v, [])) & nbrs))
            ego_edges *= 0.5
            features[u] = [deg, ego_edges]

        for _ in range(self._recursions):
            next_features: Dict[TNode, List[float]] = {}
            for u in self._nodes:
                nbrs = self._adj.get(u, [])
                if not nbrs:
                    next_features[u] = features[u] + [0.0, 0.0]
                else:
                    sum_deg = sum(features[v][0] for v in nbrs)
                    mean_deg = sum_deg / float(len(nbrs))
                    next_features[u] = features[u] + [sum_deg, mean_deg]
            features = next_features

        num_feat = len(next(iter(features.values())))
        v_mat = [features[u] for u in self._nodes]

        k = min(self._num_roles, num_feat, n)
        w = [[(1.0 / float(k)) + 0.01 * (i % k) for _ in range(k)] for i in range(n)]
        h = [[(1.0 / float(num_feat)) + 0.01 * (j % num_feat) for j in range(num_feat)] for _ in range(k)]

        for _ in range(25):
            for i in range(n):
                for r in range(k):
                    num = sum(v_mat[i][j] * h[r][j] for j in range(num_feat))
                    denom = sum(sum(w[i][r2] * h[r2][j] for r2 in range(k)) * h[r][j] for j in range(num_feat)) + 1e-9
                    w[i][r] = w[i][r] * (num / denom)

            for r in range(k):
                for j in range(num_feat):
                    num = sum(w[i][r] * v_mat[i][j] for i in range(n))
                    denom = sum(w[i][r] * sum(w[i][r2] * h[r2][j] for r2 in range(k)) for i in range(n)) + 1e-9
                    h[r][j] = h[r][j] * (num / denom)

        role_dist: Dict[TNode, List[float]] = {}
        primary_role: Dict[TNode, int] = {}

        for i, u in enumerate(self._nodes):
            row = w[i]
            row_sum = sum(row)
            norm_row = [val / row_sum for val in row] if row_sum > 0 else row
            role_dist[u] = norm_row
            primary_role[u] = int(norm_row.index(max(norm_row)))

        return role_dist, primary_role, features
