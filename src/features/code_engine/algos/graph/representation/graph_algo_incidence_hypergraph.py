"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: INCIDENCE MATRIX & HYPERGRAPH (ALGO-GRAPH-REP-04)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encodes high-order many-to-many relationship structures using hyperedges
   and incidence matrices. Supports bipartite star expansion, co-membership
   clique projections (B * B^T), hyperedge degree accounting, and dual hypergraphs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|V| * |E_hyper|) for incidence construction, O(|V|^2 * |E_hyper|) projection.
   - Space Complexity: O(|V| + |E_hyper| + sum(memberships)).
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder.
   - Guardrails: Capped pairwise clique projections to prevent O(k^2) edge explosions.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Set


class GraphAlgoIncidenceHypergraph:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-04
      name: GraphAlgoIncidenceHypergraph
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, hypergraph, incidence_matrix, clique_projection]
      inputs:
        type: object
        required: [vertices, hyperedges]
        properties:
          vertices:
            type: array
            items: {type: string}
          hyperedges:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [incidence_matrix, clique_projection_edges, hyperedge_degrees, vertex_degrees]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(|V| * |E_hyper|)
        space: O(|V| + sum(|e|))
    ---
    """

    @staticmethod
    def construct(
        vertices: List[str],
        hyperedges: Dict[str, List[str]],
        max_clique_projection_size: int = 50,
    ) -> Dict[str, Any]:
        ordered_vertices = sorted(list(dict.fromkeys(vertices)))
        v_to_idx = {v: i for i, v in enumerate(ordered_vertices)}
        ordered_edges = sorted(list(hyperedges.keys()))
        e_to_idx = {e: j for j, e in enumerate(ordered_edges)}

        n_v = len(ordered_vertices)
        n_e = len(ordered_edges)

        incidence_matrix = [[0] * n_e for _ in range(n_v)]
        hyperedge_degrees: Dict[str, int] = {}
        vertex_degrees: Dict[str, int] = {v: 0 for v in ordered_vertices}
        pair_weights: Dict[tuple, float] = {}

        for e_name in ordered_edges:
            members = sorted(list(set(hyperedges[e_name])))
            e_idx = e_to_idx[e_name]
            hyperedge_degrees[e_name] = len(members)

            for member in members:
                if member in v_to_idx:
                    v_idx = v_to_idx[member]
                    incidence_matrix[v_idx][e_idx] = 1
                    vertex_degrees[member] += 1

            if len(members) <= max_clique_projection_size:
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        u, v = members[i], members[j]
                        pair = (u, v) if u < v else (v, u)
                        pair_weights[pair] = pair_weights.get(pair, 0.0) + 1.0

        clique_edges = [
            {"source": pair[0], "target": pair[1], "weight": wt}
            for pair, wt in sorted(pair_weights.items())
        ]

        bipartite_edges: List[Dict[str, str]] = []
        for e_name, members in hyperedges.items():
            for member in members:
                bipartite_edges.append({"vertex": member, "hyperedge": e_name})

        return {
            "incidence_matrix": incidence_matrix,
            "ordered_vertices": ordered_vertices,
            "ordered_hyperedges": ordered_edges,
            "vertex_to_index": v_to_idx,
            "hyperedge_to_index": e_to_idx,
            "clique_projection_edges": clique_edges,
            "bipartite_representation": bipartite_edges,
            "hyperedge_degrees": hyperedge_degrees,
            "vertex_degrees": vertex_degrees,
            "num_vertices": n_v,
            "num_hyperedges": n_e,
        }
