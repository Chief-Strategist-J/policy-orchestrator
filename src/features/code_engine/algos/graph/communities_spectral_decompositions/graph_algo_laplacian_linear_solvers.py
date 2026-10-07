"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Laplacian Linear System Solvers - Preconditioned Conjugate Gradient (ALGO-GRAPH-SPEC-174)

1. OVERVIEW & OBJECTIVE:
Solves symmetric positive semidefinite graph Laplacian linear systems L x = b (subject to b^T 1 = 0)
using Jacobi-preconditioned Conjugate Gradient (PCG) iterations, powering electrical network
flows, effective resistance queries, harmonic label propagation, and GSP graph filtering.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) residual and search direction vectors.
- Time Complexity: O(iterations * |E|) sparse matrix-vector multiplications.
- Invariants:
  - b must be orthogonal to the null space (sum(b) == 0 for connected graphs).
  - Residual ||L x - b||_2 <= tolerance * ||b||_2 upon convergence.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Graph adjacency structure.
- `rhs` (Mapping[TNode, float]): Right-hand-side load vector b.
- `max_iterations` (int): Maximum CG iterations (default: 100).
- `tolerance` (float): Relative residual convergence tolerance (default: 1e-6).

4. OUTPUT PARAMETERS:
- `LaplacianSolveResult`: Solution potential vector x, final residual norm, and iterations taken.

5. AGENT CONTRACT:
- Role: Electrical flow and Laplacian linear equation solver.
- Rules: Enforce zero-mean projection on rhs b to handle Laplacian singularity.
- Guardrails: If graph is empty, returns empty solution vector.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class LaplacianSolveResult(Generic[TNode]):
    """
    Result container for Laplacian linear system solve L x = b.
    """
    solution: Dict[TNode, float]
    residual_norm: float
    iterations: int
    converged: bool


class LaplacianLinearSolver(Generic[TNode]):
    """
    Solves L x = b using Jacobi Preconditioned Conjugate Gradient (PCG).

    ```yaml
    contract_id: ALGO-GRAPH-SPEC-174
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      rhs: Mapping[TNode, float]
      max_iterations: int
      tolerance: float
    outputs:
      result: LaplacianSolveResult[TNode]
    parameters:
      max_iterations: int
      tolerance: float
    capability_tags:
      - graph
      - spectral
      - laplacian_solver
      - pcg
      - conjugate_gradient
    purity: deterministic
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(iterations * |E|)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6) -> None:
        """
        Args:
            max_iterations: Maximum PCG iterations.
            tolerance: Relative residual tolerance.
        """
        self._max_iterations = max_iterations
        self._tolerance = tolerance

    def solve(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        rhs: Mapping[TNode, float],
    ) -> LaplacianSolveResult[TNode]:
        """
        Solves L x = b for the potential vector x.

        Args:
            adjacency: Graph adjacency map.
            rhs: Target vector b.

        Returns:
            LaplacianSolveResult containing potentials and convergence status.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n == 0:
            return LaplacianSolveResult(solution={}, residual_norm=0.0, iterations=0, converged=True)

        node_idx = {u: i for i, u in enumerate(nodes)}
        degrees = [len(list(adjacency.get(u, ()))) for u in nodes]
        adj_list = [[node_idx[v] for v in adjacency.get(u, ()) if v in node_idx] for u in nodes]

        b = [rhs.get(u, 0.0) for u in nodes]
        mean_b = sum(b) / n
        b = [val - mean_b for val in b]

        norm_b = math.sqrt(sum(val * val for val in b))
        if norm_b < 1e-12:
            return LaplacianSolveResult(
                solution={u: 0.0 for u in nodes},
                residual_norm=0.0,
                iterations=0,
                converged=True,
            )

        def laplacian_mult(x_vec: List[float]) -> List[float]:
            y = [0.0] * n
            for i in range(n):
                y[i] = degrees[i] * x_vec[i] - sum(x_vec[j] for j in adj_list[i])
            return y

        diag_inv = [1.0 / max(1.0, deg) for deg in degrees]

        x = [0.0] * n
        r = list(b)
        z = [diag_inv[i] * r[i] for i in range(n)]
        p = list(z)
        rz_old = sum(r[i] * z[i] for i in range(n))

        iterations = 0
        converged = False

        for k in range(self._max_iterations):
            iterations += 1
            ap = laplacian_mult(p)
            pap = sum(p[i] * ap[i] for i in range(n))
            if abs(pap) < 1e-15:
                break

            alpha = rz_old / pap
            for i in range(n):
                x[i] += alpha * p[i]
                r[i] -= alpha * ap[i]

            res_norm = math.sqrt(sum(val * val for val in r))
            if (res_norm / norm_b) < self._tolerance:
                converged = True
                break

            z = [diag_inv[i] * r[i] for i in range(n)]
            rz_new = sum(r[i] * z[i] for i in range(n))
            beta = rz_new / rz_old if abs(rz_old) > 1e-15 else 0.0
            for i in range(n):
                p[i] = z[i] + beta * p[i]
            rz_old = rz_new

        final_res = math.sqrt(sum(val * val for val in r))
        mean_x = sum(x) / n
        x = [val - mean_x for val in x]

        return LaplacianSolveResult(
            solution={nodes[i]: x[i] for i in range(n)},
            residual_norm=final_res,
            iterations=iterations,
            converged=converged or (final_res / norm_b < self._tolerance),
        )
