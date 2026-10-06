"""
================================================================================
ALGORITHM BLUEPRINT: BIDIRECTIONAL BFS SHORTEST PATH FINDER
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

from collections import deque
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoBidirectionalBfs:
    """
    --- contract:
      id: ALGO-KG-65
      name: KgAlgoBidirectionalBfs
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(b^(d/2))
        space: O(b^(d/2))
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - bidirectional_bfs
      - shortest_path
      - frontier.collision
      input_schema:
        forward_adj: object
        reverse_adj: object
        source: string
        target: string
      output_schema:
        algorithm: string
        path_found: boolean
        distance: integer
        meeting_node: string
    ---
    """
    def find_shortest_path(self, fwd: Dict[str, List[str]], rev: Dict[str, List[str]], source: str, target: str) -> Dict[str, Any]:
        if source == target:
            return {"algorithm": "ALGO-KG-65", "path_found": True, "distance": 0, "meeting_node": source}
        q_src, q_tgt = deque([source]), deque([target])
        dist_src, dist_tgt = {source: 0}, {target: 0}
        while q_src and q_tgt:
            curr_s = q_src.popleft()
            for nbr in fwd.get(curr_s, []):
                if nbr in dist_tgt:
                    return {"algorithm": "ALGO-KG-65", "path_found": True, "distance": dist_src[curr_s] + 1 + dist_tgt[nbr], "meeting_node": nbr}
                if nbr not in dist_src:
                    dist_src[nbr] = dist_src[curr_s] + 1
                    q_src.append(nbr)
            curr_t = q_tgt.popleft()
            for nbr in rev.get(curr_t, []):
                if nbr in dist_src:
                    return {"algorithm": "ALGO-KG-65", "path_found": True, "distance": dist_src[nbr] + 1 + dist_tgt[curr_t], "meeting_node": nbr}
                if nbr not in dist_tgt:
                    dist_tgt[nbr] = dist_tgt[curr_t] + 1
                    q_tgt.append(nbr)
        return {"algorithm": "ALGO-KG-65", "path_found": False, "distance": -1, "meeting_node": None}
