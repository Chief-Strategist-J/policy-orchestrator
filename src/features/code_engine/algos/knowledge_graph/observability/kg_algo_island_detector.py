"""
DISCONNECTED SUBGRAPH ISLAND AND ISOLATION ALERTING
Implementation Module for KgAlgoIslandDetector (ALGO-KG-196).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoIslandDetector:
    """
    --- contract:
      id: ALGO-KG-196
      name: KgAlgoIslandDetector
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - island_detection
      - connected_components
      - isolation_monitor
      input_schema:
        nodes: array
        edges: array
      output_schema:
        algorithm: string
        isolated_islands: array
        giant_component_size: integer
    ---
    """
    def detect_islands(self, nodes: List[str], edges: List[Tuple[str, str]], min_island_size: int = 1) -> Dict[str, Any]:
        adj: Dict[str, Set[str]] = {n: set() for n in nodes}
        for u, v in edges:
            if u in adj and v in adj:
                adj[u].add(v)
                adj[v].add(u)
        visited: Set[str] = set()
        components: List[List[str]] = []
        for n in nodes:
            if n not in visited:
                comp: List[str] = []
                q = [n]
                visited.add(n)
                while q:
                    curr = q.pop(0)
                    comp.append(curr)
                    for nxt in adj.get(curr, set()):
                        if nxt not in visited:
                            visited.add(nxt)
                            q.append(nxt)
                components.append(comp)
        components.sort(key=len, reverse=True)
        giant_size = len(components[0]) if components else 0
        islands = [c for c in components[1:] if len(c) >= min_island_size]
        return {
            "algorithm": "ALGO-KG-196",
            "component_count": len(components),
            "giant_component_size": giant_size,
            "isolated_islands": islands[:10],
            "total_isolated_islands": len(islands),
        }
