"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MAXIMUM WEIGHT CLOSURE (ALGO-GRAPH-ROUT-100)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Maximum Weight Closure (Project Selection Problem) solver using s-t Minimum Cut.
   Selects a subset of projects/tasks with maximal net value subject to prerequisite dependencies
   by reducing the problem to a maximum flow / minimum cut dual certificate.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E^2) single max-flow / min-cut computation.
   - Space Complexity: O(V + E) network flow capacity graph.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Optimal project selection subset obeying all prerequisite constraints.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from src.features.code_engine.algos.graph.connectivity_flows.graph_algo_dinic_max_flow import GraphAlgoDinicMaxFlow

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMaximumWeightClosure(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROUT-100
      name: GraphAlgoMaximumWeightClosure
      version: 1.0.0
      category: graph_routing
      capability_tags: [graph, project_selection, maximum_weight_closure, min_cut_reduction, prerequisites]
      inputs:
        type: object
        required: [node_values, prerequisites]
        properties:
          node_values:
            type: object
            additionalProperties: {type: number}
          prerequisites:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}]
      outputs:
        type: object
        required: [max_closure_weight, selected_nodes]
        properties:
          max_closure_weight: {type: number}
          selected_nodes:
            type: array
            items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^2 * E)
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        node_values: Dict[TNode, float],
        prerequisites: List[Tuple[TNode, TNode]],
    ) -> None:
        self._values: Dict[TNode, float] = node_values
        self._prereqs: List[Tuple[TNode, TNode]] = prerequisites

    def solve_closure(self) -> Tuple[float, Set[TNode]]:
        flow_engine = GraphAlgoDinicMaxFlow[str]()
        source = "__SRC__"
        sink = "__SNK__"
        total_positive = 0.0

        for node, val in self._values.items():
            node_str = str(node)
            if val > 0:
                total_positive += val
                flow_engine.add_edge(source, node_str, val)
            elif val < 0:
                flow_engine.add_edge(node_str, sink, -val)

        for u, v in self._prereqs:
            flow_engine.add_edge(str(u), str(v), float("inf"))

        max_flow_val, _ = flow_engine.compute_max_flow(source, sink)

        reachable: Set[str] = {source}
        queue: List[str] = [source]

        while queue:
            curr = queue.pop(0)
            for nxt in flow_engine._adj.get(curr, []):
                res_cap = flow_engine._capacity.get((curr, nxt), 0.0) - flow_engine._flow.get((curr, nxt), 0.0)
                if res_cap > 1e-9 and nxt not in reachable:
                    reachable.add(nxt)
                    queue.append(nxt)

        selected_str = reachable - {source, sink}
        str_to_node = {str(k): k for k in self._values.keys()}
        selected_nodes: Set[TNode] = {str_to_node[s] for s in selected_str if s in str_to_node}

        max_profit = total_positive - max_flow_val
        return max(0.0, max_profit), selected_nodes
