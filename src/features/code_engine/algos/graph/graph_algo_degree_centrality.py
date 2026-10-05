"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DEGREE CENTRALITY (ALGO-GRAPH-06)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates normalized in-degree, out-degree, and total degree centrality
   for all nodes in directed or undirected graphs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E)
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Any


class GraphAlgoDegreeCentrality:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-06
      name: GraphAlgoDegreeCentrality
      version: 1.0.0
      category: graph
      capability_tags: [graph, centrality, degree_centrality, in_degree, out_degree]
      inputs:
        type: object
        required: [adjacency_list]
        properties:
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [in_degree, out_degree, total_degree]
        properties:
          in_degree:
            type: object
            additionalProperties: {type: number}
          out_degree:
            type: object
            additionalProperties: {type: number}
          total_degree:
            type: object
            additionalProperties: {type: number}
      parameters:
        normalized: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(V + E)
        space: O(V)
      preconditions:
        - len(input.adjacency_list) >= 0
      postconditions:
        - len(output.total_degree) >= 0
      compatible_adapters:
        - ADAPTER-GRAPH-TO-DEGREE-CENTRALITY
    ---
    """

    @staticmethod
    def compute(
        adjacency_list: Dict[str, List[str]],
        normalized: bool = True,
    ) -> Dict[str, Any]:
        nodes = set(adjacency_list.keys())
        for targets in adjacency_list.values():
            nodes.update(targets)

        n = len(nodes)
        if n <= 1:
            scale = 1.0
        else:
            scale = 1.0 / (n - 1) if normalized else 1.0

        in_deg: Dict[str, float] = {node: 0.0 for node in nodes}
        out_deg: Dict[str, float] = {node: 0.0 for node in nodes}

        for u, targets in adjacency_list.items():
            out_deg[u] = float(len(targets))
            for v in targets:
                in_deg[v] = in_deg.get(v, 0.0) + 1.0

        total_deg: Dict[str, float] = {
            node: in_deg[node] + out_deg[node] for node in nodes
        }

        if normalized:
            in_deg = {k: round(v * scale, 6) for k, v in in_deg.items()}
            out_deg = {k: round(v * scale, 6) for k, v in out_deg.items()}
            total_deg = {k: round(v * scale, 6) for k, v in total_deg.items()}

        return {
            "in_degree": in_deg,
            "out_degree": out_deg,
            "total_degree": total_deg,
            "node_count": n,
        }
