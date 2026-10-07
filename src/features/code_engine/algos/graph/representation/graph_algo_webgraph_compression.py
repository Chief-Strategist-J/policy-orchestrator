"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: WEBGRAPH BV-CODING COMPRESSION (ALGO-GRAPH-REP-06)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements Boldi-Vigna (BV) WebGraph compression exploiting structural
   locality and similarity in graph adjacency lists. Employs:
   - Reference compression (copying neighbor list prefixes from reference vertices).
   - Consecutive intervals run-length encoding.
   - Residual gap difference compression using variable-length delta encoding.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * max_window * max_deg) compression, O(degree) decompression.
   - Space Complexity: O(compressed_bits) compact storage (< 3-5 bits/edge on sparse graphs).
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder.
   - Preconditions: Graph vertices indexed by dense integers [0..n-1].
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoWebGraphCompression(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-06
      name: GraphAlgoWebGraphCompression
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, webgraph, bv_compression, succinct_encoding]
      inputs:
        type: object
        required: [adjacency_list]
        properties:
          adjacency_list:
            type: object
            additionalProperties:
              type: array
              items: {type: integer}
      outputs:
        type: object
        required: [compressed_nodes, total_original_edges, compression_ratio]
      parameters:
        window_size: {type: integer, default: 7}
        min_interval_length: {type: integer, default: 3}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * window * degree)
        space: O(V + E)
    ---
    """

    @staticmethod
    def compress(
        adjacency_list: Dict[int, List[int]],
        window_size: int = 7,
        min_interval_length: int = 3,
    ) -> Dict[str, Any]:
        num_nodes = len(adjacency_list)
        sorted_adj: Dict[int, List[int]] = {
            u: sorted(list(set(neighbors)))
            for u, neighbors in adjacency_list.items()
        }

        compressed_records: Dict[int, Dict[str, Any]] = {}
        total_edges = 0

        for u in range(num_nodes):
            curr_list = sorted_adj.get(u, [])
            total_edges += len(curr_list)

            best_ref = -1
            best_copied: List[int] = []
            best_residuals: List[int] = curr_list

            for ref in range(max(0, u - window_size), u):
                ref_list = sorted_adj.get(ref, [])
                copied = [v for v in ref_list if v in curr_list]
                if len(copied) > len(best_copied):
                    best_ref = ref
                    best_copied = copied
                    copied_set = set(copied)
                    best_residuals = [v for v in curr_list if v not in copied_set]

            intervals, remaining = GraphAlgoWebGraphCompression._extract_intervals(
                best_residuals, min_interval_length
            )
            gaps = GraphAlgoWebGraphCompression._encode_gaps(remaining, u)

            compressed_records[u] = {
                "out_degree": len(curr_list),
                "reference_offset": (u - best_ref) if best_ref != -1 else 0,
                "copied_count": len(best_copied),
                "intervals": intervals,
                "residual_gaps": gaps,
            }

        return {
            "compressed_nodes": compressed_records,
            "num_nodes": num_nodes,
            "total_original_edges": total_edges,
            "window_size": window_size,
        }

    @staticmethod
    def decompress(
        compressed_records: Dict[int, Dict[str, Any]],
    ) -> Dict[int, List[int]]:
        num_nodes = len(compressed_records)
        decompressed: Dict[int, List[int]] = {}

        for u in range(num_nodes):
            rec = compressed_records[u]
            ref_offset = rec["reference_offset"]
            copied_neighbors: List[int] = []

            if ref_offset > 0:
                ref_node = u - ref_offset
                if ref_node in decompressed:
                    copied_neighbors = decompressed[ref_node][: rec["copied_count"]]

            interval_neighbors: List[int] = []
            for start, length in rec["intervals"]:
                interval_neighbors.extend(range(start, start + length))

            residual_neighbors = GraphAlgoWebGraphCompression._decode_gaps(
                rec["residual_gaps"], u
            )

            all_neighbors = sorted(
                list(set(copied_neighbors + interval_neighbors + residual_neighbors))
            )
            decompressed[u] = all_neighbors

        return decompressed

    @staticmethod
    def _extract_intervals(
        nodes: List[int], min_len: int
    ) -> Tuple[List[Tuple[int, int]], List[int]]:
        if not nodes:
            return [], []

        intervals: List[Tuple[int, int]] = []
        residuals: List[int] = []
        i = 0
        n = len(nodes)

        while i < n:
            start = nodes[i]
            length = 1
            while i + length < n and nodes[i + length] == start + length:
                length += 1

            if length >= min_len:
                intervals.append((start, length))
                i += length
            else:
                residuals.append(nodes[i])
                i += 1

        return intervals, residuals

    @staticmethod
    def _encode_gaps(nodes: List[int], source_node: int) -> List[int]:
        if not nodes:
            return []
        gaps: List[int] = []
        prev = source_node
        for v in nodes:
            gaps.append(v - prev)
            prev = v
        return gaps

    @staticmethod
    def _decode_gaps(gaps: List[int], source_node: int) -> List[int]:
        nodes: List[int] = []
        curr = source_node
        for g in gaps:
            curr += g
            nodes.append(curr)
        return nodes
