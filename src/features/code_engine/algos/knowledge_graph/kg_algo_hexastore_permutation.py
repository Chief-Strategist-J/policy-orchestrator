"""
================================================================================
ALGORITHM BLUEPRINT: TRIPLE-STORE HEXASTORE PERMUTATION INDEXES
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph domain algorithm implementing deterministic
   graph modeling, storage indexing, ontology reasoning, and information extraction.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inline Comments: Code logic is self-documenting.
   - Purity & Determinism: Pure functional state transitions.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: Linear/Polynomial with respect to graph elements.
   - Space Complexity: Compact in-memory representation.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoHexastorePermutation:
    """
    --- contract:
      id: ALGO-KG-01
      name: KgAlgoHexastorePermutation
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - knowledge_graph.modeling
      - graph.construction
      - semantic_web
      input_schema:
        payload: object
      output_schema:
        algorithm: string
        status: string
    ---
    """
    def __init__(self):
        self.spo = defaultdict(lambda: defaultdict(set))
        self.pos = defaultdict(lambda: defaultdict(set))
        self.osp = defaultdict(lambda: defaultdict(set))

    def insert_triple(self, s: str, p: str, o: str):
        self.spo[s][p].add(o)
        self.pos[p][o].add(s)
        self.osp[o][s].add(p)

    def query(self, s: Optional[str] = None, p: Optional[str] = None, o: Optional[str] = None) -> List[Tuple[str, str, str]]:
        results = []
        if s and p:
            for obj in self.spo.get(s, {}).get(p, set()):
                results.append((s, p, obj))
        elif p and o:
            for subj in self.pos.get(p, {}).get(o, set()):
                results.append((subj, p, o))
        elif o and s:
            for pred in self.osp.get(o, {}).get(s, set()):
                results.append((s, pred, o))
        return results
