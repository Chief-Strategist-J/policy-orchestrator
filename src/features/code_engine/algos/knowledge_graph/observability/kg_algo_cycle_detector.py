"""
UNEXPECTED HIERARCHICAL CYCLE AND LOOP ANOMALY DETECTOR
Implementation Module for KgAlgoCycleDetector (ALGO-KG-195).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoCycleDetector:
    """
    --- contract:
      id: ALGO-KG-195
      name: KgAlgoCycleDetector
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - cycle_detection
      - loop_anomaly
      - hierarchy_validator
      input_schema:
        adj: object
      output_schema:
        algorithm: string
        has_cycle: boolean
        cycles: array
    ---
    """
    def detect_cycles(self, adj: Dict[str, List[str]]) -> Dict[str, Any]:
        visited: Dict[str, int] = {u: 0 for u in adj}
        detected_cycles: List[List[str]] = []
        path: List[str] = []

        def dfs(u: str):
            visited[u] = 1
            path.append(u)
            for v in adj.get(u, []):
                if visited.get(v, 0) == 0:
                    dfs(v)
                elif visited.get(v, 0) == 1:
                    cycle_start = path.index(v)
                    detected_cycles.append(path[cycle_start:] + [v])
            path.pop()
            visited[u] = 2

        for node in adj:
            if visited[node] == 0:
                dfs(node)
        return {
            "algorithm": "ALGO-KG-195",
            "has_cycle": len(detected_cycles) > 0,
            "cycles": detected_cycles[:5],
            "cycle_count": len(detected_cycles),
        }
