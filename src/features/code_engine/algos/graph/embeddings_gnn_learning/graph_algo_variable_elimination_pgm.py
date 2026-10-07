"""ALGORITHM & ARCHITECTURE BLUEPRINT: VARIABLE ELIMINATION FOR GRAPHICAL MODELS (ALGO-GRAPH-PGM-273)

1. OVERVIEW & OBJECTIVE
Exact probabilistic inference in discrete graphical models (Bayesian Networks and Markov Random Fields)
via dynamic programming factor marginalization (Variable Elimination). Successively sums out non-query,
non-evidence nuisance variables according to a min-fill or min-degree heuristic elimination order,
multiplying associated factors and reducing intermediate tensor dimensionality.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|K|^w) where w is the induced width of the elimination ordering.
- Time Complexity: O(N * |K|^w) where N is factor count and K is maximum domain size.
- Invariants:
  - Eliminated variables are removed from the active factor pool permanently.
  - Query marginal sums to 1.0 upon normalization by partition function Z.

3. INPUT PARAMETERS:
- query_variables: Sequence[TNode] targets for posterior marginal estimation.
- evidence: Mapping[TNode, int] fixed variable observations.
- factors: Sequence[Dict[str, Any]] list of discrete factors with 'scope' and 'table' (Dict[Tuple[int, ...], float]).
- elimination_order: Optional[Sequence[TNode]] explicit ordering for variable elimination.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'posterior': Dict[Tuple[int, ...], float] normalized joint probability table for query variables.
  - 'query_variables': List[TNode] order of variables in the posterior table keys.
  - 'partition_function': float normalizer constant Z = P(evidence).
  - 'elimination_order': List[TNode] executed variable elimination sequence.

5. AGENT CONTRACT:
- Pure algorithmic computation with zero inline comments.
- Automatic heuristic min-weight / min-fill variable ordering when none is specified.
"""

from __future__ import annotations

import itertools
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoVariableEliminationPgm(Generic[TNode]):
    """Exact inference in Bayesian & Markov networks via Variable Elimination.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-273
      name: GraphAlgoVariableEliminationPgm
      inputs:
        - name: query_variables
          type: Sequence[TNode]
          description: Target variable identifiers.
        - name: evidence
          type: Mapping[TNode, int]
          description: Fixed variable value assignments.
        - name: factors
          type: Sequence[Dict[str, Any]]
          description: Factor dictionaries with 'scope': List[TNode] and 'table': Dict[Tuple[int,...], float].
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Posterior factor, query variable list, and partition constant Z.
      parameters:
        elimination_order: Optional[Sequence[TNode]] (default None)
      capability_tags:
        - PGM
        - EXACT_INFERENCE
        - VARIABLE_ELIMINATION
        - FACTOR_OPERATIONS
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(N * |K|^w)
        space: O(|K|^w)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        query_variables: Sequence[TNode],
        evidence: Mapping[TNode, int],
        factors: Sequence[Dict[str, Any]],
        elimination_order: Optional[Sequence[TNode]] = None,
    ) -> Dict[str, Any]:
        """Performs variable elimination and returns the normalized query marginal."""
        query_set = set(query_variables)
        evidence_set = set(evidence.keys())

        active_factors: List[Dict[str, Any]] = []
        all_variables: Set[TNode] = set()

        for f in factors:
            scope = list(f["scope"])
            table = dict(f["table"])
            for v in scope:
                all_variables.add(v)

            if any(v in evidence_set for v in scope):
                reduced_scope = [v for v in scope if v not in evidence_set]
                reduced_table: Dict[Tuple[int, ...], float] = {}
                for cfg, val in table.items():
                    match = True
                    for v, idx in zip(scope, cfg):
                        if v in evidence and evidence[v] != idx:
                            match = False
                            break
                    if match:
                        new_cfg = tuple(cfg[i] for i, v in enumerate(scope) if v not in evidence_set)
                        reduced_table[new_cfg] = reduced_table.get(new_cfg, 0.0) + val
                active_factors.append({"scope": reduced_scope, "table": reduced_table})
            else:
                active_factors.append({"scope": scope, "table": table})

        hidden_variables = all_variables - query_set - evidence_set
        if elimination_order is not None:
            order = [v for v in elimination_order if v in hidden_variables]
        else:
            order = self._heuristic_order(hidden_variables, active_factors)

        for var in order:
            relevant = [f for f in active_factors if var in f["scope"]]
            if not relevant:
                continue

            active_factors = [f for f in active_factors if var not in f["scope"]]
            combined = relevant[0]
            for f in relevant[1:]:
                combined = self._multiply_factors(combined, f)

            summed = self._sum_out_variable(combined, var)
            if summed["scope"]:
                active_factors.append(summed)

        final_factor = active_factors[0] if active_factors else {"scope": list(query_variables), "table": {(): 1.0}}
        for f in active_factors[1:]:
            final_factor = self._multiply_factors(final_factor, f)

        final_table = final_factor["table"]
        z_normalizer = sum(final_table.values())

        if z_normalizer > 0.0:
            normalized_table = {cfg: val / z_normalizer for cfg, val in final_table.items()}
        else:
            normalized_table = dict(final_table)

        return {
            "posterior": normalized_table,
            "query_variables": final_factor["scope"],
            "partition_function": z_normalizer,
            "elimination_order": order,
        }

    def _multiply_factors(self, f1: Dict[str, Any], f2: Dict[str, Any]) -> Dict[str, Any]:
        """Pointwise multiplication of two factors over their union scope."""
        s1, t1 = f1["scope"], f1["table"]
        s2, t2 = f2["scope"], f2["table"]

        union_scope = list(s1) + [v for v in s2 if v not in s1]
        idx1 = [union_scope.index(v) for v in s1]
        idx2 = [union_scope.index(v) for v in s2]

        new_table: Dict[Tuple[int, ...], float] = {}

        for cfg1, v1 in t1.items():
            for cfg2, v2 in t2.items():
                consistent = True
                for i, var in enumerate(s2):
                    if var in s1:
                        j = s1.index(var)
                        if cfg1[j] != cfg2[i]:
                            consistent = False
                            break
                if consistent:
                    combined_cfg = list(cfg1) + [cfg2[i] for i, v in enumerate(s2) if v not in s1]
                    new_table[tuple(combined_cfg)] = v1 * v2

        return {"scope": union_scope, "table": new_table}

    def _sum_out_variable(self, factor: Dict[str, Any], var: TNode) -> Dict[str, Any]:
        """Marginalizes out a single variable from factor."""
        scope, table = factor["scope"], factor["table"]
        if var not in scope:
            return factor

        var_idx = scope.index(var)
        new_scope = [v for v in scope if v != var]
        new_table: Dict[Tuple[int, ...], float] = {}

        for cfg, val in table.items():
            sub_cfg = tuple(val_elem for i, val_elem in enumerate(cfg) if i != var_idx)
            new_table[sub_cfg] = new_table.get(sub_cfg, 0.0) + val

        return {"scope": new_scope, "table": new_table}

    def _heuristic_order(
        self, hidden_vars: Set[TNode], factors: List[Dict[str, Any]]
    ) -> List[TNode]:
        """Computes min-degree heuristic elimination ordering."""
        order: List[TNode] = []
        remaining = set(hidden_vars)
        while remaining:
            best_var = min(
                remaining,
                key=lambda v: sum(len(f["scope"]) for f in factors if v in f["scope"]),
            )
            order.append(best_var)
            remaining.remove(best_var)
        return order
