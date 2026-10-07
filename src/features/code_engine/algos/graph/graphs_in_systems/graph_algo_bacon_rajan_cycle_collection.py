"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Bacon-Rajan Cycle Collection (ALGO-GRAPH-SYS-307)

1. OVERVIEW & OBJECTIVE:
Implements the Bacon-Rajan synchronous/asynchronous cycle collection algorithm for
reference-counted runtimes. Resolves cyclic data structures that reference counting alone
fails to collect. Operates via trial deletion: marking candidate subgraphs gray by subtracting
internal references, scanning to detect surviving external references (restoring black),
and reclaiming isolated zero-count cycles (collecting white).

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(|V_candidate_subgraph| + |E_candidate_subgraph|) proportional to candidate size.
- Space Complexity: O(|V_candidate_subgraph|) auxiliary map for trial refcounts and colors.
- Invariants: Objects with external references are never collected; trial decrements are
  precisely balanced and restored on surviving subgraphs.

3. INPUT PARAMETERS:
- `references`: Dict[TNode, List[TNode]] mapping each object to referenced child objects.
- `external_ref_counts`: Dict[TNode, int] total actual incoming reference count per object.
- `candidate_roots`: List[TNode] or Set[TNode] candidate objects whose refcount was decremented.

4. OUTPUT PARAMETERS:
- `collected_cycles`: List[Set[TNode]] identified cyclic garbage components reclaimed.
- `freed_nodes`: Set[TNode] total set of nodes collected by cycle detection.
- `surviving_nodes`: Set[TNode] candidates validated as having active external references.
- `final_ref_counts`: Dict[TNode, int] post-collection reference counts of remaining objects.

5. AGENT CONTRACT:
- Role: Analyst and Operator.
- Rules: Operates locally on decrement candidate buffers without scanning full heap.
- Guardrails: Validate external pointer safety before final reclamation.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from collections import defaultdict

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBaconRajanCycleCollection(Generic[TNode]):
    """
    inputs:
      references: Dict[TNode, List[TNode]]
      external_ref_counts: Dict[TNode, int]
      candidate_roots: List[TNode]
    outputs:
      collected_cycles: List[Set[TNode]]
      freed_nodes: Set[TNode]
      surviving_nodes: Set[TNode]
      final_ref_counts: Dict[TNode, int]
    parameters:
      none
    capability_tags:
      - reference_counting
      - cycle_collection
      - trial_deletion
      - bacon_rajan
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(|V_sub| + |E_sub|)"
      space: "O(|V_sub|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        references: Dict[TNode, List[TNode]],
        external_ref_counts: Dict[TNode, int],
        candidate_roots: List[TNode],
    ) -> Dict[str, Any]:
        all_nodes: Set[TNode] = set(references.keys())
        for targets in references.values():
            all_nodes.update(targets)

        trial_rc: Dict[TNode, int] = {
            node: external_ref_counts.get(node, 0) for node in all_nodes
        }
        color: Dict[TNode, str] = {node: "black" for node in all_nodes}

        def mark_gray(s: TNode, visited: Set[TNode]) -> None:
            if color[s] != "gray":
                color[s] = "gray"
                for target in references.get(s, []):
                    trial_rc[target] = trial_rc.get(target, 0) - 1
                    if target not in visited:
                        visited.add(target)
                        mark_gray(target, visited)

        def scan_black(s: TNode) -> None:
            color[s] = "black"
            for target in references.get(s, []):
                trial_rc[target] = trial_rc.get(target, 0) + 1
                if color.get(target) != "black":
                    scan_black(target)

        def scan(s: TNode, visited: Set[TNode]) -> None:
            if color[s] == "gray":
                if trial_rc.get(s, 0) > 0:
                    scan_black(s)
                else:
                    color[s] = "white"
                    for target in references.get(s, []):
                        if target not in visited:
                            visited.add(target)
                            scan(target, visited)

        for root in candidate_roots:
            if root in all_nodes and color[root] == "black":
                visited_gray: Set[TNode] = {root}
                mark_gray(root, visited_gray)
                visited_scan: Set[TNode] = {root}
                scan(root, visited_scan)

        freed_nodes: Set[TNode] = {node for node, c in color.items() if c == "white"}
        surviving_nodes: Set[TNode] = all_nodes - freed_nodes

        collected_cycles: List[Set[TNode]] = []
        visited_collect: Set[TNode] = set()
        for node in freed_nodes:
            if node not in visited_collect:
                cycle_comp: Set[TNode] = set()
                q = [node]
                visited_collect.add(node)
                while q:
                    curr = q.pop()
                    cycle_comp.add(curr)
                    for target in references.get(curr, []):
                        if target in freed_nodes and target not in visited_collect:
                            visited_collect.add(target)
                            q.append(target)
                collected_cycles.append(cycle_comp)

        final_counts: Dict[TNode, int] = {}
        for node in surviving_nodes:
            cnt = external_ref_counts.get(node, 0)
            for freed in freed_nodes:
                if node in references.get(freed, []):
                    cnt -= 1
            final_counts[node] = max(0, cnt)

        return {
            "collected_cycles": collected_cycles,
            "freed_nodes": freed_nodes,
            "surviving_nodes": surviving_nodes,
            "final_ref_counts": final_counts,
        }
