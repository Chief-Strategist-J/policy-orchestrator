"""ALGORITHM & ARCHITECTURE BLUEPRINT: MEAN-FIELD VARIATIONAL INFERENCE (ALGO-GRAPH-PGM-275)

1. OVERVIEW & OBJECTIVE
Deterministic variational approximation for high-dimensional discrete graphical models under the
fully factorized mean-field family Q(X) = prod_{i} q_i(X_i). Coordinates iterative updates of local variational
factors q_i by taking expectations of log-factors with respect to all other variables Q_{-i}, maximizing the
Evidence Lower Bound (ELBO) until convergence.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * |K|) storing variational distributions q_i.
- Time Complexity: O(T_iter * sum_{f} prod_{v in scope(f)} |K_v|).
- Invariants:
  - Each variational factor q_i(x_i) is a valid probability distribution summing to 1.0.
  - ELBO monotonically increases at each coordinate ascent step up to numerical precision.

3. INPUT PARAMETERS:
- variables: Sequence[TNode] discrete variable set.
- cardinalities: Mapping[TNode, int] domain cardinality for each variable.
- factors: Sequence[Dict[str, Any]] log-factor potentials or energy functions.
- max_iterations: int maximum coordinate ascent iterations.
- tolerance: float KL divergence / distribution update threshold.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'variational_marginals': Dict[TNode, List[float]] converged factors q_i(X_i).
  - 'elbo': float final Evidence Lower Bound.
  - 'converged': bool convergence flag.
  - 'iterations': int count of coordinate ascent rounds.

5. AGENT CONTRACT:
- Strict zero-inline-comment rule.
- Generic type parameterization over `TNode`.
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMeanFieldVariationalInference(Generic[TNode]):
    """Coordinate Ascent Mean-Field Variational Inference for graphical models.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-275
      name: GraphAlgoMeanFieldVariationalInference
      inputs:
        - name: variables
          type: Sequence[TNode]
          description: Variables in the model.
        - name: cardinalities
          type: Mapping[TNode, int]
          description: Variable state domain sizes.
        - name: factors
          type: Sequence[Dict[str, Any]]
          description: Energy factors with 'scope' and 'table' (probabilities or unnormalized weights).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Approximate marginals q_i, final ELBO, and convergence statistics.
      parameters:
        max_iterations: int (default 100)
        tolerance: float (default 1e-6)
      capability_tags:
        - PGM
        - VARIATIONAL_INFERENCE
        - MEAN_FIELD
        - ELBO_OPTIMIZATION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T_iter * sum_f |scope_f|^K)
        space: O(|V| * |K|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        variables: Sequence[TNode],
        cardinalities: Mapping[TNode, int],
        factors: Sequence[Dict[str, Any]],
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        """Executes Coordinate Ascent Variational Inference (CAVI) on factorized family."""
        var_list = list(variables)
        if not var_list:
            return {
                "variational_marginals": {},
                "elbo": 0.0,
                "converged": True,
                "iterations": 0,
            }

        q: Dict[TNode, List[float]] = {
            v: [1.0 / float(cardinalities[v])] * cardinalities[v] for v in var_list
        }

        var_to_factors: Dict[TNode, List[Dict[str, Any]]] = {v: [] for v in var_list}
        for f in factors:
            for v in f["scope"]:
                var_to_factors[v].append(f)

        converged = False
        iteration = 0

        for it in range(max_iterations):
            iteration = it + 1
            max_delta = 0.0

            for v in var_list:
                k = cardinalities[v]
                log_q_unnorm = [0.0] * k

                for val_v in range(k):
                    expected_log_p = 0.0
                    for f in var_to_factors[v]:
                        f_scope = f["scope"]
                        other_vars = [u for u in f_scope if u != v]
                        other_dims = [cardinalities[u] for u in other_vars]

                        for other_cfg in itertools.product(*[range(d) for d in other_dims]):
                            q_weight = 1.0
                            full_cfg_dict = dict(zip(other_vars, other_cfg))
                            full_cfg_dict[v] = val_v

                            for u, state_u in zip(other_vars, other_cfg):
                                q_weight *= q[u][state_u]

                            full_cfg = tuple(full_cfg_dict[u] for u in f_scope)
                            pot = f["table"].get(full_cfg, 1e-15)
                            log_pot = math.log(max(1e-15, float(pot)))
                            expected_log_p += q_weight * log_pot

                    log_q_unnorm[val_v] = expected_log_p

                max_log = max(log_q_unnorm)
                exp_q = [math.exp(val - max_log) for val in log_q_unnorm]
                sum_exp = sum(exp_q)
                new_q_v = [val / sum_exp for val in exp_q]

                delta = sum(abs(new_q_v[j] - q[v][j]) for j in range(k))
                if delta > max_delta:
                    max_delta = delta

                q[v] = new_q_v

            if max_delta < tolerance:
                converged = True
                break

        elbo = 0.0
        for f in factors:
            f_scope = f["scope"]
            dims = [cardinalities[u] for u in f_scope]
            for cfg in itertools.product(*[range(d) for d in dims]):
                prob_q = 1.0
                for u, state_u in zip(f_scope, cfg):
                    prob_q *= q[u][state_u]
                pot = f["table"].get(cfg, 1e-15)
                log_pot = math.log(max(1e-15, float(pot)))
                elbo += prob_q * log_pot

        for v in var_list:
            for val in range(cardinalities[v]):
                if q[v][val] > 1e-15:
                    elbo -= q[v][val] * math.log(q[v][val])

        return {
            "variational_marginals": q,
            "elbo": elbo,
            "converged": converged,
            "iterations": iteration,
        }
