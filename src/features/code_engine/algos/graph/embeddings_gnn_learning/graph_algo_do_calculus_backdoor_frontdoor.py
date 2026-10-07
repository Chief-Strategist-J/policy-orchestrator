"""ALGORITHM & ARCHITECTURE BLUEPRINT: DO-CALCULUS & ADJUSTMENT CRITERIA (BACKDOOR & FRONTDOOR) (ALGO-GRAPH-CAUSAL-281)

1. OVERVIEW & OBJECTIVE
Identifies causal effects P(Y | do(X)) in causal Directed Acyclic Graphs using Judea Pearl's Backdoor and
Frontdoor Adjustment criteria and Do-Calculus transformation rules. Searches for valid covariate adjustment
sets Z that block all spurious confounding backdoor paths between treatment X and outcome Y without opening
colliders or blocking causal descendant paths.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| + |E|) for storing causal graph and path structures.
- Time Complexity: O(2^|Covariates| * (|V| + |E|)) subset search or polynomial heuristic search.
- Invariants:
  - Backdoor Criterion: (1) No node in Z is a descendant of X; (2) Z blocks every path between X and Y that contains an arrow into X.
  - Frontdoor Criterion: (1) Path X -> M -> Y captures all directed causal effect; (2) No unblocked backdoor between X and M; (3) All backdoor paths between M and Y blocked by X.

3. INPUT PARAMETERS:
- dag_adjacency: Mapping[TNode, Collection[TNode]] directed causal DAG.
- treatment: TNode treatment variable X.
- outcome: TNode outcome variable Y.
- candidate_covariates: Optional[Collection[TNode]] subset of measurable candidate variables.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'is_identifiable': bool True if causal effect is identifiable via backdoor or frontdoor criterion.
  - 'method': str 'backdoor', 'frontdoor', or 'non_identifiable'.
  - 'adjustment_set': Set[TNode] valid covariate adjustment set Z.
  - 'causal_effect_formula': str symbolic formula representation of the adjusted distribution.

5. AGENT CONTRACT:
- Implemented with exact graph path reachability and d-separation checks.
- Zero inline comments.
"""

from __future__ import annotations

