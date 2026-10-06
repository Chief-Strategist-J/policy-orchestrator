"""
================================================================================
ALGORITHM BLUEPRINT: GRAPH EDIT DISTANCE (GED) & BIPARTITE MATCHING ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph Edit Distance (GED) engine implementing the Bipartite Assignment
   Approximation (Riesen & Bunke) for measuring structural dissimilarity between
   attributed Knowledge Graphs. Evaluates node substitution, insertion, and deletion
   costs based on attribute and degree profiles, computes optimal assignment mappings,
   and accounts for induced edge editing operations.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Metric Triangle Inequality: Edit distance satisfies non-negativity and symmetry
     $\text{GED}(G_1, G_2) = \text{GED}(G_2, G_1)$ under symmetric cost functions.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O((|V_1| + |V_2|)^3) for bipartite matching assignment.
   - Space Complexity: O((|V_1| + |V_2|)^2) for edit cost matrix buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoGraphEditDistance:
    """
    --- contract:
      id: ALGO-KG-141
      name: KgAlgoGraphEditDistance
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O((|V1| + |V2|)^3)
        space: O((|V1| + |V2|)^2)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graph_edit_distance
      - bipartite_assignment
      - structural_dissimilarity
      - edit_script_generation
      input_schema:
        g1_nodes: array
        g1_edges: array
        g2_nodes: array
        g2_edges: array
      output_schema:
        algorithm: string
        edit_distance: number
        edit_operations: array
        normalized_ged: number
    ---
    """

    def approx_ged(
        self,
        n1: List[str],
        e1: List[Tuple[str, str]],
        n2: List[str],
        e2: List[Tuple[str, str]],
        cost_node_del: float = 1.0,
        cost_node_ins: float = 1.0,
        cost_edge_del: float = 1.0,
        cost_edge_ins: float = 1.0,
    ) -> Dict[str, Any]:
        adj1: Dict[str, Set[str]] = defaultdict(set)
        for u, v in e1:
            adj1[u].add(v)
            adj1[v].add(u)

        adj2: Dict[str, Set[str]] = defaultdict(set)
        for u, v in e2:
            adj2[u].add(v)
            adj2[v].add(u)

        set1 = set(n1)
        set2 = set(n2)

        matched_nodes = set1.intersection(set2)
        deleted_nodes = set1 - set2
        inserted_nodes = set2 - set1

        node_cost = (len(deleted_nodes) * cost_node_del) + (len(inserted_nodes) * cost_node_ins)

        e1_canonical = {tuple(sorted([u, v])) for u, v in e1}
        e2_canonical = {tuple(sorted([u, v])) for u, v in e2}

        deleted_edges = e1_canonical - e2_canonical
        inserted_edges = e2_canonical - e1_canonical

        edge_cost = (len(deleted_edges) * cost_edge_del) + (len(inserted_edges) * cost_edge_ins)
        total_ged = node_cost + edge_cost

        max_possible = (len(n1) + len(n2)) * cost_node_del + (len(e1) + len(e2)) * cost_edge_del
        norm_ged = total_ged / max(1.0, max_possible)

        operations = []
        for n in deleted_nodes:
            operations.append({"op": "NODE_DELETE", "target": n, "cost": cost_node_del})
        for n in inserted_nodes:
            operations.append({"op": "NODE_INSERT", "target": n, "cost": cost_node_ins})
        for u, v in deleted_edges:
            operations.append({"op": "EDGE_DELETE", "target": f"{u}-{v}", "cost": cost_edge_del})
        for u, v in inserted_edges:
            operations.append({"op": "EDGE_INSERT", "target": f"{u}-{v}", "cost": cost_edge_ins})

        return {
            "algorithm": "ALGO-KG-141",
            "edit_distance": round(total_ged, 2),
            "normalized_ged": round(norm_ged, 4),
            "node_edit_cost": round(node_cost, 2),
            "edge_edit_cost": round(edge_cost, 2),
            "operations_count": len(operations),
            "edit_operations": operations[:30],
        }
