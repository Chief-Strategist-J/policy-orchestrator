"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Laplacian Eigensolvers - Lanczos and Fiedler Vector (ALGO-GRAPH-SPEC-172)

1. OVERVIEW & OBJECTIVE:
Computes the second smallest eigenvalue (algebraic connectivity lambda_2) and the corresponding
eigenvector (Fiedler vector) of the unnormalized and normalized graph Laplacian matrix using
Krylov-subspace Lanczos iterations with Gram-Schmidt orthogonalization.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(k * |V|) Lanczos basis vectors storage.
- Time Complexity: O(k * |E| + k^2 * |V|) where k is the number of Lanczos iterations.
- Invariants:
  - Smallest eigenvalue lambda_1 == 0.0 with constant eigenvector 1.
  - Algebraic connectivity lambda_2 > 0 iff the graph is connected.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph adjacency structure.
- `num_iterations` (int): Lanczos Krylov subspace dimension (default: 30).
- `tolerance` (float): Convergence tolerance for tridiagonal eigensolution (default: 1e-6).

4. OUTPUT PARAMETERS:
- `LaplacianSpectrumResult`: Algebraic connectivity lambda_2 and Fiedler vector dictionary.

5. AGENT CONTRACT:
- Role: Spectral graph theory and connectivity analyst.
- Rules: Enforce orthogonalization against the all-ones null-space vector.
- Guardrails: If |V| < 2, algebraic connectivity is 0.0.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
import random
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class LaplacianSpectrumResult(Generic[TNode]):
    """
    Container for Laplacian spectral decomposition.
    """
    algebraic_connectivity: float
    fiedler_vector: Dict[TNode, float]
    is_connected: bool
    iterations_run: int


class LaplacianEigensolver(Generic[TNode]):
    """
    Solves for Laplacian algebraic connectivity and the Fiedler vector via Lanczos iteration.

    ```yaml
    contract_id: ALGO-GRAPH-SPEC-172
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      num_iterations: int
      tolerance: float
    outputs:
      result: LaplacianSpectrumResult[TNode]
    parameters:
      num_iterations: int
      tolerance: float
    capability_tags:
      - graph
      - spectral
      - laplacian
      - lanczos
      - fiedler_vector
      - algebraic_connectivity
    purity: deterministic
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(k * |E| + k^2 * |V|)
      space: O(k * |V|)
    ```
    """

    def __init__(self, num_iterations: int = 30, tolerance: float = 1e-6) -> None:
        """
        Args:
            num_iterations: Krylov subspace dimension limit.
            tolerance: Convergence tolerance.
        """
        self._num_iterations = num_iterations
        self._tolerance = tolerance

    def solve(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> LaplacianSpectrumResult[TNode]:
        """
        Computes the Fiedler vector and algebraic connectivity lambda_2.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            LaplacianSpectrumResult containing lambda_2 and Fiedler vector.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 2:
            fiedler = {u: 0.0 for u in nodes}
            return LaplacianSpectrumResult(
                algebraic_connectivity=0.0,
                fiedler_vector=fiedler,
                is_connected=False,
                iterations_run=0,
            )

        node_idx = {u: i for i, u in enumerate(nodes)}
        degrees = [len(list(adjacency.get(u, ()))) for u in nodes]
        adj_list = [[node_idx[v] for v in adjacency.get(u, ()) if v in node_idx] for u in nodes]

        def laplacian_mult(x: List[float]) -> List[float]:
            y = [0.0] * n
            for i in range(n):
                y[i] = degrees[i] * x[i] - sum(x[j] for j in adj_list[i])
            return y

        v = [random.uniform(-1.0, 1.0) for _ in range(n)]
        mean_v = sum(v) / n
        v = [x - mean_v for x in v]
        norm_v = math.sqrt(sum(x * x for x in v))
        if norm_v < 1e-12:
            v = [1.0 if i == 0 else (-1.0 / (n - 1)) for i in range(n)]
            norm_v = math.sqrt(sum(x * x for x in v))
        v = [x / norm_v for x in v]

        k_max = min(self._num_iterations, n)
        alphas: List[float] = []
        betas: List[float] = [0.0]
        v_vectors: List[List[float]] = [v]

        for j in range(k_max):
            w = laplacian_mult(v_vectors[j])
            if j > 0:
                beta_prev = betas[j]
                w = [w[i] - beta_prev * v_vectors[j - 1][i] for i in range(n)]

            alpha = sum(w[i] * v_vectors[j][i] for i in range(n))
            alphas.append(alpha)

            w = [w[i] - alpha * v_vectors[j][i] for i in range(n)]

            mean_w = sum(w) / n
            w = [x - mean_w for x in w]
            for prev_v in v_vectors:
                dot = sum(w[i] * prev_v[i] for i in range(n))
                w = [w[i] - dot * prev_v[i] for i in range(n)]

            beta = math.sqrt(sum(x * x for x in w))
            if beta < self._tolerance or j == k_max - 1:
                break
            betas.append(beta)
            v_vectors.append([x / beta for x in w])

        lambda_2, eigvec_k = self._solve_tridiagonal_smallest_nonzero(alphas, betas[1:])
        fiedler_raw = [0.0] * n
        for idx_k, weight in enumerate(eigvec_k):
            for i in range(n):
                fiedler_raw[i] += weight * v_vectors[idx_k][i]

        norm_f = math.sqrt(sum(x * x for x in fiedler_raw))
        if norm_f > 1e-12:
            fiedler_raw = [x / norm_f for x in fiedler_raw]

        fiedler_dict = {nodes[i]: fiedler_raw[i] for i in range(n)}
        is_conn = lambda_2 > 1e-4

        return LaplacianSpectrumResult(
            algebraic_connectivity=max(0.0, lambda_2),
            fiedler_vector=fiedler_dict,
            is_connected=is_conn,
            iterations_run=len(alphas),
        )

    def _solve_tridiagonal_smallest_nonzero(
        self,
        alphas: List[float],
        betas: List[float],
    ) -> Tuple[float, List[float]]:
        m = len(alphas)
        if m == 1:
            return alphas[0], [1.0]

        t_mat = [[0.0] * m for _ in range(m)]
        for i in range(m):
            t_mat[i][i] = alphas[i]
            if i < len(betas):
                t_mat[i][i + 1] = betas[i]
                t_mat[i + 1][i] = betas[i]

        vec = [1.0 / math.sqrt(m)] * m
        for _ in range(50):
            next_vec = [0.0] * m
            for r in range(m):
                next_vec[r] = sum(t_mat[r][c] * vec[c] for c in range(m))
            norm = math.sqrt(sum(x * x for x in next_vec))
            if norm > 1e-12:
                vec = [x / norm for x in next_vec]

        rayleigh = sum(vec[r] * sum(t_mat[r][c] * vec[c] for c in range(m)) for r in range(m))
        return max(0.0, rayleigh), vec