import itertools
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDoCalculusBackdoorFrontdoor(Generic[TNode]):
    """Causal effect identification via Backdoor Criterion, Frontdoor Criterion, and Do-Calculus.

    ```yaml
    contract:
      id: ALGO-GRAPH-CAUSAL-281
      name: GraphAlgoDoCalculusBackdoorFrontdoor
      inputs:
        - name: dag_adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Directed causal DAG topology.
        - name: treatment
          type: TNode
          description: Treatment/intervention variable X.
        - name: outcome
          type: TNode
          description: Target outcome variable Y.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Identifiability status, method used, adjustment set, and symbolic formula.
      parameters:
        candidate_covariates: Optional[Collection[TNode]] (default None)
      capability_tags:
        - CAUSAL_INFERENCE
        - DO_CALCULUS
        - BACKDOOR_CRITERION
        - FRONTDOOR_CRITERION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(2^|C| * (|V| + |E|))
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        dag_adjacency: Mapping[TNode, Collection[TNode]],
        treatment: TNode,
        outcome: TNode,
        candidate_covariates: Optional[Collection[TNode]] = None,
    ) -> Dict[str, Any]:
        """Tests backdoor and frontdoor criteria to identify P(Y | do(X))."""
        all_nodes: Set[TNode] = set(dag_adjacency.keys())
        for c_list in dag_adjacency.values():
            all_nodes.update(c_list)
        all_nodes.add(treatment)
        all_nodes.add(outcome)

        descendants_of_x = self._get_descendants(dag_adjacency, treatment)

        covariates = (
            set(candidate_covariates)
            if candidate_covariates is not None
            else all_nodes - {treatment, outcome}
        )

        valid_backdoor_candidates = covariates - descendants_of_x

        dag_no_x_outgoing: Dict[TNode, List[TNode]] = {
            u: [v for v in dag_adjacency.get(u, [])] if u != treatment else []
            for u in all_nodes
        }

        cand_list = list(valid_backdoor_candidates)
        found_backdoor: Optional[Set[TNode]] = None

        for r in range(len(cand_list) + 1):
            for subset in itertools.combinations(cand_list, r):
                z_set = set(subset)
                if self._is_d_separated(dag_no_x_outgoing, treatment, outcome, z_set):
                    found_backdoor = z_set
                    break
            if found_backdoor is not None:
                break

        if found_backdoor is not None:
            formula = (
                f"sum_{{{','.join(str(z) for z in sorted(list(found_backdoor), key=str))}}} "
                f"P({outcome} | {treatment}, {','.join(str(z) for z in sorted(list(found_backdoor), key=str))}) "
                f"P({','.join(str(z) for z in sorted(list(found_backdoor), key=str))})"
                if found_backdoor
                else f"P({outcome} | {treatment})"
            )
            return {
                "is_identifiable": True,
                "method": "backdoor",
                "adjustment_set": found_backdoor,
                "causal_effect_formula": formula,
            }

        mediators = set(dag_adjacency.get(treatment, [])).intersection(
            {u for u in all_nodes if outcome in self._get_descendants(dag_adjacency, u)}
        )
        for m in mediators:
            if self._is_valid_frontdoor(dag_adjacency, treatment, m, outcome):
                formula = (
                    f"sum_{{{m}}} P({m} | {treatment}) "
                    f"sum_{{{treatment}'}} P({outcome} | {treatment}', {m}) P({treatment}')"
                )
                return {
                    "is_identifiable": True,
                    "method": "frontdoor",
                    "adjustment_set": {m},
                    "causal_effect_formula": formula,
                }

        return {
            "is_identifiable": False,
            "method": "non_identifiable",
            "adjustment_set": set(),
            "causal_effect_formula": "",
        }

    def _get_descendants(
        self, dag: Mapping[TNode, Collection[TNode]], src: TNode
    ) -> Set[TNode]:
        """Returns all descendant nodes of src."""
        descendants: Set[TNode] = set()
        queue = list(dag.get(src, []))
        while queue:
            curr = queue.pop(0)
            if curr not in descendants:
                descendants.add(curr)
                queue.extend(dag.get(curr, []))
        return descendants

    def _is_d_separated(
        self,
        dag: Mapping[TNode, Collection[TNode]],
        x: TNode,
        y: TNode,
        z_set: Set[TNode],
    ) -> bool:
        """Tests d-separation between x and y given z_set."""
        all_nodes: Set[TNode] = set(dag.keys())
        for c in dag.values():
            all_nodes.update(c)
        all_nodes.update({x, y})
        all_nodes.update(z_set)

        parents: Dict[TNode, Set[TNode]] = {u: set() for u in all_nodes}
        for u, children in dag.items():
            for v in children:
                parents[v].add(u)

        visited: Set[Tuple[TNode, str]] = set()
        queue = [(x, "from_child")]
        visited.add((x, "from_child"))
        reachable: Set[TNode] = set()

        while queue:
            node, direction = queue.pop(0)
            reachable.add(node)

            if node not in z_set:
                if direction == "from_child":
                    for p in parents[node]:
                        st = (p, "from_child")
                        if st not in visited:
                            visited.add(st)
                            queue.append(st)
                    for c in dag.get(node, []):
                        st = (c, "from_parent")
                        if st not in visited:
                            visited.add(st)
                            queue.append(st)
                elif direction == "from_parent":
                    for c in dag.get(node, []):
                        st = (c, "from_parent")
                        if st not in visited:
                            visited.add(st)
                            queue.append(st)
            else:
                if direction == "from_parent":
                    for p in parents[node]:
                        st = (p, "from_child")
                        if st not in visited:
                            visited.add(st)
                            queue.append(st)

        return y not in reachable

    def _is_valid_frontdoor(
        self,
        dag: Mapping[TNode, Collection[TNode]],
        x: TNode,
        m: TNode,
        y: TNode,
    ) -> bool:
        """Verifies if m satisfies Pearl's frontdoor criterion relative to (x, y)."""
        all_nodes = set(dag.keys())
        for c in dag.values():
            all_nodes.update(c)

        dag_no_x_out: Dict[TNode, List[TNode]] = {
            u: [v for v in dag.get(u, [])] if u != x else [] for u in all_nodes
        }
        if not self._is_d_separated(dag_no_x_out, x, m, set()):
            return False

        dag_no_m_out: Dict[TNode, List[TNode]] = {
            u: [v for v in dag.get(u, [])] if u != m else [] for u in all_nodes
        }
        if not self._is_d_separated(dag_no_m_out, m, y, {x}):
            return False

        return True
