"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: JOHNSON'S ALL-PAIRS SHORTEST PATHS (ALGO-GRAPH-PATH-28)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes all-pairs shortest paths on sparse graphs with arbitrary real edge
   weights. Constructs an augmented graph with a synthetic source, runs Bellman-Ford
   to compute node potentials h(u), reweights all edges to non-negative values
   w'(u, v) = w(u, v) + h(u) - h(v), and executes |V| independent Dijkstra passes.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E + V^2 * log V).
   - Space Complexity: O(V^2) all-pairs distance matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
   - Verifier: Detects negative cycles during the initial potential phase.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoJohnsonAllPairs(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PATH-28
      name: GraphAlgoJohnsonAllPairs
      version: 1.0.0
      category: graph_shortest_path
      capability_tags: [graph, shortest_path, all_pairs, johnsons_algorithm, potential_reweighting]
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
        required: [distances, has_negative_cycle, node_order]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * E + V^2 * log V)
        space: O(V^2)
    ---
    """

    @staticmethod
    def compute(
        nodes: List[str],
        edges: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(dict.fromkeys(nodes)))
        n = len(all_nodes)
        synthetic_source = "__synthetic_source__"

        augmented_nodes = all_nodes + [synthetic_source]
        augmented_edges = [
            {
                "source": str(e["source"]),
                "target": str(e["target"]),
                "weight": float(e["weight"]),
            }
            for e in edges
        ]

        for u in all_nodes:
            augmented_edges.append({"source": synthetic_source, "target": u, "weight": 0.0})

        h_dist: Dict[str, float] = {u: float("inf") for u in augmented_nodes}
        h_dist[synthetic_source] = 0.0

        for _ in range(len(augmented_nodes) - 1):
            for e in augmented_edges:
                u, v, w = e["source"], e["target"], e["weight"]
                if h_dist[u] != float("inf") and h_dist[u] + w < h_dist[v]:
                    h_dist[v] = h_dist[u] + w

        has_negative_cycle = False
        for e in augmented_edges:
            u, v, w = e["source"], e["target"], e["weight"]
            if h_dist[u] != float("inf") and h_dist[u] + w < h_dist[v]:
                has_negative_cycle = True
                break

        if has_negative_cycle:
            return {
                "distances": {},
                "has_negative_cycle": True,
                "node_order": all_nodes,
            }

        reweighted_adj: Dict[str, List[Tuple[str, float]]] = {u: [] for u in all_nodes}
        for e in edges:
            u = str(e["source"])
            v = str(e["target"])
            w = float(e["weight"])
            if u in h_dist and v in h_dist:
                w_hat = w + h_dist[u] - h_dist[v]
                reweighted_adj[u].append((v, max(0.0, w_hat)))

        all_pairs_dist: Dict[str, Dict[str, float]] = {}

        for u in all_nodes:
            dijkstra_dist: Dict[str, float] = {v: float("inf") for v in all_nodes}
            dijkstra_dist[u] = 0.0
            pq: List[Tuple[float, str]] = [(0.0, u)]

            while pq:
                d_curr, curr = heapq.heappop(pq)
                if d_curr > dijkstra_dist[curr]:
                    continue

                for v, w_hat in reweighted_adj.get(curr, []):
                    if dijkstra_dist[curr] + w_hat < dijkstra_dist[v]:
                        dijkstra_dist[v] = dijkstra_dist[curr] + w_hat
                        heapq.heappush(pq, (dijkstra_dist[v], v))

            all_pairs_dist[u] = {}
            for v in all_nodes:
                if dijkstra_dist[v] != float("inf"):
                    real_dist = dijkstra_dist[v] - h_dist[u] + h_dist[v]
                    all_pairs_dist[u][v] = round(real_dist, 6)

        return {
            "distances": all_pairs_dist,
            "has_negative_cycle": False,
            "node_order": all_nodes,
        }
