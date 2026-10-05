"""
================================================================================
ALGORITHM BLUEPRINT: GRAPH INDEX HEALTH AUDITOR (HNSW / DISKANN) (ALGO-VEC-OBS-183)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Measures structural connectivity and health of proximity graph indices (HNSW/DiskANN):
   reachability from entry points, isolated/orphan node counts, and in/out-degree distribution.

2. MATHEMATICAL FORMULATION:
   ReachabilityRatio = |ReachableNodesFromEntryPoint| / |TotalNodes|
   DegreeSkew = (max_degree - min_degree) / avg_degree
================================================================================
"""

from typing import Any, Dict, List, Optional, Set


class VectorObservabilityAlgoGraphIndexHealth:
    """
    --- contract:
      id: ALGO-VEC-OBS-183
      name: VectorObservabilityAlgoGraphIndexHealth
      category: observability
      complexity: O(V + E)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        adjacency_list: dict[str, list[str]]
        entry_points: list[str]
        deleted_node_ids: Optional[list[str]]
      output_schema:
        total_nodes: int
        reachable_node_count: int
        reachability_ratio: float
        unreachable_node_ids: list[str]
        average_out_degree: float
        zero_in_degree_node_count: int
        is_graph_degraded: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        adjacency_list: Dict[str, List[str]],
        entry_points: List[str],
        deleted_node_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not adjacency_list:
            return {
                "total_nodes": 0,
                "reachable_node_count": 0,
                "reachability_ratio": 1.0,
                "unreachable_node_ids": [],
                "average_out_degree": 0.0,
                "zero_in_degree_node_count": 0,
                "is_graph_degraded": False,
            }

        deleted_set = set(deleted_node_ids or [])
        all_nodes = set(adjacency_list.keys()) - deleted_set
        total_v = len(all_nodes)

        visited: Set[str] = set()
        queue = [ep for ep in entry_points if ep in all_nodes]
        for ep in queue:
            visited.add(ep)

        while queue:
            curr = queue.pop(0)
            neighbors = adjacency_list.get(curr, [])
            for nbr in neighbors:
                if nbr in all_nodes and nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)

        unreachable = list(all_nodes - visited)
        reachability = len(visited) / float(total_v) if total_v > 0 else 1.0

        in_degrees: Dict[str, int] = {node: 0 for node in all_nodes}
        out_degrees: List[int] = []

        for node in all_nodes:
            nbrs = [n for n in adjacency_list.get(node, []) if n in all_nodes]
            out_degrees.append(len(nbrs))
            for nbr in nbrs:
                if nbr in in_degrees:
                    in_degrees[nbr] += 1

        zero_in_count = sum(1 for node, in_deg in in_degrees.items() if in_deg == 0 and node not in entry_points)
        avg_out = sum(out_degrees) / float(len(out_degrees)) if out_degrees else 0.0

        is_degraded = (reachability < 0.98) or (zero_in_count > 0) or (len(unreachable) > 0)

        return {
            "total_nodes": total_v,
            "reachable_node_count": len(visited),
            "reachability_ratio": round(reachability, 4),
            "unreachable_node_ids": unreachable[:50],
            "average_out_degree": round(avg_out, 2),
            "zero_in_degree_node_count": zero_in_count,
            "is_graph_degraded": is_degraded,
        }
