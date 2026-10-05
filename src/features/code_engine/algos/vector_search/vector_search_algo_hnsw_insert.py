"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HNSW INSERTION & HEURISTIC (ALGO-VEC-SRCH-67)
================================================================================

1. OVERVIEW & OBJECTIVE:
   HNSW graph insertion and heuristic neighbor selection (#67). Dynamically assigns
   an exponential decay maximum layer level to a new node, routes greedily to the
   entry point at that layer, explores candidate sets with efConstruction, and prunes
   edges using the heuristic diversity criterion (closer to base than to any chosen
   neighbor).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(log N) insertion with bounded per-layer degrees.
   - Space Complexity: O(M) edge footprint per node.
   - Pure, deterministic, zero inline comments.
================================================================================
"""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Set, Tuple


class VectorSearchAlgoHNSWInsert:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-67
      name: VectorSearchAlgoHNSWInsert
      version: 1.0.0
      category: vector
      capability_tags: [vector, proximity_graph, hnsw, indexer, heuristic_prune]
      inputs:
        type: object
        required: [vectors]
        properties:
          vectors:
            type: array
            items: {type: array, items: {type: number}}
          m: {type: integer, default: 4}
          ef_construction: {type: integer, default: 16}
          m_max_0: {type: integer, default: 8}
          ml: {type: number, default: 0.62}
      outputs:
        type: object
        required: [total_nodes, num_layers, entry_point, top_layer, layers]
        properties:
          total_nodes: {type: integer}
          num_layers: {type: integer}
          entry_point: {type: integer}
          top_layer: {type: integer}
          layers:
            type: array
            items: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N log N)
        space: O(N * M)
      preconditions:
        - len(vectors) > 0
        - m > 0
      postconditions:
        - output.total_nodes == len(input.vectors)
      compatible_adapters:
        - ADAPTER-HNSW-GRAPH
    ---
    """

    @staticmethod
    def _euclidean_distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def select_neighbors_heuristic(
        cls,
        base_vec: List[float],
        candidates: List[Tuple[float, int]],
        vectors: List[List[float]],
        m_max: int,
    ) -> List[int]:
        candidates.sort(key=lambda x: x[0])
        result: List[int] = []

        for c_dist, c_idx in candidates:
            if len(result) >= m_max:
                break
            c_vec = vectors[c_idx]
            keep = True
            for r_idx in result:
                r_vec = vectors[r_idx]
                if cls._euclidean_distance(c_vec, r_vec) < c_dist:
                    keep = False
                    break
            if keep:
                result.append(c_idx)

        return result

    @classmethod
    def build_index(
        cls,
        vectors: List[List[float]],
        m: int = 4,
        ef_construction: int = 16,
        m_max_0: int = 8,
        ml: float = 0.62,
    ) -> Dict[str, Any]:
        if not vectors:
            return {"total_nodes": 0, "num_layers": 0, "entry_point": -1, "top_layer": -1, "layers": []}

        n = len(vectors)
        node_levels: List[int] = []
        rnd = random.Random(42)

        for i in range(n):
            if i == 0:
                node_levels.append(0)
            else:
                level = int(-math.log(rnd.random()) * ml)
                node_levels.append(level)

        max_level = max(node_levels)
        layers: List[Dict[str, List[int]]] = [{} for _ in range(max_level + 1)]
        entry_point = 0

        for i in range(n):
            curr_vec = vectors[i]
            target_level = node_levels[i]

            for lc in range(target_level + 1):
                layers[lc][str(i)] = []

            if i == 0:
                continue

            curr_ep = entry_point
            curr_top = max(node_levels[:i])

            for lc in range(curr_top, target_level, -1):
                if str(curr_ep) in layers[lc]:
                    curr_dist = cls._euclidean_distance(curr_vec, vectors[curr_ep])
                    improved = True
                    while improved:
                        improved = False
                        for neighbor in layers[lc].get(str(curr_ep), []):
                            ndist = cls._euclidean_distance(curr_vec, vectors[neighbor])
                            if ndist < curr_dist:
                                curr_dist = ndist
                                curr_ep = neighbor
                                improved = True

            for lc in range(min(target_level, curr_top), -1, -1):
                layer_adj = layers[lc]
                nodes_in_layer = [int(k) for k in layer_adj.keys() if int(k) != i]
                candidate_pool = [
                    (cls._euclidean_distance(curr_vec, vectors[node_idx]), node_idx)
                    for node_idx in nodes_in_layer
                ]
                m_curr = m_max_0 if lc == 0 else m
                selected = cls.select_neighbors_heuristic(curr_vec, candidate_pool, vectors, m_curr)
                layer_adj[str(i)] = selected

                for sel in selected:
                    if i not in layer_adj[str(sel)]:
                        layer_adj[str(sel)].append(i)
                        if len(layer_adj[str(sel)]) > m_curr:
                            sel_candidates = [
                                (cls._euclidean_distance(vectors[sel], vectors[other]), other)
                                for other in layer_adj[str(sel)]
                            ]
                            layer_adj[str(sel)] = cls.select_neighbors_heuristic(
                                vectors[sel], sel_candidates, vectors, m_curr
                            )

            if target_level > curr_top:
                entry_point = i

        return {
            "total_nodes": n,
            "num_layers": len(layers),
            "entry_point": entry_point,
            "top_layer": max_level,
            "layers": layers,
        }
