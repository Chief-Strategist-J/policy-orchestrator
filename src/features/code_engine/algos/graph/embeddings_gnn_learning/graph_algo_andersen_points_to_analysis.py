"""ALGORITHM & ARCHITECTURE BLUEPRINT: ANDERSEN'S POINTS-TO ANALYSIS (INCLUSION-BASED CONSTRAINT PROPAGATION) (ALGO-GRAPH-PROG-299)

1. OVERVIEW & OBJECTIVE
Andersen's points-to analysis (1994) is an inclusion-based (subset-based) flow-insensitive, context-insensitive
interprocedural pointer analysis. It translates program pointer operations into four canonical set constraints:
(1) Address-of: p = &x => loc(x) in pts(p);
(2) Copy / Assignment: p = q => pts(q) subseteq pts(p);
(3) Store / Write: *p = q => for all a in pts(p), pts(q) subseteq pts(a);
(4) Load / Read: p = *q => for all b in pts(q), pts(b) subseteq pts(p).
Executes iterative worklist constraint propagation and dynamic edge insertion on the constraint graph.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|Vars|^2) for constraint graph edges and points-to sets.
- Time Complexity: O(|Vars|^3) cubic worst-case constraint propagation.
- Invariants:
  - Inclusion monotonicity: points-to sets grow monotonically during analysis.
  - Fixpoint guarantee: pts(p) contains all heap/stack locations variable p may reference at runtime.

3. INPUT PARAMETERS:
- statements: Sequence[tuple[str, str, Optional[str]]] pointer statements:
  - ('addr', p, x) for p = &x
  - ('copy', p, q) for p = q
  - ('load', p, q) for p = *q
  - ('store', p, q) for *p = q

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'points_to_sets': Dict[str, Set[str]] mapping each pointer variable to its candidate allocation locations.
  - 'constraint_graph': Dict[str, Set[str]] dynamic inclusion graph edges (q -> p meaning pts(q) subseteq pts(p)).
  - 'iterations': int count of worklist propagations.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic over node/variable type `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAndersenPointsToAnalysis(Generic[TNode]):
    """Andersen's inclusion-based pointer analysis via dynamic constraint graph propagation.

    ```yaml
    contract:
      id: ALGO-GRAPH-PROG-299
      name: GraphAlgoAndersenPointsToAnalysis
      inputs:
        - name: statements
          type: Sequence[tuple[str, str, Optional[str]]]
          description: List of pointer operations: ('addr', p, x), ('copy', p, q), ('load', p, q), ('store', p, q).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Inferred points-to sets pts(p) and inclusion constraint graph.
      capability_tags:
        - STATIC_ANALYSIS
        - POINTER_ANALYSIS
        - ANDERSEN
        - INCLUSION_BASED
        - CONSTRAINT_PROPAGATION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(N^3)
        space: O(N^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        statements: Sequence[Tuple[str, str, Optional[str]]],
    ) -> Dict[str, Any]:
        """Runs Andersen's pointer analysis fixpoint algorithm."""
        all_vars: Set[str] = set()
        for kind, p, q in statements:
            all_vars.add(p)
            if q is not None:
                all_vars.add(q)

        pts: Dict[str, Set[str]] = collections.defaultdict(set)
        graph: Dict[str, Set[str]] = collections.defaultdict(set)
        worklist: collections.deque[str] = collections.deque()

        load_stmts: List[Tuple[str, str]] = []
        store_stmts: List[Tuple[str, str]] = []

        for kind, p, q in statements:
            if kind == "addr" and q is not None:
                pts[p].add(q)
                if p not in worklist:
                    worklist.append(p)
            elif kind == "copy" and q is not None:
                graph[q].add(p)
                if q not in worklist:
                    worklist.append(q)
            elif kind == "load" and q is not None:
                load_stmts.append((p, q))
            elif kind == "store" and q is not None:
                store_stmts.append((p, q))

        iterations = 0

        while worklist:
            v = worklist.popleft()
            iterations += 1
            pts_v = list(pts[v])

            for p, q in load_stmts:
                if q == v:
                    for a in pts_v:
                        if p not in graph[a]:
                            graph[a].add(p)
                            if a not in worklist:
                                worklist.append(a)

            for p, q in store_stmts:
                if p == v:
                    for a in pts_v:
                        if a not in graph[q]:
                            graph[q].add(a)
                            if q not in worklist:
                                worklist.append(q)

            for target in list(graph[v]):
                old_len = len(pts[target])
                pts[target].update(pts_v)
                if len(pts[target]) > old_len:
                    if target not in worklist:
                        worklist.append(target)

        return {
            "points_to_sets": {v: pts[v] for v in all_vars},
            "constraint_graph": {v: graph[v] for v in graph},
            "iterations": iterations,
        }
