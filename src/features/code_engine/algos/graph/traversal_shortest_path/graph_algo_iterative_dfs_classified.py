"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ITERATIVE CLASSIFIED DFS (ALGO-GRAPH-TRV-14)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Iterative depth-first search using an explicit stack preventing recursion
   stack exhaustion. Records discovery and finish timestamps, computes DFS
   trees, detects cycles, and classifies every edge as:
   - Tree Edge (first discovery)
   - Back Edge (ancestor edge -> cycle detection)
   - Forward Edge (descendant non-tree edge)
   - Cross Edge (cross-branch edge)

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) deterministic traversal.
   - Space Complexity: O(V) explicit stack and timestamp arrays.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Verifier.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar, Set

NodeId = TypeVar("NodeId")


class GraphAlgoIterativeDfsClassified(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-14
      name: GraphAlgoIterativeDfsClassified
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, dfs, edge_classification, cycle_detection]
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
        required: [edge_classification, discovery_times, finish_times, has_cycles, topological_order]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    @staticmethod
    def traverse(
        nodes: List[str],
        adjacency_list: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        state: Dict[str, int] = {n: 0 for n in all_nodes}
        discovery_time: Dict[str, int] = {}
        finish_time: Dict[str, int] = {}
        parents: Dict[str, Optional[str]] = {n: None for n in all_nodes}

        classified_edges: List[Dict[str, str]] = []
        finish_order: List[str] = []
        has_cycles = False
        timer = 0

        for root in all_nodes:
            if state[root] != 0:
                continue

            stack: List[Tuple[str, int]] = [(root, 0)]
            state[root] = 1
            timer += 1
            discovery_time[root] = timer

            while stack:
                curr, edge_idx = stack[-1]
                neighbors = adjacency_list.get(curr, [])

                if edge_idx < len(neighbors):
                    neighbor = neighbors[edge_idx]
                    stack[-1] = (curr, edge_idx + 1)

                    if state[neighbor] == 0:
                        parents[neighbor] = curr
                        state[neighbor] = 1
                        timer += 1
                        discovery_time[neighbor] = timer
                        classified_edges.append(
                            {"source": curr, "target": neighbor, "edge_class": "tree"}
                        )
                        stack.append((neighbor, 0))
                    elif state[neighbor] == 1:
                        has_cycles = True
                        classified_edges.append(
                            {"source": curr, "target": neighbor, "edge_class": "back"}
                        )
                    elif state[neighbor] == 2:
                        if discovery_time[curr] < discovery_time[neighbor]:
                            classified_edges.append(
                                {
                                    "source": curr,
                                    "target": neighbor,
                                    "edge_class": "forward",
                                }
                            )
                        else:
                            classified_edges.append(
                                {
                                    "source": curr,
                                    "target": neighbor,
                                    "edge_class": "cross",
                                }
                            )
                else:
                    stack.pop()
                    state[curr] = 2
                    timer += 1
                    finish_time[curr] = timer
                    finish_order.append(curr)

        topological_order = finish_order[::-1] if not has_cycles else []

        return {
            "edge_classification": classified_edges,
            "discovery_times": discovery_time,
            "finish_times": finish_time,
            "parents": parents,
            "has_cycles": has_cycles,
            "topological_order": topological_order,
            "total_nodes": len(all_nodes),
        }
