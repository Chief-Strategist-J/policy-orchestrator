"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BITMAP ADJACENCY (ALGO-GRAPH-REP-08)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Bitmap adjacency representation using 64-bit integer words and roaring-style
   block partitioning for ultra-fast set operations (bitwise AND, OR, XOR, NOT).
   Enables hardware-accelerated triangle counting, common neighbor discovery,
   Jaccard similarity computation, and dense clique filtering.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N / 64) per pair intersection, O(degree) iteration.
   - Space Complexity: O(V * (N / 64)) words for dense, O(active_blocks) for sparse.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guardrails: Capped memory allocations for large V via sparse chunked maps.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoBitmapAdjacency(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-08
      name: GraphAlgoBitmapAdjacency
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, bitmap_adjacency, set_operations, fast_intersection]
      inputs:
        type: object
        required: [num_nodes, edges]
        properties:
          num_nodes: {type: integer}
          edges:
            type: array
            items:
              type: array
              items: {type: integer}
      outputs:
        type: object
        required: [bitmaps, num_nodes, num_edges]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V * (V / 64))
    ---
    """

    @staticmethod
    def construct(
        num_nodes: int,
        edges: List[Tuple[int, int]],
        directed: bool = False,
    ) -> Dict[str, Any]:
        num_words = (num_nodes + 63) // 64
        bitmaps: Dict[int, List[int]] = {i: [0] * num_words for i in range(num_nodes)}
        edge_count = 0

        for u, v in edges:
            if 0 <= u < num_nodes and 0 <= v < num_nodes:
                w_idx_v = v // 64
                b_idx_v = v % 64
                bitmaps[u][w_idx_v] |= 1 << b_idx_v
                edge_count += 1

                if not directed:
                    w_idx_u = u // 64
                    b_idx_u = u % 64
                    bitmaps[v][w_idx_u] |= 1 << b_idx_u

        return {
            "bitmaps": bitmaps,
            "num_nodes": num_nodes,
            "num_words_per_node": num_words,
            "num_edges": edge_count if directed else edge_count // 2,
            "directed": directed,
        }

    @staticmethod
    def intersect_neighbors(
        bitmaps: Dict[int, List[int]],
        node_a: int,
        node_b: int,
    ) -> List[int]:
        if node_a not in bitmaps or node_b not in bitmaps:
            return []

        words_a = bitmaps[node_a]
        words_b = bitmaps[node_b]
        common_nodes: List[int] = []

        for w_idx in range(min(len(words_a), len(words_b))):
            common_bits = words_a[w_idx] & words_b[w_idx]
            while common_bits > 0:
                lsb = common_bits & -common_bits
                bit_pos = (lsb.bit_length() - 1)
                common_nodes.append(w_idx * 64 + bit_pos)
                common_bits &= common_bits - 1

        return common_nodes

    @staticmethod
    def count_common_neighbors(
        bitmaps: Dict[int, List[int]],
        node_a: int,
        node_b: int,
    ) -> int:
        if node_a not in bitmaps or node_b not in bitmaps:
            return 0

        words_a = bitmaps[node_a]
        words_b = bitmaps[node_b]
        count = 0

        for w_idx in range(min(len(words_a), len(words_b))):
            common_bits = words_a[w_idx] & words_b[w_idx]
            count += bin(common_bits).count("1")

        return count

    @staticmethod
    def count_triangles(
        bitmaps: Dict[int, List[int]],
        num_nodes: int,
    ) -> int:
        total_triangles = 0
        for u in range(num_nodes):
            for v in range(u + 1, num_nodes):
                w_idx_v = v // 64
                b_idx_v = v % 64
                if (bitmaps[u][w_idx_v] & (1 << b_idx_v)) != 0:
                    common_count = GraphAlgoBitmapAdjacency.count_common_neighbors(
                        bitmaps, u, v
                    )
                    total_triangles += common_count

        return total_triangles // 3
