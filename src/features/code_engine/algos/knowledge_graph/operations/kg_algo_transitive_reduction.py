"""
DAG TRANSITIVE REDUCTION AND REDUNDANT EDGE PRUNER
Implementation Module for KgAlgoTransitiveReduction (ALGO-KG-167).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoTransitiveReduction:
    """
    --- contract:
      id: ALGO-KG-167
      name: KgAlgoTransitiveReduction
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V * (V + E))
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - transitive_reduction
      - dag_minimization
      - redundancy_pruner
      input_schema:
        adj: object
      output_schema:
        algorithm: string
        reduced_edges: array
        pruned_count: integer
    ---
    """
    def compute_reduction(self, adj: Dict[str, List[str]]) -> Dict[str, Any]:
        reduced_adj: Dict[str, List[str]] = {u: [] for u in adj}
        pruned_edges: List[Tuple[str, str]] = []
        for u in adj:
            for v in adj[u]:
                has_alt_path = False
                queue = [w for w in adj[u] if w != v]
                visited = set(queue)
                while queue:
                    curr = queue.pop(0)
                    if curr == v:
                        has_alt_path = True
                        break
                    for nxt in adj.get(curr, []):
                        if nxt not in visited:
                            visited.add(nxt)
                            queue.append(nxt)
                if not has_alt_path:
                    reduced_adj[u].append(v)
                else:
                    pruned_edges.append((u, v))
        return {
            "algorithm": "ALGO-KG-167",
            "reduced_adj": reduced_adj,
            "pruned_edges": [f"{u}->{v}" for u, v in pruned_edges],
            "pruned_count": len(pruned_edges),
        }
