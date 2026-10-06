"""
================================================================================
ALGORITHM BLUEPRINT: HISTOGRAM DIFFERENCE ALGORITHM (LOW-FREQUENCY ANCHORING)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Histogram Diff is Git's modern default diff algorithm. It extends Patience Diff
   by dynamically finding the lowest-frequency common line when strictly unique
   lines cannot be found. If a region has no unique elements, it builds a
   frequency histogram of shared elements, picks the least common anchor, and
   splits the diff region around it.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Lowest-Frequency Invariant: The chosen pivot element minimizes
     $\max(\text{count}_A(\text{line}), \text{count}_B(\text{line}))$.
   - Greedy Extension: Extends matches before and after the anchor line greedily.

3. COMPLEXITY ANALYSIS:
   - Average Time Complexity: $O(N \log N)$
   - Space Complexity: $O(N)$

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import Counter
from typing import Dict, Any, List, Optional, Tuple


class CodeEngineHistogramDiffAlgo:
    """
    --- contract:
      id: ALGO-DIFF-149
      name: CodeEngineHistogramDiffAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(N log N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.histogram_diff
      - git.default_algorithm
      - low_frequency.anchoring
      input_schema:
        source_lines: array
        target_lines: array
      output_schema:
        algorithm: string
        edit_script: array
        total_hunks: integer
    ---
    """

    def _find_lowest_frequency_anchor(
        self, a: List[str], a_start: int, a_end: int, b: List[str], b_start: int, b_end: int
    ) -> Optional[Tuple[int, int]]:
        count_a = Counter(a[a_start:a_end])
        count_b = Counter(b[b_start:b_end])

        common_elements = set(count_a.keys()) & set(count_b.keys())
        if not common_elements:
            return None

        best_elem: Optional[str] = None
        min_freq: int = 10**9

        for elem in common_elements:
            freq = max(count_a[elem], count_b[elem])
            if freq < min_freq:
                min_freq = freq
                best_elem = elem

        if best_elem is None:
            return None

        idx_a = a.index(best_elem, a_start, a_end)
        idx_b = b.index(best_elem, b_start, b_end)
        return (idx_a, idx_b)

    def diff_histogram(
        self, a: List[str], a_start: int, a_end: int, b: List[str], b_start: int, b_end: int
    ) -> List[Dict[str, Any]]:
        while a_start < a_end and b_start < b_end and a[a_start] == b[b_start]:
            a_start += 1
            b_start += 1

        prefix_match = [
            {"type": "equal", "line": a[i], "old_idx": i, "new_idx": b_start - (a_start - i)}
            for i in range(a_start)
        ]

        orig_a_end, orig_b_end = a_end, b_end
        while a_end > a_start and b_end > b_start and a[a_end - 1] == b[b_end - 1]:
            a_end -= 1
            b_end -= 1

        suffix_match = [
            {"type": "equal", "line": a[i], "old_idx": i, "new_idx": b_end + (i - a_end)}
            for i in range(a_end, orig_a_end)
        ]

        if a_start == a_end:
            middle_insert = [
                {"type": "insert", "line": b[j], "new_idx": j} for j in range(b_start, b_end)
            ]
            return prefix_match + middle_insert + suffix_match

        if b_start == b_end:
            middle_delete = [
                {"type": "delete", "line": a[i], "old_idx": i} for i in range(a_start, a_end)
            ]
            return prefix_match + middle_delete + suffix_match

        anchor = self._find_lowest_frequency_anchor(a, a_start, a_end, b, b_start, b_end)
        if not anchor:
            middle: List[Dict[str, Any]] = []
            for i in range(a_start, a_end):
                middle.append({"type": "delete", "line": a[i], "old_idx": i})
            for j in range(b_start, b_end):
                middle.append({"type": "insert", "line": b[j], "new_idx": j})
            return prefix_match + middle + suffix_match

        anchor_a, anchor_b = anchor
        sub_left = self.diff_histogram(a, a_start, anchor_a, b, b_start, anchor_b)
        sub_right = self.diff_histogram(a, anchor_a + 1, a_end, b, anchor_b + 1, b_end)

        pivot = [{
            "type": "equal",
            "line": a[anchor_a],
            "old_idx": anchor_a,
            "new_idx": anchor_b,
            "is_histogram_anchor": True,
        }]

        return prefix_match + sub_left + pivot + sub_right + suffix_match

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: List[str] = payload.get("source_lines", [])
        target: List[str] = payload.get("target_lines", [])

        if isinstance(source, str):
            source = source.splitlines()
        if isinstance(target, str):
            target = target.splitlines()

        script = self.diff_histogram(source, 0, len(source), target, 0, len(target))

        return {
            "algorithm": "ALGO-DIFF-149",
            "edit_script": script,
            "total_hunks": len(script),
        }
