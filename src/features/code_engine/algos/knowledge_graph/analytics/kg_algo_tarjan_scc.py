"""
================================================================================
ALGORITHM BLUEPRINT: TARJAN'S STRONGLY CONNECTED COMPONENTS (SCC)
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

class KgAlgoTarjanScc:
    """
    --- contract:
      id: ALGO-KG-80
      name: KgAlgoTarjanScc
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - tarjan_scc
      - strongly_connected_components
      - directed_graph
      input_schema:
        nodes: array
        edges: array
      output_schema:
        algorithm: string
        scc_count: integer
        scc_list: array
    ---
    """
    def compute_scc(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        adj = defaultdict(list)
        for u, v in edges: adj[u].append(v)
        index = 0
        indices = {}; lowlink = {}; on_stack = set(); stack = []; sccs = []

        def strongconnect(node):
            nonlocal index
            indices[node] = index
            lowlink[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            for nbr in adj[node]:
                if nbr not in indices:
                    strongconnect(nbr)
                    lowlink[node] = min(lowlink[node], lowlink[nbr])
                elif nbr in on_stack:
                    lowlink[node] = min(lowlink[node], indices[nbr])
            if lowlink[node] == indices[node]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == node: break
                sccs.append(sorted(scc))

        for n in nodes:
            if n not in indices: strongconnect(n)
        return {
            "algorithm": "ALGO-KG-80",
            "scc_count": len(sccs),
            "scc_list": sccs,
        }
