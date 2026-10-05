"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CONNECTED COMPONENTS UNION-FIND (ALGO-GRAPH-07)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Disjoint-set union (Union-Find) with path compression and union by rank
   to find connected components in undirected graphs in near-linear time.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E * alpha(V)) where alpha is inverse Ackermann.
   - Space Complexity: O(V)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Set, Any


class GraphAlgoConnectedComponents:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-07
      name: GraphAlgoConnectedComponents
      version: 1.0.0
      category: graph
      capability_tags: [graph, components, connected_components, union_find, disjoint_set]
      inputs:
        type: object
        required: [edges]
        properties:
          edges:
            type: array
            items:
              type: array
              items: {type: string}
          nodes:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [components, component_count]
        properties:
          components:
            type: array
            items:
              type: array
              items: {type: string}
          component_count: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(E * alpha(V))
        space: O(V)
      preconditions:
        - len(input.edges) >= 0
      postconditions:
        - output.component_count >= 0
      compatible_adapters:
        - ADAPTER-GRAPH-TO-COMPONENTS
    ---
    """

    @staticmethod
    def find_components(
        edges: List[List[str]],
        nodes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        all_nodes: Set[str] = set(nodes or [])
        for edge in edges:
            if len(edge) >= 2:
                all_nodes.add(edge[0])
                all_nodes.add(edge[1])

        parent: Dict[str, str] = {n: n for n in all_nodes}
        rank: Dict[str, int] = {n: 0 for n in all_nodes}

        def find(u: str) -> str:
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        def union(u: str, v: str) -> None:
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                if rank[root_u] < rank[root_v]:
                    root_u, root_v = root_v, root_u
                parent[root_v] = root_u
                if rank[root_u] == rank[root_v]:
                    rank[root_u] += 1

        for edge in edges:
            if len(edge) >= 2:
                union(edge[0], edge[1])

        comp_map: Dict[str, List[str]] = {}
        for n in all_nodes:
            root = find(n)
            if root not in comp_map:
                comp_map[root] = []
            comp_map[root].append(n)

        sorted_components = [sorted(members) for members in comp_map.values()]
        sorted_components.sort(key=lambda c: (-len(c), c[0] if c else ""))

        return {
            "components": sorted_components,
            "component_count": len(sorted_components),
            "node_count": len(all_nodes),
        }
