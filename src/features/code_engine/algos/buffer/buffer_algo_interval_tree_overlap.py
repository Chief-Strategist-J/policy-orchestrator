"""
================================================================================
ALGORITHM BLUEPRINT: INTERVAL TREE OVERLAP DETECTOR
================================================================================

1. OVERVIEW & OBJECTIVE:
   An augmented binary search tree storing interval spans $[start, end]$.
   Each node maintains the maximum upper endpoint (`max_end`) across its subtree.
   Enables fast $O(\log N + K)$ collision detection to identify conflicting edits
   and intersecting source ranges before applying multi-agent code mutations.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Augmentation Invariant: `node.max_end = max(node.end, left.max_end, right.max_end)`.
   - Overlap Condition: Two intervals $[a, b]$ and $[c, d]$ overlap if and only if
     $a < d$ and $c < b$.

3. COMPLEXITY ANALYSIS:
   - Insertion: O(log N)
   - Query Overlaps: O(log N + K) where K is number of overlapping intervals
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class IntervalNode:
    def __init__(self, start: int, end: int, data: Any = None) -> None:
        self.start: int = start
        self.end: int = end
        self.max_end: int = end
        self.data: Any = data
        self.left: Optional["IntervalNode"] = None
        self.right: Optional["IntervalNode"] = None


class CodeEngineIntervalTreeAlgo:
    """
    --- contract:
      id: ALGO-BUF-122
      name: CodeEngineIntervalTreeAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(log N + K) per query
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.interval_tree
      - overlap_detection.ranges
      - conflict.collision_guard
      input_schema:
        intervals: array
        query_range: object
      output_schema:
        algorithm: string
        overlapping_count: integer
        overlapping_intervals: array
        has_overlap: boolean
    ---
    """

    def __init__(self) -> None:
        self.root: Optional[IntervalNode] = None

    def insert(self, start: int, end: int, data: Any = None) -> None:
        def _insert(node: Optional[IntervalNode], s: int, e: int, d: Any) -> IntervalNode:
            if node is None:
                return IntervalNode(s, e, d)
            if s < node.start:
                node.left = _insert(node.left, s, e, d)
            else:
                node.right = _insert(node.right, s, e, d)
            node.max_end = max(node.max_end, e)
            return node

        self.root = _insert(self.root, start, end, data)

    def search_overlaps(self, start: int, end: int) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        def _search(node: Optional[IntervalNode], s: int, e: int) -> None:
            if node is None:
                return
            if node.start < e and s < node.end:
                results.append({
                    "start": node.start,
                    "end": node.end,
                    "data": node.data,
                })
            if node.left and node.left.max_end > s:
                _search(node.left, s, e)
            if node.right and node.start < e:
                _search(node.right, s, e)

        _search(self.root, start, end)
        return results

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        intervals: List[Dict[str, Any]] = payload.get("intervals", [])
        q: Dict[str, Any] = payload.get("query_range", {"start": 0, "end": 10})

        tree = CodeEngineIntervalTreeAlgo()
        for item in intervals:
            s = int(item.get("start", 0))
            e = int(item.get("end", s))
            d = item.get("data", None)
            tree.insert(s, e, d)

        q_s = int(q.get("start", 0))
        q_e = int(q.get("end", 0))
        overlaps = tree.search_overlaps(q_s, q_e)

        return {
            "algorithm": "ALGO-BUF-122",
            "overlapping_count": len(overlaps),
            "overlapping_intervals": overlaps,
            "has_overlap": len(overlaps) > 0,
        }
