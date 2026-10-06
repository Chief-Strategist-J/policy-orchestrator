"""
================================================================================
ALGORITHM BLUEPRINT: K-CORE SUBGRAPH DECOMPOSITION ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph domain algorithm implementing graph querying,
   declarative pattern matching, graph analytics, and description logic reasoning.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inline Comments: Self-documenting pure methods.
   - Purity & Determinism: Pure functional state transitions.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: Conforming to graph query semantics and polynomial fragments.
   - Space Complexity: Compact working memory and frontier representations.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoKCoreDecomposition:
    """
    --- contract:
      id: ALGO-KG-84
      name: KgAlgoKCoreDecomposition
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - k_core.decomposition
      - dense_subgraph
      - degeneracy
      input_schema:
        nodes: array
        edges: array
        k: integer
      output_schema:
        algorithm: string
        k_core_nodes: array
        k: integer
    ---
    """
    def extract_k_core(self, nodes: List[str], edges: List[Tuple[str, str]], k: int = 2) -> Dict[str, Any]:
        adj = {n: set() for n in nodes}
        for u, v in edges:
            if u in adj and v in adj:
                adj[u].add(v); adj[v].add(u)
        degrees = {n: len(adj[n]) for n in nodes}
        removed = set()
        queue = [n for n in nodes if degrees[n] < k]
        while queue:
            curr = queue.pop(0)
            if curr in removed: continue
            removed.add(curr)
            for nbr in adj[curr]:
                if nbr not in removed:
                    degrees[nbr] -= 1
                    if degrees[nbr] < k: queue.append(nbr)
        k_core = [n for n in nodes if n not in removed]
        return {
            "algorithm": "ALGO-KG-84",
            "k": k,
            "k_core_nodes": sorted(k_core),
            "k_core_size": len(k_core),
        }
