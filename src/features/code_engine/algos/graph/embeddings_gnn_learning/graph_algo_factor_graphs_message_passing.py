"""ALGORITHM & ARCHITECTURE BLUEPRINT: FACTOR GRAPHS & GENERALIZED MESSAGE PASSING (ALGO-GRAPH-PGM-277)

1. OVERVIEW & OBJECTIVE
Generalized message passing on bipartite factor graphs G = (V, F, E) containing discrete variable nodes V
and multi-argument factor nodes F. Computes variable-to-factor messages (products of incoming factor messages)
and factor-to-variable messages (sum-product contractions over factor hyperedges) to derive variable marginals
and factor posteriors.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(sum_{f} |scope(f)| * |K| + |V| * |K|).
- Time Complexity: O(T_iter * sum_{f} |scope(f)| * |K|^|scope(f)|).
- Invariants:
  - Bipartite connectivity: edges only exist between variables and factors.
  - Variable belief is proportional to the product of all incoming factor messages.

3. INPUT PARAMETERS:
- variables: Sequence[TNode] discrete variable identifiers.
- cardinalities: Mapping[TNode, int] domain sizes per variable.
- factors: Sequence[Dict[str, Any]] factor definitions with 'name' (str), 'scope' (List[TNode]), and 'table' (Dict[Tuple[int,...], float]).
- max_iterations: int message update rounds.
- damping: float message smoothing factor.
- tolerance: float message convergence threshold.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'variable_marginals': Dict[TNode, List[float]] posterior distributions for all variables.
  - 'converged': bool convergence status.
  - 'iterations': int count of execution iterations.
  - 'v_to_f_messages': Dict[tuple[TNode, str], List[float]] variable-to-factor messages.
  - 'f_to_v_messages': Dict[tuple[str, TNode], List[float]] factor-to-variable messages.

5. AGENT CONTRACT:
- Strict zero-inline-comment policy.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoFactorGraphsMessagePassing(Generic[TNode]):
    """Generalized Sum-Product message passing on bipartite Factor Graphs.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-277
      name: GraphAlgoFactorGraphsMessagePassing
      inputs:
        - name: variables
          type: Sequence[TNode]
          description: Random variables in the factor graph.
        - name: cardinalities
          type: Mapping[TNode, int]
          description: Cardinality per variable.
        - name: factors
          type: Sequence[Dict[str, Any]]
          description: Factor list with 'name', 'scope', 'table'.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Exact or loopy marginals, message dictionaries, and convergence report.
      parameters:
        max_iterations: int (default 50)
        damping: float (default 0.0)
        tolerance: float (default 1e-6)
      capability_tags:
        - PGM
        - FACTOR_GRAPH
        - SUM_PRODUCT
        - MESSAGE_PASSING
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T_iter * sum_f |scope_f| * |K|^|scope_f|)
        space: O(sum_f |scope_f| * |K| + |V| * |K|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        variables: Sequence[TNode],
        cardinalities: Mapping[TNode, int],
        factors: Sequence[Dict[str, Any]],
        max_iterations: int = 50,
        damping: float = 0.0,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        """Runs iterative two-phase message passing on bipartite factor graph."""
        var_list = list(variables)
        if not var_list:
            return {
                "variable_marginals": {},
                "converged": True,
                "iterations": 0,
                "v_to_f_messages": {},
                "f_to_v_messages": {},
            }

        var_adj_factors: Dict[TNode, List[Dict[str, Any]]] = {v: [] for v in var_list}
        factor_map: Dict[str, Dict[str, Any]] = {}

        for idx, f in enumerate(factors):
            f_name = f.get("name", f"factor_{idx}")
            f_copy = {"name": f_name, "scope": list(f["scope"]), "table": dict(f["table"])}
            factor_map[f_name] = f_copy
            for v in f_copy["scope"]:
                var_adj_factors[v].append(f_copy)

        v_to_f: Dict[Tuple[TNode, str], List[float]] = {}
        f_to_v: Dict[Tuple[str, TNode], List[float]] = {}

        for v in var_list:
            k = cardinalities[v]
            for f in var_adj_factors[v]:
                f_name = f["name"]
                v_to_f[(v, f_name)] = [1.0 / float(k)] * k
                f_to_v[(f_name, v)] = [1.0 / float(k)] * k

        converged = False
        iteration = 0

        for it in range(max_iterations):
            iteration = it + 1
            max_delta = 0.0

            new_f_to_v: Dict[Tuple[str, TNode], List[float]] = {}
            for f_name, f in factor_map.items():
                scope = f["scope"]
                table = f["table"]

                for target_v in scope:
                    k_target = cardinalities[target_v]
                    target_idx = scope.index(target_v)
                    other_vars = [u for u in scope if u != target_v]
                    other_indices = [scope.index(u) for u in other_vars]
                    other_dims = [cardinalities[u] for u in other_vars]

                    msg_out = [0.0] * k_target

                    for val_target in range(k_target):
                        total_sum = 0.0
                        for other_cfg in itertools.product(*[range(d) for d in other_dims]):
                            full_cfg = [0] * len(scope)
                            full_cfg[target_idx] = val_target
                            for u_pos, val_u in zip(other_indices, other_cfg):
                                full_cfg[u_pos] = val_u

                            pot = table.get(tuple(full_cfg), 1.0)
                            prod_incoming = 1.0
                            for u, val_u in zip(other_vars, other_cfg):
                                prod_incoming *= v_to_f.get((u, f_name), [1.0] * cardinalities[u])[val_u]

                            total_sum += pot * prod_incoming

                        msg_out[val_target] = total_sum

                    sum_m = sum(msg_out)
                    norm_msg = [v / sum_m if sum_m > 0.0 else 1.0 / float(k_target) for v in msg_out]

                    old_msg = f_to_v.get((f_name, target_v), norm_msg)
                    damped_msg = [
                        (1.0 - damping) * norm_msg[j] + damping * old_msg[j] for j in range(k_target)
                    ]
                    d_sum = sum(damped_msg)
                    final_msg = [v / d_sum if d_sum > 0.0 else 1.0 / float(k_target) for v in damped_msg]

                    delta = sum(abs(final_msg[j] - old_msg[j]) for j in range(k_target))
                    if delta > max_delta:
                        max_delta = delta

                    new_f_to_v[(f_name, target_v)] = final_msg

            f_to_v = new_f_to_v

            new_v_to_f: Dict[Tuple[TNode, str], List[float]] = {}
            for v in var_list:
                k = cardinalities[v]
                adj_f_list = var_adj_factors[v]

                for target_f in adj_f_list:
                    target_name = target_f["name"]
                    prod = [1.0] * k
                    for other_f in adj_f_list:
                        other_name = other_f["name"]
                        if other_name != target_name:
                            inc = f_to_v.get((other_name, v), [1.0] * k)
                            for s in range(k):
                                prod[s] *= inc[s]

                    sum_p = sum(prod)
                    norm_v_msg = [val / sum_p if sum_p > 0.0 else 1.0 / float(k) for val in prod]
                    new_v_to_f[(v, target_name)] = norm_v_msg

            v_to_f = new_v_to_f

            if max_delta < tolerance:
                converged = True
                break

        marginals: Dict[TNode, List[float]] = {}
        for v in var_list:
            k = cardinalities[v]
            belief = [1.0] * k
            for f in var_adj_factors[v]:
                inc = f_to_v.get((f["name"], v), [1.0] * k)
                for s in range(k):
                    belief[s] *= inc[s]
            sum_b = sum(belief)
            if sum_b > 0.0:
                marginals[v] = [val / sum_b for val in belief]
            else:
                marginals[v] = [1.0 / float(k)] * k

        return {
            "variable_marginals": marginals,
            "converged": converged,
            "iterations": iteration,
            "v_to_f_messages": v_to_f,
            "f_to_v_messages": f_to_v,
        }
