"""ALGORITHM & ARCHITECTURE BLUEPRINT: IFDS & IDE INTERPROCEDURAL DATAFLOW ANALYSIS (ALGO-GRAPH-PROG-297)

1. OVERVIEW & OBJECTIVE
Reps-Horwitz-Sagiv (RHS) IFDS (Interprocedural Finite Distributive Subset) and IDE (Interprocedural Distributive
Environment) frameworks transform interprocedural static program dataflow analysis (e.g. taint tracking, uninitialized
variables, secure type state verification) into context-sensitive Dyck/CFL graph reachability problems over
an exploded supergraph G# with procedure summary edges.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|E_supergraph| * |D|^2 + |SummaryEdges|) where D is finite dataflow fact set.
- Time Complexity: O(|E_supergraph| * |D|^3) tabulated worklist reachability.
- Invariants:
  - Context sensitivity is preserved via valid-path (matched call-return paren string) reachability.
  - Summary jump functions memoize transfer effects from procedure entry to exit.

3. INPUT PARAMETERS:
- control_flow_edges: Sequence[tuple[TNode, TNode, str]] (u, v, edge_type) where edge_type in ('call', 'return', 'normal').
- dataflow_facts: Sequence[str] finite domain facts D.
- transfer_functions: Mapping[tuple[TNode, TNode, str], Mapping[str, Collection[str]]] exploded edge functions.
- entry_point: TNode program entry node.
- initial_fact: str entry dataflow seed fact (e.g. '0' or 'lambda').

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'reachable_facts': Dict[TNode, Set[str]] active dataflow facts holding at each program point.
  - 'summary_edges': List[tuple[TNode, str, TNode, str]] computed procedure summary edges.
  - 'evaluated_edges': int total path edges explored in the exploded supergraph.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic program node typing via `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoIfdsIdeDataflowAnalysis(Generic[TNode]):
    """Interprocedural Finite Distributive Subset (IFDS) static analysis via tabulated graph reachability.

    ```yaml
    contract:
      id: ALGO-GRAPH-PROG-297
      name: GraphAlgoIfdsIdeDataflowAnalysis
      inputs:
        - name: control_flow_edges
          type: Sequence[tuple[TNode, TNode, str]]
          description: Supergraph CFG edges (u, v, kind) with kind in ('call', 'return', 'normal').
        - name: dataflow_facts
          type: Sequence[str]
          description: Finite set of dataflow facts D.
        - name: transfer_functions
          type: Mapping[tuple[TNode, TNode, str], Mapping[str, Collection[str]]]
          description: Micro-functions mapping fact d1 at u to facts d2 at v.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Reaching facts per CFG node and procedure summaries.
      parameters:
        entry_point: TNode
        initial_fact: str (default '0')
      capability_tags:
        - STATIC_ANALYSIS
        - IFDS
        - IDE
        - INTERPROCEDURAL_DATAFLOW
        - GRAPH_REACHABILITY
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|E| * |D|^3)
        space: O(|E| * |D|^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        control_flow_edges: Sequence[Tuple[TNode, TNode, str]],
        dataflow_facts: Sequence[str],
        transfer_functions: Mapping[Tuple[TNode, TNode, str], Mapping[str, Collection[str]]],
        entry_point: TNode,
        initial_fact: str = "0",
    ) -> Dict[str, Any]:
        """Runs IFDS tabulated worklist algorithm over exploded supergraph."""
        facts = list(dataflow_facts)
        if initial_fact not in facts:
            facts.insert(0, initial_fact)

        call_edges: List[Tuple[TNode, TNode]] = []
        return_edges: List[Tuple[TNode, TNode]] = []
        normal_edges: List[Tuple[TNode, TNode]] = []

        cfg_succ: Dict[TNode, List[Tuple[TNode, str]]] = collections.defaultdict(list)

        for u, v, kind in control_flow_edges:
            cfg_succ[u].append((v, kind))
            if kind == "call":
                call_edges.append((u, v))
            elif kind == "return":
                return_edges.append((u, v))
            else:
                normal_edges.append((u, v))

        path_edges: Set[Tuple[TNode, str, TNode, str]] = set()
        summary_edges: Set[Tuple[TNode, str, TNode, str]] = set()
        worklist: collections.deque[Tuple[TNode, str, TNode, str]] = collections.deque()

        init_edge = (entry_point, initial_fact, entry_point, initial_fact)
        path_edges.add(init_edge)
        worklist.append(init_edge)

        evaluated_edges = 0

        while worklist:
            s_p, d1, n, d2 = worklist.popleft()
            evaluated_edges += 1

            for m, kind in cfg_succ.get(n, []):
                t_key = (n, m, kind)
                m_func = transfer_functions.get(t_key, {})

                gen_facts = m_func.get(d2, [d2] if d2 == initial_fact else [])

                if kind == "normal":
                    for d3 in gen_facts:
                        edge = (s_p, d1, m, d3)
                        if edge not in path_edges:
                            path_edges.add(edge)
                            worklist.append(edge)

                elif kind == "call":
                    for d3 in gen_facts:
                        edge_call = (m, d3, m, d3)
                        if edge_call not in path_edges:
                            path_edges.add(edge_call)
                            worklist.append(edge_call)

                        for s_p2, d1_2, e_p, d4 in list(summary_edges):
                            if s_p2 == m and d1_2 == d3:
                                for ret_node, r_kind in cfg_succ.get(e_p, []):
                                    if r_kind == "return":
                                        edge_sum = (s_p, d1, ret_node, d4)
                                        if edge_sum not in path_edges:
                                            path_edges.add(edge_sum)
                                            worklist.append(edge_sum)

                elif kind == "return":
                    sum_edge = (s_p, d1, n, d2)
                    if sum_edge not in summary_edges:
                        summary_edges.add(sum_edge)

                    for c_src, d_c1, c_tgt, d_c2 in list(path_edges):
                        if c_tgt == s_p and d_c2 == d1:
                            edge_ret = (c_src, d_c1, m, d2)
                            if edge_ret not in path_edges:
                                path_edges.add(edge_ret)
                                worklist.append(edge_ret)

        reaching: Dict[TNode, Set[str]] = collections.defaultdict(set)
        for _, _, n, d in path_edges:
            reaching[n].add(d)

        return {
            "reachable_facts": dict(reaching),
            "summary_edges": list(summary_edges),
            "evaluated_edges": evaluated_edges,
        }
