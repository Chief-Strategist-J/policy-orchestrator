"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SUBGRAPH ISOMORPHISM PATTERN MATCH (ALGO-GRAPH-09)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Subgraph pattern matching (VF2 / backtracking state-space exploration) to identify
   all structure-preserving mappings from pattern graph query into target host graph.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^k) where k is pattern size (NP-complete general, fast with state pruning).
   - Space Complexity: O(V_target)
   - Pure, deterministic, zero side effects.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Set, Any


class GraphAlgoSubgraphIsomorphism:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-09
      name: GraphAlgoSubgraphIsomorphism
      version: 1.0.0
      category: graph
      capability_tags: [graph, pattern_matching, vf2, subgraph_isomorphism, graph_query]
      inputs:
        type: object
        required: [target_graph, pattern_graph]
        properties:
          target_graph:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          pattern_graph:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [matches, match_count]
        properties:
          matches:
            type: array
            items:
              type: object
              additionalProperties: {type: string}
          match_count: {type: integer}
      parameters:
        max_matches: {type: integer, default: 100}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(V_target ^ V_pattern)
        space: O(V_target)
      preconditions:
        - len(input.pattern_graph) > 0
      postconditions:
        - output.match_count >= 0
      compatible_adapters:
        - ADAPTER-GRAPH-TO-SUBGRAPH-MATCHES
    ---
    """

    @staticmethod
    def match(
        target_graph: Dict[str, List[str]],
        pattern_graph: Dict[str, List[str]],
        max_matches: int = 100,
    ) -> Dict[str, Any]:
        pattern_nodes = sorted(pattern_graph.keys())
        target_nodes = sorted(
            set(target_graph.keys()).union(
                {v for tg in target_graph.values() for v in tg}
            )
        )

        matches: List[Dict[str, str]] = []

        def backtrack(
            idx: int,
            mapping: Dict[str, str],
            used_targets: Set[str],
        ) -> None:
            if len(matches) >= max_matches:
                return

            if idx == len(pattern_nodes):
                matches.append(dict(mapping))
                return

            p_node = pattern_nodes[idx]
            p_neighbors = set(pattern_graph.get(p_node, []))

            for t_node in target_nodes:
                if t_node in used_targets:
                    continue

                t_neighbors = set(target_graph.get(t_node, []))
                if len(t_neighbors) < len(p_neighbors):
                    continue

                valid = True
                for prev_p, prev_t in mapping.items():
                    if prev_p in p_neighbors and prev_t not in t_neighbors:
                        valid = False
                        break
                    if p_node in set(pattern_graph.get(prev_p, [])) and t_node not in set(target_graph.get(prev_t, [])):
                        valid = False
                        break

                if valid:
                    mapping[p_node] = t_node
                    used_targets.add(t_node)
                    backtrack(idx + 1, mapping, used_targets)
                    del mapping[p_node]
                    used_targets.remove(t_node)

        backtrack(0, {}, set())

        return {
            "matches": matches,
            "match_count": len(matches),
            "pattern_node_count": len(pattern_nodes),
            "target_node_count": len(target_nodes),
        }
