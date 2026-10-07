"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BELLMAN-FORD-MOORE & SPFA (ALGO-GRAPH-PATH-27)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes single-source shortest paths on graphs with arbitrary real edge
   weights (including negative edge weights). Incorporates the Shortest Path
   Faster Algorithm (SPFA) queue optimization to achieve O(k * E) average time,
   and identifies negative-weight cycles with full cycle path reconstruction.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E) worst case, O(E) average with SPFA.
   - Space Complexity: O(V) for distance table and relaxation counters.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Verifier.
   - Guarantees: Reconstructs exact negative cycles on infeasibility.
================================================================================
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoBellmanFordMoore(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PATH-27
      name: GraphAlgoBellmanFordMoore
      version: 1.0.0
      category: graph_shortest_path
      capability_tags: [graph, shortest_path, bellman_ford, spfa, negative_cycles]
      inputs:
        type: object
        required: [nodes, edges, start_node]
        properties:
          nodes:
            type: array
            items: {type: string}
          edges:
            type: array
            items:
              type: object
              required: [source, target, weight]
              properties:
                source: {type: string}
                target: {type: string}
                weight: {type: number}
          start_node: {type: string}
      outputs:
        type: object
        required: [distances, parents, has_negative_cycle, negative_cycle]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * E)
        space: O(V)
    ---
    """

    @staticmethod
    def compute(
        nodes: List[str],
        edges: List[Dict[str, Any]],
        start_node: str,
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        n = len(all_nodes)
        distances: Dict[str, float] = {node: float("inf") for node in all_nodes}
        parents: Dict[str, Optional[str]] = {node: None for node in all_nodes}

        adj: Dict[str, List[Tuple[str, float]]] = {node: [] for node in all_nodes}
        for edge in edges:
            src = str(edge["source"])
            tgt = str(edge["target"])
            wt = float(edge["weight"])
            if src in adj and tgt in distances:
                adj[src].append((tgt, wt))

        distances[start_node] = 0.0
        in_queue: Dict[str, bool] = {node: False for node in all_nodes}
        relax_count: Dict[str, int] = {node: 0 for node in all_nodes}

        queue: deque[str] = deque([start_node])
        in_queue[start_node] = True
        relax_count[start_node] = 1

        has_negative_cycle = False
        cycle_node: Optional[str] = None

        while queue:
            curr = queue.popleft()
            in_queue[curr] = False
            curr_dist = distances[curr]

            for neighbor, weight in adj.get(curr, []):
                if curr_dist + weight < distances[neighbor]:
                    distances[neighbor] = curr_dist + weight
                    parents[neighbor] = curr

                    if not in_queue[neighbor]:
                        queue.append(neighbor)
                        in_queue[neighbor] = True
                        relax_count[neighbor] += 1

                        if relax_count[neighbor] >= n:
                            has_negative_cycle = True
                            cycle_node = neighbor
                            break

            if has_negative_cycle:
                break

        negative_cycle: List[str] = []
        if has_negative_cycle and cycle_node is not None:
            curr_c = cycle_node
            for _ in range(n):
                if curr_c in parents and parents[curr_c] is not None:
                    curr_c = parents[curr_c]

            cycle_start = curr_c
            negative_cycle.append(cycle_start)
            curr_c = parents[cycle_start]
            while curr_c != cycle_start and curr_c is not None and len(negative_cycle) <= n + 1:
                negative_cycle.append(curr_c)
                curr_c = parents.get(curr_c)
            negative_cycle.append(cycle_start)
            negative_cycle = negative_cycle[::-1]

        valid_dist = {k: v for k, v in distances.items() if v != float("inf")}

        return {
            "distances": valid_dist,
            "parents": {k: v for k, v in parents.items() if distances.get(k, float("inf")) != float("inf")},
            "has_negative_cycle": has_negative_cycle,
            "negative_cycle": negative_cycle,
            "total_nodes": n,
        }
