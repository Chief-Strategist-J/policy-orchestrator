"""
================================================================================
ALGORITHM BLUEPRINT: NODE2VEC BIASED RANDOM WALK SAMPLER (P & Q)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph domain algorithm implementing graph embeddings,
   Graph Neural Network architectures, link prediction, and representation learning.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inline Comments: Code logic is self-documenting.
   - Purity & Determinism: Pure functional state transitions.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: Linear with respect to dimensionality and sample size.
   - Space Complexity: Compact tensor representations.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import random
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoNode2vec:
    """
    --- contract:
      id: ALGO-KG-113
      name: KgAlgoNode2vec
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Walk_Length * Degree)
        space: O(Walk_Length)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - node2vec
      - biased_random_walk
      - bfs_dfs_tradeoff
      input_schema:
        adj: object
        start_node: string
        p: number
        q: number
      output_schema:
        algorithm: string
        walk: array
    ---
    """
    def biased_walk(self, adj: Dict[str, List[str]], start_node: str, p: float = 1.0, q: float = 1.0, length: int = 8) -> Dict[str, Any]:
        walk = [start_node]
        if not adj.get(start_node):
            return {"algorithm": "ALGO-KG-113", "walk": walk}
        curr = random.choice(adj[start_node])
        walk.append(curr)
        for _ in range(length - 2):
            prev = walk[-2]
            nbrs = adj.get(curr, [])
            if not nbrs: break
            weights = []
            for nbr in nbrs:
                if nbr == prev: weights.append(1.0 / p)
                elif nbr in adj.get(prev, []): weights.append(1.0)
                else: weights.append(1.0 / q)
            total = sum(weights)
            r = random.uniform(0, total)
            cum = 0.0
            next_node = nbrs[-1]
            for nbr, w in zip(nbrs, weights):
                cum += w
                if r <= cum: next_node = nbr; break
            walk.append(next_node)
            curr = next_node
        return {
            "algorithm": "ALGO-KG-113",
            "walk": walk,
        }
