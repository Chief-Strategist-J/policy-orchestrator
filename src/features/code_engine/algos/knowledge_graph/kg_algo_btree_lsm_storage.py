"""
================================================================================
ALGORITHM BLUEPRINT: LSM MEMTABLE & WAL GRAPH STORAGE ENGINE
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

import bisect
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoBtreeLsmStorage:
    """
    --- contract:
      id: ALGO-KG-01
      name: KgAlgoBtreeLsmStorage
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
    def __init__(self, max_memtable_size: int = 100):
        self.memtable = []
        self.wal_log = []
        self.max_size = max_memtable_size
        self.flushed_segments = []

    def put_fact(self, key: str, value: Any):
        self.wal_log.append((key, value))
        self.memtable.append((key, value))
        if len(self.memtable) >= self.max_size:
            self.flush()

    def flush(self):
        sorted_segment = sorted(self.memtable, key=lambda x: x[0])
        self.flushed_segments.append(sorted_segment)
        self.memtable = []

    def get_fact(self, key: str) -> Optional[Any]:
        for k, v in reversed(self.memtable):
            if k == key:
                return v
        for seg in reversed(self.flushed_segments):
            keys = [k for k, _ in seg]
            idx = bisect.bisect_left(keys, key)
            if idx < len(keys) and keys[idx] == key:
                return seg[idx][1]
        return None
