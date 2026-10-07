"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DIRECTION-OPTIMIZING BFS (ALGO-GRAPH-TRV-13)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Beamer's direction-optimizing breadth-first search dynamically switches
   between top-down frontier pushing (when frontier is small) and bottom-up
   unvisited scanning (when frontier is large). Skips substantial edge checks
   on low-diameter small-world and scale-free networks.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) worst case, O(m_active) average.
   - Space Complexity: O(V) for visited and parent arrays.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Adjacency must provide forward and backward neighbor access.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Set, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoDirectionOptimizingBfs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-13
      name: GraphAlgoDirectionOptimizingBfs
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, bfs, direction_optimizing, beamer_algorithm]
      inputs:
        type: object
        required: [nodes, out_adjacency, in_adjacency, start_node]
        properties:
          nodes:
            type: array
            items: {type: string}
          out_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          in_adjacency:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          start_node: {type: string}
      outputs:
        type: object
        required: [distances, parents, visited_count, level_sizes]
      parameters:
        alpha: {type: number, default: 14.0}
        beta: {type: number, default: 24.0}
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
        out_adjacency: Dict[str, List[str]],
        in_adjacency: Dict[str, List[str]],
        start_node: str,
        alpha: float = 14.0,
        beta: float = 24.0,
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        if start_node not in all_nodes:
            all_nodes.append(start_node)

        node_set = set(all_nodes)
        distances: Dict[str, int] = {n: -1 for n in all_nodes}
        parents: Dict[str, Optional[str]] = {n: None for n in all_nodes}

        distances[start_node] = 0
        frontier: Set[str] = {start_node}
        unvisited: Set[str] = set(all_nodes) - {start_node}

        level = 0
        level_sizes: List[int] = [1]

        while frontier:
            next_frontier: Set[str] = set()
            level += 1

            frontier_edges = sum(len(out_adjacency.get(u, [])) for u in frontier)
            unvisited_edges = sum(len(in_adjacency.get(v, [])) for v in unvisited)

            use_bottom_up = (
                len(frontier) > 0
                and frontier_edges > unvisited_edges / alpha
            )

            if use_bottom_up:
                discovered: List[str] = []
                for v in unvisited:
                    in_nbrs = in_adjacency.get(v, [])
                    for u in in_nbrs:
                        if u in frontier:
                            distances[v] = level
                            parents[v] = u
                            next_frontier.add(v)
                            discovered.append(v)
                            break

                for d in discovered:
                    unvisited.remove(d)
            else:
                for u in frontier:
                    for v in out_adjacency.get(u, []):
                        if distances[v] == -1 and v in unvisited:
                            distances[v] = level
                            parents[v] = u
                            next_frontier.add(v)
                            unvisited.discard(v)

            if next_frontier:
                level_sizes.append(len(next_frontier))
            frontier = next_frontier

        visited_nodes = [n for n in all_nodes if distances[n] != -1]

        return {
            "distances": {k: v for k, v in distances.items() if v != -1},
            "parents": {k: v for k, v in parents.items() if distances[k] != -1},
            "visited_count": len(visited_nodes),
            "max_depth": level - 1 if level > 0 else 0,
            "level_sizes": level_sizes,
        }
