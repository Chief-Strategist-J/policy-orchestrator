"""
ORPHAN ENTITY AND DANGLING RELATION GARBAGE COLLECTOR
Implementation Module for KgAlgoGarbageCollector (ALGO-KG-154).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoGarbageCollector:
    """
    --- contract:
      id: ALGO-KG-154
      name: KgAlgoGarbageCollector
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Nodes + Edges)
        space: O(Nodes + Edges)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - garbage_collection
      - orphan_pruning
      - dangling_edge_cleanup
      input_schema:
        nodes: array
        edges: array
      output_schema:
        algorithm: string
        pruned_nodes: array
        valid_edges: array
        cleaned_count: integer
    ---
    """
    def collect_garbage(self, nodes: List[str], edges: List[Tuple[str, str]], keep_disconnected: bool = False) -> Dict[str, Any]:
        valid_nodes_set = set(nodes)
        connected_nodes: Set[str] = set()
        clean_edges: List[Tuple[str, str]] = []
        for u, v in edges:
            if u in valid_nodes_set and v in valid_nodes_set:
                clean_edges.append((u, v))
                connected_nodes.add(u)
                connected_nodes.add(v)
        if keep_disconnected:
            surviving_nodes = nodes
            orphans = []
        else:
            surviving_nodes = [n for n in nodes if n in connected_nodes]
            orphans = [n for n in nodes if n not in connected_nodes]
        dangling_edges_count = len(edges) - len(clean_edges)
        return {
            "algorithm": "ALGO-KG-154",
            "surviving_nodes": surviving_nodes,
            "valid_edges": clean_edges,
            "pruned_orphans": orphans,
            "pruned_dangling_edges_count": dangling_edges_count,
            "total_pruned": len(orphans) + dangling_edges_count,
        }
