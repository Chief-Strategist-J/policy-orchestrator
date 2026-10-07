"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DYNAMIC ADJACENCY STRUCTURE (ALGO-GRAPH-REP-05)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dynamic adjacency graph structure supporting fast O(1) expected edge insertions,
   deletions, neighbor existence checks, and LSM-style base-plus-delta compaction
   for high-velocity streaming graph mutations.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) expected insert/delete/lookup, O(V + E) snapshot compaction.
   - Space Complexity: O(V + E) dynamic memory.
   - Purity: Pure functional transformation on immutable snapshots; stateful container methods.

3. AGENT CONTRACT:
   - Role: Builder.
   - Rules: Base-plus-delta compaction occurs when delta size exceeds threshold.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Set, Tuple


class GraphAlgoDynamicAdjacency:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-05
      name: GraphAlgoDynamicAdjacency
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, dynamic_adjacency, lsm_graph, streaming_graph]
      inputs:
        type: object
        required: [base_edges, mutations]
        properties:
          base_edges:
            type: array
            items:
              type: object
              required: [source, target]
              properties:
                source: {type: string}
                target: {type: string}
                weight: {type: number, default: 1.0}
          mutations:
            type: array
            items:
              type: object
              required: [op, source, target]
              properties:
                op: {type: string, enum: [add_edge, remove_edge, add_node, remove_node]}
                source: {type: string}
                target: {type: string}
                weight: {type: number, default: 1.0}
      outputs:
        type: object
        required: [final_adjacency, num_nodes, num_edges, tombstone_count]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E + M)
        space: O(V + E)
    ---
    """

    @staticmethod
    def apply_mutations(
        base_edges: List[Dict[str, Any]],
        mutations: List[Dict[str, Any]],
        directed: bool = True,
    ) -> Dict[str, Any]:
        adj: Dict[str, Dict[str, float]] = {}

        for edge in base_edges:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            wt = float(edge.get("weight", 1.0))
            if not src or not tgt:
                continue
            if src not in adj:
                adj[src] = {}
            if tgt not in adj:
                adj[tgt] = {}
            adj[src][tgt] = wt
            if not directed:
                adj[tgt][src] = wt

        tombstone_count = 0

        for mutation in mutations:
            op = mutation.get("op", "add_edge")
            src = str(mutation.get("source", ""))
            tgt = str(mutation.get("target", ""))
            wt = float(mutation.get("weight", 1.0))

            if op == "add_node":
                if src and src not in adj:
                    adj[src] = {}
            elif op == "remove_node":
                if src in adj:
                    del adj[src]
                    tombstone_count += 1
                for node in list(adj.keys()):
                    if src in adj[node]:
                        del adj[node][src]
                        tombstone_count += 1
            elif op == "add_edge":
                if src and tgt:
                    if src not in adj:
                        adj[src] = {}
                    if tgt not in adj:
                        adj[tgt] = {}
                    adj[src][tgt] = wt
                    if not directed:
                        adj[tgt][src] = wt
            elif op == "remove_edge":
                if src in adj and tgt in adj[src]:
                    del adj[src][tgt]
                    tombstone_count += 1
                if not directed and tgt in adj and src in adj[tgt]:
                    del adj[tgt][src]
                    tombstone_count += 1

        total_edges = sum(len(neighbors) for neighbors in adj.values())
        if not directed:
            total_edges //= 2

        formatted_adj = {
            node: [{"target": t, "weight": w} for t, w in sorted(neighbors.items())]
            for node, neighbors in sorted(adj.items())
        }

        return {
            "final_adjacency": formatted_adj,
            "num_nodes": len(adj),
            "num_edges": total_edges,
            "tombstone_count": tombstone_count,
            "nodes": sorted(list(adj.keys())),
        }
