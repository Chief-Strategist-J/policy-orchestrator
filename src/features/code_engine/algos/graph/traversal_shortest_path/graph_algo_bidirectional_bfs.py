"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BIDIRECTIONAL BFS (ALGO-GRAPH-TRV-20)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Bidirectional Breadth-First Search concurrently expands forward frontiers
   from the source and backward frontiers from the destination until wavefronts
   intersect. Reduces search space exploration from O(b^d) to O(2 * b^(d/2)),
   achieving exponential speedups on point-to-point unweighted reachability queries.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(b^(d/2)) where b is average branching factor and d is path length.
   - Space Complexity: O(b^(d/2)) for dual frontier queues.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Any, Set, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoBidirectionalBfs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-20
      name: GraphAlgoBidirectionalBfs
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, bidirectional_bfs, point_to_point, shortest_path]
      inputs:
        type: object
        required: [forward_adjacency, backward_adjacency, start_node, target_node]
        properties:
          forward_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          backward_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          start_node: {type: string}
          target_node: {type: string}
      outputs:
        type: object
        required: [found, path, distance, nodes_visited]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(b^(d/2))
        space: O(b^(d/2))
    ---
    """

    @staticmethod
    def search(
        forward_adjacency: Dict[str, List[str]],
        backward_adjacency: Dict[str, List[str]],
        start_node: str,
        target_node: str,
    ) -> Dict[str, Any]:
        if start_node == target_node:
            return {
                "found": True,
                "path": [start_node],
                "distance": 0,
                "meeting_node": start_node,
                "nodes_visited": 1,
            }

        q_fwd: deque[str] = deque([start_node])
        q_bwd: deque[str] = deque([target_node])

        parent_fwd: Dict[str, Optional[str]] = {start_node: None}
        parent_bwd: Dict[str, Optional[str]] = {target_node: None}

        dist_fwd: Dict[str, int] = {start_node: 0}
        dist_bwd: Dict[str, int] = {target_node: 0}

        meeting_node: Optional[str] = None
        visited_count = 0

        while q_fwd and q_bwd:
            if len(q_fwd) <= len(q_bwd):
                curr = q_fwd.popleft()
                visited_count += 1
                curr_dist = dist_fwd[curr]

                for nxt in forward_adjacency.get(curr, []):
                    if nxt not in dist_fwd:
                        dist_fwd[nxt] = curr_dist + 1
                        parent_fwd[nxt] = curr
                        q_fwd.append(nxt)

                    if nxt in dist_bwd:
                        meeting_node = nxt
                        break
            else:
                curr = q_bwd.popleft()
                visited_count += 1
                curr_dist = dist_bwd[curr]

                for prev in backward_adjacency.get(curr, []):
                    if prev not in dist_bwd:
                        dist_bwd[prev] = curr_dist + 1
                        parent_bwd[prev] = curr
                        q_bwd.append(prev)

                    if prev in dist_fwd:
                        meeting_node = prev
                        break

            if meeting_node is not None:
                break

        if meeting_node is None:
            return {
                "found": False,
                "path": [],
                "distance": -1,
                "meeting_node": None,
                "nodes_visited": visited_count,
            }

        path_fwd: List[str] = []
        curr_f = meeting_node
        while curr_f is not None:
            path_fwd.append(curr_f)
            curr_f = parent_fwd[curr_f]
        path_fwd = path_fwd[::-1]

        path_bwd: List[str] = []
        curr_b = parent_bwd[meeting_node]
        while curr_b is not None:
            path_bwd.append(curr_b)
            curr_b = parent_bwd[curr_b]

        full_path = path_fwd + path_bwd
        total_dist = dist_fwd[meeting_node] + dist_bwd[meeting_node]

        return {
            "found": True,
            "path": full_path,
            "distance": total_dist,
            "meeting_node": meeting_node,
            "nodes_visited": visited_count,
        }
