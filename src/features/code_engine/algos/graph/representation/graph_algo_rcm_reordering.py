"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REVERSE CUTHILL-MCKEE (RCM) REORDERING (ALGO-GRAPH-REP-09)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates graph vertex permutations to minimize adjacency matrix bandwidth
   and profile using Reverse Cuthill-McKee (RCM) and degree-sorting heuristics.
   Significantly improves CPU L1/L2/L3 cache locality and SIMD vectorization
   during downstream graph traversals, PageRank, and GNN message-passing.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V log V + E) for RCM BFS traversal and sorting.
   - Space Complexity: O(V + E) for permutation arrays and visited sets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Always returns bijective permutation and inverse mappings.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar, Set

NodeId = TypeVar("NodeId")


class GraphAlgoRcmReordering(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-09
      name: GraphAlgoRcmReordering
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, rcm, bandwidth_reduction, cache_locality]
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
        required: [permutation, original_bandwidth, optimized_bandwidth, bandwidth_reduction_ratio]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V log V + E)
        space: O(V + E)
    ---
    """

    @staticmethod
    def reorder(
        adjacency_list: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(adjacency_list.keys()))
        if not all_nodes:
            return {
                "permutation": [],
                "inverse_permutation": {},
                "original_bandwidth": 0,
                "optimized_bandwidth": 0,
                "bandwidth_reduction_ratio": 1.0,
            }

        degrees = {node: len(adjacency_list.get(node, [])) for node in all_nodes}
        visited: Set[str] = set()
        ordering: List[str] = []

        unvisited_nodes = sorted(all_nodes, key=lambda n: (degrees[n], n))

        for root in unvisited_nodes:
            if root in visited:
                continue

            queue: deque[str] = deque([root])
            visited.add(root)
            component_order: List[str] = []

            while queue:
                curr = queue.popleft()
                component_order.append(curr)

                neighbors = adjacency_list.get(curr, [])
                unvisited_neighbors = [nb for nb in neighbors if nb not in visited]
                unvisited_neighbors.sort(key=lambda nb: (degrees.get(nb, 0), nb))

                for nb in unvisited_neighbors:
                    visited.add(nb)
                    queue.append(nb)

            ordering.extend(component_order)

        rcm_order = ordering[::-1]
        inv_order = {node: i for i, node in enumerate(rcm_order)}
        orig_order = {node: i for i, node in enumerate(all_nodes)}

        orig_bw = GraphAlgoRcmReordering._calculate_bandwidth(adjacency_list, orig_order)
        opt_bw = GraphAlgoRcmReordering._calculate_bandwidth(adjacency_list, inv_order)

        reduction = (orig_bw - opt_bw) / max(orig_bw, 1) if orig_bw > 0 else 0.0

        return {
            "permutation": rcm_order,
            "inverse_permutation": inv_order,
            "original_bandwidth": orig_bw,
            "optimized_bandwidth": opt_bw,
            "bandwidth_reduction_ratio": reduction,
            "num_nodes": len(all_nodes),
        }

    @staticmethod
    def _calculate_bandwidth(
        adj: Dict[str, List[str]],
        order_map: Dict[str, int],
    ) -> int:
        max_bw = 0
        for u, neighbors in adj.items():
            if u not in order_map:
                continue
            u_pos = order_map[u]
            for v in neighbors:
                if v in order_map:
                    v_pos = order_map[v]
                    max_bw = max(max_bw, abs(u_pos - v_pos))
        return max_bw
