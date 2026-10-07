"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CSR AND CSC GRAPH STORAGE (ALGO-GRAPH-REP-02)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Compressed Sparse Row (CSR) and Compressed Sparse Column (CSC) compact array
   layouts for high-throughput sparse graph traversals. Stores contiguous
   neighbor lists and offset pointers for O(1) degree lookup and cache-line
   friendly sequential edge scans.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E log(max_deg)) to build, O(degree(v)) neighbor slice.
   - Space Complexity: O(V + E) compact contiguous memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder.
   - Guardrails: 64-bit offsets supported for graph scale > 2^31 edges.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple


class GraphAlgoCsrCsc:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-02
      name: GraphAlgoCsrCsc
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, csr, csc, sparse_matrix]
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
              required: [source, target]
              properties:
                source: {type: string}
                target: {type: string}
                weight: {type: number, default: 1.0}
      outputs:
        type: object
        required: [csr, csc, node_to_index, index_to_node]
        properties:
          csr:
            type: object
            required: [offsets, targets, weights]
          csc:
            type: object
            required: [offsets, sources, weights]
          node_to_index:
            type: object
            additionalProperties: {type: integer}
          index_to_node:
            type: array
            items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E log V)
        space: O(V + E)
    ---
    """

    @staticmethod
    def build(
        nodes: List[str],
        edges: List[Dict[str, Any]],
        directed: bool = True,
    ) -> Dict[str, Any]:
        ordered_nodes = sorted(list(dict.fromkeys(nodes)))
        node_to_idx = {node: i for i, node in enumerate(ordered_nodes)}
        n = len(ordered_nodes)

        out_edges: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
        in_edges: List[List[Tuple[int, float]]] = [[] for _ in range(n)]

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            wt = float(edge.get("weight", 1.0))
            if src in node_to_idx and tgt in node_to_idx:
                u = node_to_idx[src]
                v = node_to_idx[tgt]
                out_edges[u].append((v, wt))
                in_edges[v].append((u, wt))
                if not directed:
                    out_edges[v].append((u, wt))
                    in_edges[u].append((v, wt))

        csr_offsets = [0] * (n + 1)
        csr_targets: List[int] = []
        csr_weights: List[float] = []

        for i in range(n):
            out_edges[i].sort(key=lambda item: item[0])
            csr_offsets[i] = len(csr_targets)
            for target_idx, weight in out_edges[i]:
                csr_targets.append(target_idx)
                csr_weights.append(weight)
        csr_offsets[n] = len(csr_targets)

        csc_offsets = [0] * (n + 1)
        csc_sources: List[int] = []
        csc_weights: List[float] = []

        for i in range(n):
            in_edges[i].sort(key=lambda item: item[0])
            csc_offsets[i] = len(csc_sources)
            for source_idx, weight in in_edges[i]:
                csc_sources.append(source_idx)
                csc_weights.append(weight)
        csc_offsets[n] = len(csc_sources)

        return {
            "csr": {
                "offsets": csr_offsets,
                "targets": csr_targets,
                "weights": csr_weights,
            },
            "csc": {
                "offsets": csc_offsets,
                "sources": csc_sources,
                "weights": csc_weights,
            },
            "node_to_index": node_to_idx,
            "index_to_node": ordered_nodes,
            "num_nodes": n,
            "num_edges": len(csr_targets),
        }

    @staticmethod
    def get_out_neighbors(
        csr: Dict[str, Any],
        node_index: int,
        index_to_node: List[str],
    ) -> List[Tuple[str, float]]:
        offsets = csr["offsets"]
        targets = csr["targets"]
        weights = csr["weights"]
        if node_index < 0 or node_index >= len(offsets) - 1:
            return []

        start = offsets[node_index]
        end = offsets[node_index + 1]
        return [
            (index_to_node[targets[k]], weights[k])
            for k in range(start, end)
        ]

    @staticmethod
    def get_in_neighbors(
        csc: Dict[str, Any],
        node_index: int,
        index_to_node: List[str],
    ) -> List[Tuple[str, float]]:
        offsets = csc["offsets"]
        sources = csc["sources"]
        weights = csc["weights"]
        if node_index < 0 or node_index >= len(offsets) - 1:
            return []

        start = offsets[node_index]
        end = offsets[node_index + 1]
        return [
            (index_to_node[sources[k]], weights[k])
            for k in range(start, end)
        ]
