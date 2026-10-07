"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DIAL'S SHORTEST PATH (ALGO-GRAPH-TRV-22)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dial's algorithm (bucket priority queue implementation of Dijkstra) computes
   exact single-source shortest paths on graphs with small maximum edge weight W.
   Uses an array of circular buckets of size (W + 1), achieving O(E + W * V)
   time complexity without logarithmic comparison heap overhead.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E + W * V) deterministic bucket scanning.
   - Space Complexity: O(V + W) bucket memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: All edge weights must be non-negative integers bounded by W.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar, Set

NodeId = TypeVar("NodeId")


class GraphAlgoDialsShortestPath(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-22
      name: GraphAlgoDialsShortestPath
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, dials_algorithm, bucket_queue, integer_weights]
      inputs:
        type: object
        required: [weighted_adjacency, start_node]
        properties:
          weighted_adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: object
                required: [target, weight]
                properties:
                  target: {type: string}
                  weight: {type: integer}
          start_node: {type: string}
      outputs:
        type: object
        required: [distances, parents, max_edge_weight]
      parameters:
        max_edge_weight: {type: integer, default: 100}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E + W * V)
        space: O(V + W)
    ---
    """

    @staticmethod
    def compute(
        weighted_adjacency: Dict[str, List[Dict[str, Any]]],
        start_node: str,
        max_edge_weight: int = 100,
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(weighted_adjacency.keys()))
        if start_node not in all_nodes:
            all_nodes.append(start_node)

        max_w = 1
        for edges in weighted_adjacency.values():
            for e in edges:
                wt = int(e.get("weight", 1))
                if wt > max_w:
                    max_w = wt

        num_buckets = max_w * len(all_nodes) + 1
        buckets: List[Set[str]] = [set() for _ in range(num_buckets)]

        distances: Dict[str, int] = {n: -1 for n in all_nodes}
        parents: Dict[str, Optional[str]] = {n: None for n in all_nodes}

        distances[start_node] = 0
        buckets[0].add(start_node)

        idx = 0
        remaining_nodes = len(all_nodes)

        while idx < num_buckets and remaining_nodes > 0:
            while idx < num_buckets and not buckets[idx]:
                idx += 1

            if idx >= num_buckets:
                break

            curr = buckets[idx].pop()
            if distances[curr] < idx:
                continue

            remaining_nodes -= 1

            for edge in weighted_adjacency.get(curr, []):
                tgt = str(edge["target"])
                wt = max(0, int(edge.get("weight", 1)))
                old_dist = distances.get(tgt, -1)
                new_dist = idx + wt

                if old_dist == -1 or new_dist < old_dist:
                    if old_dist != -1 and old_dist < num_buckets:
                        buckets[old_dist].discard(tgt)
                    distances[tgt] = new_dist
                    parents[tgt] = curr
                    if new_dist < num_buckets:
                        buckets[new_dist].add(tgt)

        valid_distances = {k: v for k, v in distances.items() if v != -1}

        return {
            "distances": valid_distances,
            "parents": {k: v for k, v in parents.items() if distances[k] != -1},
            "max_edge_weight": max_w,
            "total_reachable": len(valid_distances),
        }
