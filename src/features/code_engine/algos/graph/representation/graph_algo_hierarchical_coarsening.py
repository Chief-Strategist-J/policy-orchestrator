"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HIERARCHICAL COARSENING (ALGO-GRAPH-REP-12)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs multi-level hierarchical coarse graph representations using
   Heavy-Edge Matching (HEM) and modular contraction. Collapses tightly-coupled
   subgraphs into super-vertices with summed edge weights, enabling fast
   coarse-to-fine search, multilevel partitioning, and overview summarization.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) per coarsening level.
   - Space Complexity: O(V + E) across the multi-level hierarchy pyramid.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder & Analyst.
   - Rules: Retains member projection mappings between coarse and fine levels.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar, Set

NodeId = TypeVar("NodeId")


class GraphAlgoHierarchicalCoarsening(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-12
      name: GraphAlgoHierarchicalCoarsening
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, coarsening, heavy_edge_matching, multilevel]
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
        required: [levels, num_levels, reduction_ratio]
      parameters:
        max_levels: {type: integer, default: 3}
        min_nodes: {type: integer, default: 4}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(L * (V + E))
        space: O(V + E)
    ---
    """

    @staticmethod
    def coarsen_hierarchy(
        nodes: List[str],
        edges: List[Dict[str, Any]],
        max_levels: int = 3,
        min_nodes: int = 4,
    ) -> Dict[str, Any]:
        current_nodes = sorted(list(dict.fromkeys(nodes)))
        current_edges = [
            {
                "source": str(e["source"]),
                "target": str(e["target"]),
                "weight": float(e.get("weight", 1.0)),
            }
            for e in edges
            if str(e["source"]) != str(e["target"])
        ]

        levels: List[Dict[str, Any]] = [
            {
                "level": 0,
                "nodes": current_nodes,
                "edges": current_edges,
                "node_to_super": {n: n for n in current_nodes},
                "super_to_members": {n: [n] for n in current_nodes},
            }
        ]

        for lvl in range(1, max_levels + 1):
            if len(current_nodes) <= min_nodes:
                break

            adj: Dict[str, List[Tuple[str, float]]] = {n: [] for n in current_nodes}
            for e in current_edges:
                u, v, w = e["source"], e["target"], e["weight"]
                if u in adj and v in adj:
                    adj[u].append((v, w))
                    adj[v].append((u, w))

            matched: Set[str] = set()
            node_to_super: Dict[str, str] = {}
            super_to_members: Dict[str, List[str]] = {}
            super_idx = 0

            sorted_candidates = sorted(
                current_nodes,
                key=lambda n: len(adj.get(n, [])),
                reverse=True,
            )

            for u in sorted_candidates:
                if u in matched:
                    continue

                best_v = None
                best_w = -1.0
                for v, w in adj[u]:
                    if v not in matched and v != u:
                        if w > best_w:
                            best_w = w
                            best_v = v

                super_name = f"c_{lvl}_{super_idx}"
                super_idx += 1

                if best_v is not None:
                    matched.add(u)
                    matched.add(best_v)
                    node_to_super[u] = super_name
                    node_to_super[best_v] = super_name
                    super_to_members[super_name] = [u, best_v]
                else:
                    matched.add(u)
                    node_to_super[u] = super_name
                    super_to_members[super_name] = [u]

            next_nodes = sorted(list(super_to_members.keys()))
            edge_accumulator: Dict[Tuple[str, str], float] = {}

            for e in current_edges:
                su = node_to_super.get(e["source"])
                sv = node_to_super.get(e["target"])
                if su and sv and su != sv:
                    pair = (su, sv) if su < sv else (sv, su)
                    edge_accumulator[pair] = edge_accumulator.get(pair, 0.0) + e["weight"]

            next_edges = [
                {"source": p[0], "target": p[1], "weight": wt}
                for p, wt in sorted(edge_accumulator.items())
            ]

            levels.append(
                {
                    "level": lvl,
                    "nodes": next_nodes,
                    "edges": next_edges,
                    "node_to_super": node_to_super,
                    "super_to_members": super_to_members,
                }
            )

            current_nodes = next_nodes
            current_edges = next_edges

        orig_len = len(levels[0]["nodes"])
        final_len = len(levels[-1]["nodes"])
        ratio = (orig_len - final_len) / max(orig_len, 1)

        return {
            "levels": levels,
            "num_levels": len(levels),
            "original_nodes": orig_len,
            "coarsened_nodes": final_len,
            "reduction_ratio": ratio,
        }
