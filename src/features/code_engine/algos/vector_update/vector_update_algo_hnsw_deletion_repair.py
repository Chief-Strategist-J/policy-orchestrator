"""
================================================================================
ALGORITHM BLUEPRINT: HNSW DELETION WITH CONNECTIVITY REPAIR (ALGO-VEC-UPD-117)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Re-wires and repairs HNSW graph adjacency lists after node deletions to prevent
   navigation dead-ends and maintain high search recall.
================================================================================
"""

from typing import Any, Dict, List, Optional, Set


class VectorUpdateAlgoHnswDeletionRepair:
    """
    --- contract:
      id: ALGO-VEC-UPD-117
      name: VectorUpdateAlgoHnswDeletionRepair
      category: update
      complexity: O(deg(u)^2)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        adjacency_list: dict[str, list[str]]
        deleted_nodes: list[str]
        max_edges: int
      output_schema:
        repaired_adjacency: dict[str, list[str]]
        purged_nodes: list[str]
        reconnected_edges_count: int
    ---
    """

    @classmethod
    def repair(
        cls,
        adjacency_list: Dict[str, List[str]],
        deleted_nodes: List[str],
        max_edges: int = 16,
    ) -> Dict[str, Any]:
        adj: Dict[str, Set[str]] = {k: set(v) for k, v in adjacency_list.items()}
        del_set = set(deleted_nodes)
        reconnected_edges = 0

        for u in del_set:
            if u not in adj:
                continue
            neighbors = [n for n in adj[u] if n not in del_set and n in adj]
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    ni, nj = neighbors[i], neighbors[j]
                    if nj not in adj[ni] and len(adj[ni]) < max_edges:
                        adj[ni].add(nj)
                        reconnected_edges += 1
                    if ni not in adj[nj] and len(adj[nj]) < max_edges:
                        adj[nj].add(ni)
                        reconnected_edges += 1
            adj.pop(u, None)

        for node, nbrs in adj.items():
            adj[node] = {n for n in nbrs if n not in del_set}

        return {
            "repaired_adjacency": {k: sorted(list(v)) for k, v in adj.items()},
            "purged_nodes": list(del_set),
            "reconnected_edges_count": reconnected_edges,
        }
