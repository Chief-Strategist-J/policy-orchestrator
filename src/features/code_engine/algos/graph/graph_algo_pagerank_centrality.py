"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PAGERANK CENTRALITY (ALGO-GRAPH-05)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes link analysis ranking scores for every node in a directed graph
   using power iteration with a random teleport damping factor (default 0.85).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E))
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Any


class GraphAlgoPageRankCentrality:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-05
      name: GraphAlgoPageRankCentrality
      version: 1.0.0
      category: graph
      capability_tags: [graph, centrality, pagerank, link_analysis]
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
        required: [scores, iterations, converged]
        properties:
          scores:
            type: object
            additionalProperties: {type: number}
          iterations: {type: integer}
          converged: {type: boolean}
      parameters:
        damping_factor: {type: number, default: 0.85}
        max_iterations: {type: integer, default: 100}
        tolerance: {type: number, default: 1e-6}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(K * (V + E))
        space: O(V)
      preconditions:
        - len(input.adjacency_list) > 0
      postconditions:
        - abs(sum(output.scores.values()) - 1.0) < 1e-3 or len(output.scores) == 0
      compatible_adapters:
        - ADAPTER-GRAPH-TO-PAGERANK
    ---
    """

    @staticmethod
    def compute(
        adjacency_list: Dict[str, List[str]],
        damping_factor: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        nodes = set(adjacency_list.keys())
        for targets in adjacency_list.values():
            nodes.update(targets)

        n = len(nodes)
        if n == 0:
            return {"scores": {}, "iterations": 0, "converged": True}

        node_list = list(nodes)
        scores = {node: 1.0 / n for node in node_list}

        in_links: Dict[str, List[str]] = {node: [] for node in node_list}
        out_degrees: Dict[str, int] = {node: 0 for node in node_list}

        for u, targets in adjacency_list.items():
            out_degrees[u] = len(targets)
            for v in targets:
                in_links[v].append(u)

        converged = False
        iteration = 0

        for iteration in range(1, max_iterations + 1):
            next_scores: Dict[str, float] = {}
            dangling_sum = sum(scores[u] for u in node_list if out_degrees[u] == 0)

            for node in node_list:
                rank_sum = sum(
                    scores[in_node] / out_degrees[in_node]
                    for in_node in in_links[node]
                    if out_degrees[in_node] > 0
                )
                rank_sum += dangling_sum / n
                next_scores[node] = (1.0 - damping_factor) / n + damping_factor * rank_sum

            diff = sum(abs(next_scores[node] - scores[node]) for node in node_list)
            scores = next_scores

            if diff < tolerance:
                converged = True
                break

        return {
            "scores": {k: round(v, 8) for k, v in scores.items()},
            "iterations": iteration,
            "converged": converged,
        }
