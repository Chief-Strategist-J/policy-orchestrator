"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TARJAN STRONGLY CONNECTED COMPONENTS (ALGO-GRAPH-08)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Finds all maximal strongly connected subgraphs in a directed graph in a single
   DFS pass using discovery indices and low-link values.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E)
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Set, Any


class GraphAlgoTarjanScc:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-08
      name: GraphAlgoTarjanScc
      version: 1.0.0
      category: graph
      capability_tags: [graph, components, scc, tarjan, strongly_connected_components]
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
        required: [sccs, scc_count]
        properties:
          sccs:
            type: array
            items:
              type: array
              items: {type: string}
          scc_count: {type: integer}
      parameters: {}
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
        - output.scc_count >= 0
      compatible_adapters:
        - ADAPTER-GRAPH-TO-SCC
    ---
    """

    @staticmethod
    def find_sccs(adjacency_list: Dict[str, List[str]]) -> Dict[str, Any]:
        nodes = set(adjacency_list.keys())
        for targets in adjacency_list.values():
            nodes.update(targets)

        index = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        on_stack: Set[str] = set()
        stack: List[str] = []
        sccs: List[List[str]] = []

        def strongconnect(v: str) -> None:
            nonlocal index
            indices[v] = index
            lowlinks[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)

            for w in adjacency_list.get(v, []):
                if w not in indices:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])

            if lowlinks[v] == indices[v]:
                scc: List[str] = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(sorted(scc))

        for node in sorted(nodes):
            if node not in indices:
                strongconnect(node)

        sccs.sort(key=lambda s: (-len(s), s[0] if s else ""))

        return {
            "sccs": sccs,
            "scc_count": len(sccs),
            "node_count": len(nodes),
        }
