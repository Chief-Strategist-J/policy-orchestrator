"""ALGORITHM & ARCHITECTURE BLUEPRINT: STEENSGAARD'S POINTS-TO ANALYSIS (UNIFICATION-BASED EQUIVALENCE) (ALGO-GRAPH-PROG-300)

1. OVERVIEW & OBJECTIVE
Steensgaard's pointer analysis (1996) is an almost linear-time O(N * alpha(N)) unification-based (equality-based)
flow-insensitive pointer analysis. It treats pointer assignments as bidirectional equivalences (p = q => pts(p) == pts(q)),
using a Disjoint Set Union-Find structure with Tarjan's path compression and union-by-rank to merge points-to sets
into single representative equivalence classes.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|Vars|) Disjoint Set Union-Find partition table.
- Time Complexity: O(|Statements| * alpha(|Vars|)) nearly linear execution time.
- Invariants:
  - Every variable points to at most one representative equivalence class node.
  - Bidirectional alias symmetry: if p aliases q, then pts(p) == pts(q).

3. INPUT PARAMETERS:
- statements: Sequence[tuple[str, str, Optional[str]]] pointer statements:
  - ('addr', p, x) for p = &x
  - ('copy', p, q) for p = q
  - ('load', p, q) for p = *q
  - ('store', p, q) for *p = q

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'points_to_sets': Dict[str, Set[str]] points-to sets for all variables.
  - 'equivalence_classes': Dict[str, str] mapping from variable to its Union-Find root representative.
  - 'unification_count': int total union operations performed.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic over node/variable type `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSteensgaardPointsToAnalysis(Generic[TNode]):
    """Steensgaard's almost linear-time unification-based pointer analysis using Union-Find.

    ```yaml
    contract:
      id: ALGO-GRAPH-PROG-300
      name: GraphAlgoSteensgaardPointsToAnalysis
      inputs:
        - name: statements
          type: Sequence[tuple[str, str, Optional[str]]]
          description: Sequence of pointer operations: ('addr', p, x), ('copy', p, q), ('load', p, q), ('store', p, q).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Inferred points-to equivalence classes and points-to sets.
      capability_tags:
        - STATIC_ANALYSIS
        - POINTER_ANALYSIS
        - STEENSGAARD
        - UNIFICATION_BASED
        - UNION_FIND
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(N * alpha(N))
        space: O(N)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        statements: Sequence[Tuple[str, str, Optional[str]]],
    ) -> Dict[str, Any]:
        """Runs Steensgaard's unification pointer analysis using Disjoint Set Union."""
        all_vars: Set[str] = set()
        for kind, p, q in statements:
            all_vars.add(p)
            if q is not None:
                all_vars.add(q)

        parent: Dict[str, str] = {v: v for v in all_vars}
        points_to: Dict[str, Optional[str]] = {v: None for v in all_vars}
        unification_count = 0

        def find(x: str) -> str:
            path = []
            curr = x
            while parent[curr] != curr:
                path.append(curr)
                curr = parent[curr]
            for node in path:
                parent[node] = curr
            return curr

        def union(x: str, y: str) -> str:
            nonlocal unification_count
            rx, ry = find(x), find(y)
            if rx == ry:
                return rx
            unification_count += 1
            parent[ry] = rx
            pt_x = points_to[rx]
            pt_y = points_to[ry]
            if pt_x is not None and pt_y is not None:
                merged_target = union(pt_x, pt_y)
                points_to[rx] = merged_target
            elif pt_y is not None:
                points_to[rx] = pt_y
            return rx

        for kind, p, q in statements:
            if q is None:
                continue

            rp = find(p)
            rq = find(q)

            if kind == "addr":
                if points_to[rp] is None:
                    points_to[rp] = rq
                else:
                    union(points_to[rp], rq)

            elif kind == "copy":
                if points_to[rq] is not None:
                    if points_to[rp] is None:
                        points_to[rp] = points_to[rq]
                    else:
                        union(points_to[rp], points_to[rq])

            elif kind == "load":
                pt_q = points_to[rq]
                if pt_q is not None:
                    r_pt_q = find(pt_q)
                    if points_to[r_pt_q] is not None:
                        if points_to[rp] is None:
                            points_to[rp] = points_to[r_pt_q]
                        else:
                            union(points_to[rp], points_to[r_pt_q])

            elif kind == "store":
                pt_p = points_to[rp]
                if pt_p is not None:
                    r_pt_p = find(pt_p)
                    if points_to[rq] is not None:
                        if points_to[r_pt_p] is None:
                            points_to[r_pt_p] = points_to[rq]
                        else:
                            union(points_to[r_pt_p], points_to[rq])

        equiv_classes: Dict[str, str] = {v: find(v) for v in all_vars}

        loc_members: Dict[str, Set[str]] = collections.defaultdict(set)
        for v in all_vars:
            loc_members[find(v)].add(v)

        final_pts: Dict[str, Set[str]] = {}
        for v in all_vars:
            rv = find(v)
            target = points_to.get(rv)
            if target is not None:
                r_target = find(target)
                final_pts[v] = set(loc_members[r_target])
            else:
                final_pts[v] = set()

        return {
            "points_to_sets": final_pts,
            "equivalence_classes": equiv_classes,
            "unification_count": unification_count,
        }
