"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MULTIGRAPH TYPED INDEX (ALGO-GRAPH-REP-11)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Indexes multi-relational property graphs by partitioning edges across
   relationship types and directions. Enables typed path traversals without
   scanning irrelevant edge types, preventing supernode traversal degradation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E) indexing, O(deg_type(v)) typed neighbor lookup.
   - Space Complexity: O(V + E) structured partition tables.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder & Analyst.
   - Guardrails: Provides per-type degree histograms for query planner cost estimation.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoMultigraphTypedIndex(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-11
      name: GraphAlgoMultigraphTypedIndex
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, multigraph, typed_index, property_graph]
      inputs:
        type: object
        required: [edges]
        properties:
          edges:
            type: array
            items:
              type: object
              required: [source, target, edge_type]
              properties:
                source: {type: string}
                target: {type: string}
                edge_type: {type: string}
                weight: {type: number, default: 1.0}
                properties: {type: object}
      outputs:
        type: object
        required: [typed_out_index, typed_in_index, edge_type_counts, distinct_types]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E)
        space: O(V + E)
    ---
    """

    @staticmethod
    def build_index(
        edges: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        typed_out: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        typed_in: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        type_counts: Dict[str, int] = {}
        distinct_nodes: set = set()

        for edge in edges:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            e_type = str(edge.get("edge_type", "default"))
            wt = float(edge.get("weight", 1.0))
            props = dict(edge.get("properties", {}))

            if not src or not tgt:
                continue

            distinct_nodes.add(src)
            distinct_nodes.add(tgt)
            type_counts[e_type] = type_counts.get(e_type, 0) + 1

            if src not in typed_out:
                typed_out[src] = {}
            if e_type not in typed_out[src]:
                typed_out[src][e_type] = []
            typed_out[src][e_type].append({"target": tgt, "weight": wt, "properties": props})

            if tgt not in typed_in:
                typed_in[tgt] = {}
            if e_type not in typed_in[tgt]:
                typed_in[tgt][e_type] = []
            typed_in[tgt][e_type].append({"source": src, "weight": wt, "properties": props})

        return {
            "typed_out_index": typed_out,
            "typed_in_index": typed_in,
            "edge_type_counts": type_counts,
            "distinct_types": sorted(list(type_counts.keys())),
            "num_nodes": len(distinct_nodes),
            "num_edges": len(edges),
        }

    @staticmethod
    def get_typed_neighbors(
        index: Dict[str, Any],
        node: str,
        edge_type: Optional[str] = None,
        direction: str = "out",
    ) -> List[Dict[str, Any]]:
        target_dict = (
            index["typed_out_index"] if direction == "out" else index["typed_in_index"]
        )
        if node not in target_dict:
            return []

        if edge_type:
            return target_dict[node].get(edge_type, [])

        all_nbrs: List[Dict[str, Any]] = []
        for e_t, nbr_list in target_dict[node].items():
            for nbr in nbr_list:
                all_nbrs.append({**nbr, "edge_type": e_t})
        return all_nbrs
