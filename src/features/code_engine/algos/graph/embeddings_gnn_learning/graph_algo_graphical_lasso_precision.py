"""ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPHICAL LASSO (SPARSE PRECISION MATRIX ESTIMATION) (ALGO-GRAPH-CAUSAL-282)

1. OVERVIEW & OBJECTIVE
Estimates sparse precision (inverse covariance) matrix Theta = Sigma^{-1} under L1-regularization (Graphical Lasso / GLASSO)
for Gaussian Markov Random Fields (GMRFs). Employs block coordinate descent or soft-thresholded covariance
inversion to identify conditional independence graph topology, where Theta_{ij} = 0 corresponds directly
to conditional independence between variables X_i and X_j given all other variables.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V|^2) for storing empirical covariance S and precision matrix Theta.
- Time Complexity: O(T_iter * |V|^3) for coordinate descent GLASSO optimization.
- Invariants:
  - Precision matrix Theta is symmetric positive definite (or positive semi-definite).
  - Off-diagonal entry Theta_{ij} == 0 implies conditional independence X_i _|_ X_j | X_{V \ {i, j}}.

3. INPUT PARAMETERS:
- variables: Sequence[TNode] continuous random variable identifiers.
- empirical_covariance: Sequence[Sequence[float]] |V| x |V| positive semi-definite sample covariance matrix S.
- l1_penalty: float sparsity regularization parameter lambda > 0.
- max_iterations: int coordinate descent iteration cutoff.
- tolerance: float duality gap / matrix change convergence threshold.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'precision_matrix': Dict[tuple[TNode, TNode], float] sparse precision estimates Theta_{ij}.
  - 'conditional_independence_graph': Dict[TNode, List[TNode]] sparse Markov network adjacency.
  - 'converged': bool convergence status.
  - 'iterations': int completed optimization cycles.

5. AGENT CONTRACT:
- Implemented with pure Python linear algebra and soft-thresholding operators.
- Zero inline comments inside method bodies.
"""

from __future__ import annotations

import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphicalLassoPrecision(Generic[TNode]):
    """Sparse inverse covariance estimation (Graphical Lasso) for learning Gaussian Markov Random Fields.

    ```yaml
    contract:
      id: ALGO-GRAPH-CAUSAL-282
      name: GraphAlgoGraphicalLassoPrecision
      inputs:
        - name: variables
          type: Sequence[TNode]
          description: List of random variables.
        - name: empirical_covariance
          type: Sequence[Sequence[float]]
          description: Empirical sample covariance matrix S (|V| x |V|).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Sparse precision matrix and inferred conditional independence graph.
      parameters:
        l1_penalty: float (default 0.1)
        max_iterations: int (default 100)
        tolerance: float (default 1e-4)
      capability_tags:
        - CAUSAL_DISCOVERY
        - GRAPHICAL_LASSO
        - MARKOV_RANDOM_FIELD
        - PRECISION_ESTIMATION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T_iter * |V|^3)
        space: O(|V|^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        variables: Sequence[TNode],
        empirical_covariance: Sequence[Sequence[float]],
        l1_penalty: float = 0.1,
        max_iterations: int = 100,
        tolerance: float = 1e-4,
    ) -> Dict[str, Any]:
        """Runs block coordinate descent Graphical Lasso to estimate sparse precision matrix."""
        var_list = list(variables)
        p = len(var_list)
        if p == 0:
            return {
                "precision_matrix": {},
                "conditional_independence_graph": {},
                "converged": True,
                "iterations": 0,
            }

        s_mat = [[float(empirical_covariance[i][j]) for j in range(p)] for i in range(p)]
        w_mat = [[s_mat[i][j] + (l1_penalty if i == j else 0.0) for j in range(p)] for i in range(p)]
        theta_mat = [[1.0 / max(1e-6, w_mat[i][i]) if i == j else 0.0 for j in range(p)] for i in range(p)]

        converged = False
        iteration = 0

        for it in range(max_iterations):
            iteration = it + 1
            max_delta = 0.0

            for j in range(p):
                other_indices = [i for i in range(p) if i != j]
                s_12 = [s_mat[i][j] for i in other_indices]
                w_11 = [[w_mat[r][c] for c in other_indices] for r in other_indices]

                beta = self._lasso_coordinate_descent(w_11, s_12, l1_penalty)

                w_12_new = [0.0] * (p - 1)
                for r in range(p - 1):
                    s = 0.0
                    for c in range(p - 1):
                        s += w_11[r][c] * beta[c]
                    w_12_new[r] = s

                for idx, r in enumerate(other_indices):
                    delta = abs(w_mat[r][j] - w_12_new[idx])
                    if delta > max_delta:
                        max_delta = delta
                    w_mat[r][j] = w_12_new[idx]
                    w_mat[j][r] = w_12_new[idx]

                w_22 = w_mat[j][j]
                beta_dot_w12 = sum(beta[r] * w_12_new[r] for r in range(p - 1))
                denom = max(1e-12, w_22 - beta_dot_w12)
                theta_jj = 1.0 / denom
                theta_12 = [-b * theta_jj for b in beta]

                theta_mat[j][j] = theta_jj
                for idx, r in enumerate(other_indices):
                    theta_mat[r][j] = theta_12[idx]
                    theta_mat[j][r] = theta_12[idx]

            if max_delta < tolerance:
                converged = True
                break

        precision_dict: Dict[Tuple[TNode, TNode], float] = {}
        graph_adj: Dict[TNode, List[TNode]] = {u: [] for u in var_list}

        for i, u in enumerate(var_list):
            for j, v in enumerate(var_list):
                val = theta_mat[i][j]
                precision_dict[(u, v)] = val
                if i != j and abs(val) > 1e-5:
                    graph_adj[u].append(v)

        return {
            "precision_matrix": precision_dict,
            "conditional_independence_graph": graph_adj,
            "converged": converged,
            "iterations": iteration,
        }

    def _lasso_coordinate_descent(
        self,
        w_11: List[List[float]],
        s_12: List[float],
        lam: float,
        max_inner_iter: int = 50,
        tol: float = 1e-4,
    ) -> List[float]:
        """Solves Lasso subproblem: min 0.5 * beta^T * W_11 * beta - s_12^T * beta + lam * ||beta||_1."""
        dim = len(s_12)
        beta = [0.0] * dim

        for _ in range(max_inner_iter):
            max_d = 0.0
            for i in range(dim):
                w_ii = max(1e-6, w_11[i][i])
                rho = s_12[i] - sum(w_11[i][j] * beta[j] for j in range(dim) if j != i)
                new_beta_i = self._soft_threshold(rho, lam) / w_ii
                d = abs(new_beta_i - beta[i])
                if d > max_d:
                    max_d = d
                beta[i] = new_beta_i
            if max_d < tol:
                break
        return beta

    def _soft_threshold(self, x: float, lam: float) -> float:
        """Soft thresholding operator sign(x) * max(0, |x| - lam)."""
        if x > lam:
            return x - lam
        if x < -lam:
            return x + lam
        return 0.0
