"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EULER TOUR TECHNIQUE (ALGO-GRAPH-TRV-19)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Flattens hierarchical tree structures into linear traversal visit sequences.
   Maps every node's subtree to a contiguous subarray index interval [in[u], out[u]],
   enabling O(1) subtree query bounds, prefix-sum aggregations, and Range Minimum
   Query (RMQ) Lowest Common Ancestor (LCA) resolution.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V) linear DFS Euler tour construction.
   - Space Complexity: O(V) for tour sequence and entry/exit timestamps.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoEulerTourTree(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-19
      name: GraphAlgoEulerTourTree
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, euler_tour, tree_flattening, lca_range_query]
      inputs:
        type: object
        required: [tree_adjacency, root_node]
        properties:
          tree_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          root_node: {type: string}
      outputs:
        type: object
        required: [tour_sequence, depth_sequence, in_time, out_time, subtree_sizes]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V)
        space: O(V)
    ---
    """

    @staticmethod
    def construct(
        tree_adjacency: Dict[str, List[str]],
        root_node: str,
    ) -> Dict[str, Any]:
        tour_sequence: List[str] = []
        depth_sequence: List[int] = []
        in_time: Dict[str, int] = {}
        out_time: Dict[str, int] = {}
        subtree_sizes: Dict[str, int] = {}
        depths: Dict[str, int] = {root_node: 0}

        stack: List[Tuple[str, int, int]] = [(root_node, 0, 0)]
        in_time[root_node] = 0
        tour_sequence.append(root_node)
        depth_sequence.append(0)

        visited_nodes: set = {root_node}

        while stack:
            curr, child_idx, depth = stack[-1]
            children = tree_adjacency.get(curr, [])

            if child_idx < len(children):
                child = children[child_idx]
                stack[-1] = (curr, child_idx + 1, depth)

                if child not in visited_nodes:
                    visited_nodes.add(child)
                    depths[child] = depth + 1
                    in_time[child] = len(tour_sequence)
                    tour_sequence.append(child)
                    depth_sequence.append(depth + 1)
                    stack.append((child, 0, depth + 1))
            else:
                stack.pop()
                out_time[curr] = len(tour_sequence) - 1
                tour_sequence.append(curr)
                depth_sequence.append(depth)

        for node in in_time:
            first_in = in_time[node]
            last_out = out_time[node]
            distinct_in_range = len(set(tour_sequence[first_in : last_out + 1]))
            subtree_sizes[node] = distinct_in_range

        return {
            "tour_sequence": tour_sequence,
            "depth_sequence": depth_sequence,
            "in_time": in_time,
            "out_time": out_time,
            "depths": depths,
            "subtree_sizes": subtree_sizes,
            "tour_length": len(tour_sequence),
        }

    @staticmethod
    def query_lca(
        euler_model: Dict[str, Any],
        node_u: str,
        node_v: str,
    ) -> Optional[str]:
        in_time = euler_model["in_time"]
        tour = euler_model["tour_sequence"]
        depths = euler_model["depth_sequence"]

        if node_u not in in_time or node_v not in in_time:
            return None

        idx_u = in_time[node_u]
        idx_v = in_time[node_v]
        left = min(idx_u, idx_v)
        right = max(idx_u, idx_v)

        min_depth = float("inf")
        lca_node = None

        for k in range(left, right + 1):
            if depths[k] < min_depth:
                min_depth = depths[k]
                lca_node = tour[k]

        return lca_node
