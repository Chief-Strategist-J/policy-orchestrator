"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TOPOLOGICAL SORT & LEVEL LAYERS (ALGO-GRAPH-TRV-23)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates topological sorting for Directed Acyclic Graphs (DAGs) using Kahn's
   in-degree queue algorithm. Decomposes dependencies into parallel execution
   waves (layers), detecting cyclic dependency deadlocks deterministically.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) strictly linear.
   - Space Complexity: O(V + E) for in-degree and adjacency lookups.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
   - Guarantees: Generates parallel DAG execution waves for task pipelines.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Any, Set, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoTopologicalSort(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-23
      name: GraphAlgoTopologicalSort
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, topological_sort, kahns_algorithm, dag_waves]
      inputs:
        type: object
        required: [nodes, adjacency_list]
        properties:
          nodes:
            type: array
            items: {type: string}
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [is_dag, topological_order, execution_layers, cycle_nodes]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    @staticmethod
    def sort(
        nodes: List[str],
        adjacency_list: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        in_degrees: Dict[str, int] = {n: 0 for n in all_nodes}

        for u, neighbors in adjacency_list.items():
            for v in neighbors:
                if v in in_degrees:
                    in_degrees[v] += 1
                else:
                    in_degrees[v] = 1

        queue: deque[str] = deque(sorted([n for n in all_nodes if in_degrees[n] == 0]))
        topological_order: List[str] = []
        execution_layers: List[List[str]] = []

        while queue:
            layer_size = len(queue)
            current_layer: List[str] = []

            for _ in range(layer_size):
                curr = queue.popleft()
                current_layer.append(curr)
                topological_order.append(curr)

                for neighbor in adjacency_list.get(curr, []):
                    if neighbor in in_degrees:
                        in_degrees[neighbor] -= 1
                        if in_degrees[neighbor] == 0:
                            queue.append(neighbor)

            if current_layer:
                execution_layers.append(sorted(current_layer))

        is_dag = len(topological_order) == len(all_nodes)
        cycle_nodes = (
            sorted([n for n in all_nodes if in_degrees[n] > 0]) if not is_dag else []
        )

        return {
            "is_dag": is_dag,
            "topological_order": topological_order if is_dag else [],
            "execution_layers": execution_layers if is_dag else [],
            "num_layers": len(execution_layers) if is_dag else 0,
            "cycle_nodes": cycle_nodes,
            "total_nodes": len(all_nodes),
        }
