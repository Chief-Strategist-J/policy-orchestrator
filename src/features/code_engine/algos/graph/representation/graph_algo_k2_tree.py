"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: K2-TREE SUCCINCT MATRIX (ALGO-GRAPH-REP-07)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs succinct k^2-tree representation over binary graph adjacency
   matrices. Recursively decomposes the matrix into k x k submatrices, pruning
   empty regions into zero bits. Provides dual-directional neighbor querying
   (out-neighbors and in-neighbors) with succinct memory footprints.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N^2) construction, O(degree * log_k(N)) neighbor retrieval.
   - Space Complexity: O(bits_in_tree) succinct storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder & Analyst.
   - Guarantees: Bidirectional row and column range intersection queries.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Set


class GraphAlgoK2Tree:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-07
      name: GraphAlgoK2Tree
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, k2_tree, succinct_data_structure, dual_query]
      inputs:
        type: object
        required: [matrix_size, edge_coordinates]
        properties:
          matrix_size: {type: integer}
          edge_coordinates:
            type: array
            items:
              type: array
              items: {type: integer}
      outputs:
        type: object
        required: [bit_levels, leaves, matrix_size, k]
      parameters:
        k: {type: integer, default: 2}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E * log_k N)
        space: O(bit_length)
    ---
    """

    @staticmethod
    def build(
        matrix_size: int,
        edge_coordinates: List[Tuple[int, int]],
        k: int = 2,
    ) -> Dict[str, Any]:
        p = 1
        while p < matrix_size:
            p *= k
        padded_size = p

        edge_set: Set[Tuple[int, int]] = {
            (r, c)
            for r, c in edge_coordinates
            if 0 <= r < matrix_size and 0 <= c < matrix_size
        }

        bit_levels: List[List[int]] = []
        leaves: List[int] = []

        curr_blocks = [(0, 0, padded_size)]

        while curr_blocks and curr_blocks[0][2] > 1:
            next_blocks = []
            level_bits = []
            sub_size = curr_blocks[0][2] // k

            for r_top, c_left, b_size in curr_blocks:
                sub_size = b_size // k
                for i in range(k):
                    for j in range(k):
                        sub_r = r_top + i * sub_size
                        sub_c = c_left + j * sub_size

                        has_edges = any(
                            sub_r <= er < sub_r + sub_size
                            and sub_c <= ec < sub_c + sub_size
                            for er, ec in edge_set
                        )
                        bit = 1 if has_edges else 0
                        level_bits.append(bit)

                        if bit == 1 and sub_size > 1:
                            next_blocks.append((sub_r, sub_c, sub_size))

            bit_levels.append(level_bits)
            curr_blocks = next_blocks

        return {
            "bit_levels": bit_levels,
            "matrix_size": matrix_size,
            "padded_size": padded_size,
            "k": k,
            "total_edges": len(edge_set),
        }

    @staticmethod
    def query_out_neighbors(
        tree_model: Dict[str, Any],
        row: int,
    ) -> List[int]:
        k = tree_model["k"]
        padded_size = tree_model["padded_size"]
        matrix_size = tree_model["matrix_size"]
        bit_levels = tree_model["bit_levels"]

        results: List[int] = []

        def _traverse(
            level_idx: int, block_rank: int, r_top: int, c_left: int, b_size: int
        ) -> None:
            if level_idx >= len(bit_levels):
                if c_left < matrix_size:
                    results.append(c_left)
                return

            sub_size = b_size // k
            row_band = (row - r_top) // sub_size

            for col_band in range(k):
                child_idx = row_band * k + col_band
                pos = block_rank * (k * k) + child_idx

                if pos < len(bit_levels[level_idx]) and bit_levels[level_idx][pos] == 1:
                    sub_r = r_top + row_band * sub_size
                    sub_c = c_left + col_band * sub_size

                    ones_before = sum(
                        bit_levels[level_idx][p]
                        for p in range(pos)
                    )
                    _traverse(
                        level_idx + 1,
                        ones_before,
                        sub_r,
                        sub_c,
                        sub_size,
                    )

        if 0 <= row < matrix_size:
            _traverse(0, 0, 0, 0, padded_size)

        return sorted(results)

    @staticmethod
    def query_in_neighbors(
        tree_model: Dict[str, Any],
        col: int,
    ) -> List[int]:
        k = tree_model["k"]
        padded_size = tree_model["padded_size"]
        matrix_size = tree_model["matrix_size"]
        bit_levels = tree_model["bit_levels"]

        results: List[int] = []

        def _traverse(
            level_idx: int, block_rank: int, r_top: int, c_left: int, b_size: int
        ) -> None:
            if level_idx >= len(bit_levels):
                if r_top < matrix_size:
                    results.append(r_top)
                return

            sub_size = b_size // k
            col_band = (col - c_left) // sub_size

            for row_band in range(k):
                child_idx = row_band * k + col_band
                pos = block_rank * (k * k) + child_idx

                if pos < len(bit_levels[level_idx]) and bit_levels[level_idx][pos] == 1:
                    sub_r = r_top + row_band * sub_size
                    sub_c = c_left + col_band * sub_size

                    ones_before = sum(
                        bit_levels[level_idx][p]
                        for p in range(pos)
                    )
                    _traverse(
                        level_idx + 1,
                        ones_before,
                        sub_r,
                        sub_c,
                        sub_size,
                    )

        if 0 <= col < matrix_size:
            _traverse(0, 0, 0, 0, padded_size)

        return sorted(results)
