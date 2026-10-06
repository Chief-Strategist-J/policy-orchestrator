"""
GRAPH SLICING AND TARGETED K-HOP SUBGRAPH EXTRACTOR
Implementation Module for KgAlgoSubgraphSlicer (ALGO-KG-158).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoSubgraphSlicer:
    """
    --- contract:
      id: ALGO-KG-158
      name: KgAlgoSubgraphSlicer
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V_sub + E_sub)
        space: O(V_sub)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - subgraph_slicing
      - k_hop_extraction
      - focused_context
      input_schema:
        seed_nodes: array
        adjacency: object
        k_hops: integer
      output_schema:
        algorithm: string
        subgraph_nodes: array
        subgraph_edges: array
    ---
    """
    def extract_k_hop(self, seeds: List[str], adj: Dict[str, List[str]], k_hops: int = 2, max_nodes: int = 500) -> Dict[str, Any]:
        visited: Set[str] = set(seeds)
        frontier: Set[str] = set(seeds)
        edges: Set[Tuple[str, str]] = set()
        for _ in range(k_hops):
            next_frontier: Set[str] = set()
            for u in frontier:
                for v in adj.get(u, []):
                    if len(visited) < max_nodes or v in visited:
                        edges.add((u, v))
                        if v not in visited:
                            visited.add(v)
                            next_frontier.add(v)
            frontier = next_frontier
            if not frontier:
                break
        return {
            "algorithm": "ALGO-KG-158",
            "subgraph_nodes": sorted(list(visited)),
            "subgraph_edges": [f"{u}->{v}" for u, v in sorted(list(edges))],
            "node_count": len(visited),
            "edge_count": len(edges),
        }
