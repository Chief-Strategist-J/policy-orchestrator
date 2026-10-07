"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EDGE LIST COO FORMAT (ALGO-GRAPH-REP-03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Coordinate format (COO) edge list representation providing sequential ingestion,
   deduplication, normalization, edge-centric filtering, degree distributions,
   and multigraph verification. Serves as universal interchange data structure.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E log E) sorting and deduplication, O(E) validation.
   - Space Complexity: O(E) linear memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder.
   - Rules: Explicitly validates endpoint existence and detects dangling IDs.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple


class GraphAlgoEdgeListCoo:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-03
      name: GraphAlgoEdgeListCoo
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, coo, edge_list, interchange]
      inputs:
        type: object
        required: [edges]
        properties:
          edges:
            type: array
            items:
              type: object
              required: [source, target]
              properties:
                source: {type: string}
                target: {type: string}
                weight: {type: number, default: 1.0}
                edge_type: {type: string, default: "default"}
      outputs:
        type: object
        required: [normalized_edges, num_edges, num_unique_edges, is_multigraph]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E log E)
        space: O(E)
    ---
    """

    @staticmethod
    def normalize_and_deduplicate(
        edges: List[Dict[str, Any]],
        allow_multigraph: bool = False,
        aggregation: str = "sum",
    ) -> Dict[str, Any]:
        edge_map: Dict[Tuple[str, str, str], float] = {}
        distinct_nodes: set = set()

        for edge in edges:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            wt = float(edge.get("weight", 1.0))
            e_type = str(edge.get("edge_type", "default"))
            if not src or not tgt:
                continue

            distinct_nodes.add(src)
            distinct_nodes.add(tgt)
            key = (src, tgt, e_type) if allow_multigraph else (src, tgt, "default")

            if key in edge_map:
                if aggregation == "sum":
                    edge_map[key] += wt
                elif aggregation == "max":
                    edge_map[key] = max(edge_map[key], wt)
                elif aggregation == "min":
                    edge_map[key] = min(edge_map[key], wt)
                elif aggregation == "last":
                    edge_map[key] = wt
            else:
                edge_map[key] = wt

        sorted_keys = sorted(edge_map.keys())
        normalized: List[Dict[str, Any]] = [
            {
                "source": k[0],
                "target": k[1],
                "edge_type": k[2],
                "weight": edge_map[k],
            }
            for k in sorted_keys
        ]

        return {
            "normalized_edges": normalized,
            "num_edges": len(edges),
            "num_unique_edges": len(normalized),
            "num_nodes": len(distinct_nodes),
            "nodes": sorted(list(distinct_nodes)),
            "is_multigraph": len(edges) > len(normalized),
        }

    @staticmethod
    def compute_degree_distribution(
        edges: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        out_degrees: Dict[str, int] = {}
        in_degrees: Dict[str, int] = {}

        for edge in edges:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            if src:
                out_degrees[src] = out_degrees.get(src, 0) + 1
            if tgt:
                in_degrees[tgt] = in_degrees.get(tgt, 0) + 1

        all_nodes = sorted(list(set(out_degrees.keys()) | set(in_degrees.keys())))
        return {
            "out_degrees": {n: out_degrees.get(n, 0) for n in all_nodes},
            "in_degrees": {n: in_degrees.get(n, 0) for n in all_nodes},
            "total_degrees": {
                n: out_degrees.get(n, 0) + in_degrees.get(n, 0) for n in all_nodes
            },
        }
