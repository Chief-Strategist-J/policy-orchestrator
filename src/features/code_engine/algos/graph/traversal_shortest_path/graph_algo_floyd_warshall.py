"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FLOYD-WARSHALL ALL-PAIRS (ALGO-GRAPH-PATH-29)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes all-pairs shortest path distances and paths for dense graphs using
   dynamic programming over intermediate vertices k in [1..V]. Maintains a
   predecessor matrix next[i][j] for O(path_length) path reconstructions and
   flags negative-weight cycles if dist[i][i] < 0.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^3) cubic dynamic programming.
   - Space Complexity: O(V^2) for distance and predecessor matrices.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoFloydWarshall(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PATH-29
      name: GraphAlgoFloydWarshall
      version: 1.0.0
      category: graph_shortest_path
      capability_tags: [graph, shortest_path, all_pairs, floyd_warshall, dynamic_programming]
      inputs:
        type: object
        required: [nodes, edges]
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
      outputs:
        type: object
        required: [distance_matrix, node_order, has_negative_cycle]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^3)
        space: O(V^2)
    ---
    """

    @staticmethod
    def compute(
        nodes: List[str],
        edges: List[Dict[str, Any]],
        directed: bool = True,
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        n = len(all_nodes)
        node_to_idx = {node: i for i, node in enumerate(all_nodes)}

        dist = [[float("inf")] * n for _ in range(n)]
        nxt = [[-1] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0.0
            nxt[i][i] = i

        for e in edges:
            src = str(e["source"])
            tgt = str(e["target"])
            wt = float(e["weight"])
            if src in node_to_idx and tgt in node_to_idx:
                u = node_to_idx[src]
                v = node_to_idx[tgt]
                if wt < dist[u][v]:
                    dist[u][v] = wt
                    nxt[u][v] = v
                if not directed and wt < dist[v][u]:
                    dist[v][u] = wt
                    nxt[v][u] = u

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] != float("inf") and dist[k][j] != float("inf"):
                        if dist[i][k] + dist[k][j] < dist[i][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            nxt[i][j] = nxt[i][k]

        has_negative_cycle = any(dist[i][i] < 0 for i in range(n))

        formatted_dist: Dict[str, Dict[str, float]] = {}
        for i, u in enumerate(all_nodes):
            formatted_dist[u] = {}
            for j, v in enumerate(all_nodes):
                if dist[i][j] != float("inf"):
                    formatted_dist[u][v] = dist[i][j]

        return {
            "distance_matrix": formatted_dist,
            "raw_matrix": dist,
            "next_matrix": nxt,
            "node_order": all_nodes,
            "node_to_index": node_to_idx,
            "has_negative_cycle": has_negative_cycle,
        }

    @staticmethod
    def reconstruct_path(
        result_model: Dict[str, Any],
        start_node: str,
        target_node: str,
    ) -> List[str]:
        node_to_idx = result_model["node_to_index"]
        all_nodes = result_model["node_order"]
        nxt = result_model["next_matrix"]

        if start_node not in node_to_idx or target_node not in node_to_idx:
            return []

        u = node_to_idx[start_node]
        v = node_to_idx[target_node]

        if nxt[u][v] == -1:
            return []

        path = [start_node]
        curr = u
        visited_indices = {curr}

        while curr != v:
            curr = nxt[curr][v]
            if curr in visited_indices or curr == -1:
                break
            visited_indices.add(curr)
            path.append(all_nodes[curr])

        return path
