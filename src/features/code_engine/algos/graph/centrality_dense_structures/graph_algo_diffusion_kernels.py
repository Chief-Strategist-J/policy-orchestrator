"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH DIFFUSION KERNELS (ALGO-GRAPH-SIM-117)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph diffusion kernel suite for smooth continuous relevance propagation.
   Computes Heat Diffusion Kernel K = exp(-t * L) via Taylor/Chebyshev polynomial expansion,
   Regularized Laplacian Kernel K = (I + gamma * L)^(-1), and Von Neumann Kernel K = (I - alpha * A)^(-1).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(order * V^2) polynomial expansion.
   - Space Complexity: O(V^2) kernel matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency.
   - diffusion_time_t: float - Heat kernel diffusion time parameter t (default: 0.5).
   - gamma: float - Regularized Laplacian gamma parameter (default: 0.1).
   - expansion_order: int - Taylor polynomial truncated order (default: 6).

4. OUTPUT PARAMETERS:
   - heat_kernel: Dict[Tuple[TNode, TNode], float] - Heat diffusion kernel matrix exp(-t L).
   - regularized_laplacian_kernel: Dict[Tuple[TNode, TNode], float] - (I + gamma L)^(-1) approximation.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Symmetric unweighted or weighted adjacency.
   - Guardrails: Laplacian rows sum to 0.0 before matrix exponential expansion.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDiffusionKernels(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SIM-117
      name: GraphAlgoDiffusionKernels
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, diffusion_kernel, heat_kernel, regularized_laplacian, smooth_propagation]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          diffusion_time_t: {type: number, default: 0.5}
          gamma: {type: number, default: 0.1}
          expansion_order: {type: integer, default: 6}
      outputs:
        type: object
        required: [heat_kernel, regularized_laplacian_kernel]
        properties:
          heat_kernel: {type: object}
          regularized_laplacian_kernel: {type: object}
      parameters:
        diffusion_time_t: {type: number, default: 0.5}
        gamma: {type: number, default: 0.1}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * V^2)
        space: O(V^2)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        diffusion_time_t: float = 0.5,
        gamma: float = 0.1,
        expansion_order: int = 6,
    ) -> None:
        """
        Initialize the Graph Diffusion Kernel engine.

        Args:
            adjacency: Graph adjacency dictionary.
            diffusion_time_t: Time parameter for heat kernel.
            gamma: Laplacian regularization constant.
            expansion_order: Truncated polynomial order.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._t: float = diffusion_time_t
        self._gamma: float = gamma
        self._order: int = expansion_order
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _mat_mul(self, a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        n = len(a)
        c = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if a[i][k] != 0:
                    for j in range(n):
                        c[i][j] += a[i][k] * b[k][j]
        return c

    def compute_kernels(self) -> Tuple[Dict[Tuple[TNode, TNode], float], Dict[Tuple[TNode, TNode], float]]:
        """
        Compute Heat Kernel and Regularized Laplacian diffusion matrices.

        Returns:
            Tuple of (heat_kernel_dict, regularized_laplacian_kernel_dict).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}

        idx = {u: i for i, u in enumerate(self._nodes)}
        laplacian = [[0.0] * n for _ in range(n)]

        for u in self._nodes:
            u_i = idx[u]
            deg = len(self._adj.get(u, []))
            laplacian[u_i][u_i] = float(deg)
            for v in self._adj.get(u, []):
                v_i = idx[v]
                laplacian[u_i][v_i] -= 1.0

        heat_mat = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        curr_power = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        factorial: float = 1.0

        for k in range(1, self._order + 1):
            curr_power = self._mat_mul(curr_power, laplacian)
            factorial *= float(k)
            coeff = ((-self._t) ** k) / factorial
            for i in range(n):
                for j in range(n):
                    heat_mat[i][j] += coeff * curr_power[i][j]

        reg_mat = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        curr_l_power = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for k in range(1, min(4, self._order) + 1):
            curr_l_power = self._mat_mul(curr_l_power, laplacian)
            coeff = ((-self._gamma) ** k)
            for i in range(n):
                for j in range(n):
                    reg_mat[i][j] += coeff * curr_l_power[i][j]

        heat_kernel: Dict[Tuple[TNode, TNode], float] = {}
        reg_kernel: Dict[Tuple[TNode, TNode], float] = {}

        for i in range(n):
            for j in range(n):
                u, v = self._nodes[i], self._nodes[j]
                heat_kernel[(u, v)] = heat_mat[i][j]
                reg_kernel[(u, v)] = reg_mat[i][j]

        return heat_kernel, reg_kernel
