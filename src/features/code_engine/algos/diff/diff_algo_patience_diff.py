"""
================================================================================
ALGORITHM BLUEPRINT: PATIENCE DIFFERENCE ALGORITHM (UNIQUE COMMON LINE ANCHORS)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Patience Diff (designed by Bram Cohen) matches lines that appear uniquely
   in both source and target documents. Computes the Longest Increasing
   Subsequence (LIS) across these unique pairs using Patience Sorting (hence the name).
   These matched lines serve as structural anchors, and the unaligned regions
   between anchors are diffed recursively. This eliminates false matches on
   repetitive lines such as isolated closing braces `}` or blank lines.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Unique Line Invariant: A line is considered an anchor ONLY if its occurrence
     frequency in sequence A is exactly 1 AND its occurrence frequency in sequence B
     is exactly 1.
   - Monotonic Anchor Alignment: Anchors must be strictly monotonically increasing
     in both index spaces.

3. COMPLEXITY ANALYSIS:
   - LIS on Unique Lines: O(U log U) where U is unique common line count
   - Recursive Diff: Proportional to partition sizes
   - Generates visually cleaner, human-intuitive diff hunks.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import bisect
from collections import Counter
from typing import Dict, Any, List, Optional, Tuple


class CodeEnginePatienceDiffAlgo:
    """
    --- contract:
      id: ALGO-DIFF-148
      name: CodeEnginePatienceDiffAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(N log N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.patience_diff
      - patience_sort.longest_increasing_subsequence
      - structural_anchors.clean_hunks
      input_schema:
        source_lines: array
        target_lines: array
      output_schema:
        algorithm: string
        unique_anchors: integer
        edit_script: array
    ---
    """

    def _find_unique_common_lines(
        self, a: List[str], a_start: int, a_end: int, b: List[str], b_start: int, b_end: int
    ) -> List[Tuple[int, int]]:
        count_a = Counter(a[a_start:a_end])
        count_b = Counter(b[b_start:b_end])

        unique_a: Dict[str, int] = {}
        for idx in range(a_start, a_end):
            line = a[idx]
            if count_a[line] == 1 and count_b.get(line, 0) == 1:
                unique_a[line] = idx

        unique_b: Dict[str, int] = {}
        for idx in range(b_start, b_end):
            line = b[idx]
            if count_b[line] == 1 and line in unique_a:
                unique_b[line] = idx

        pairs: List[Tuple[int, int]] = []
        for line, idx_a in unique_a.items():
            if line in unique_b:
                pairs.append((idx_a, unique_b[line]))

        pairs.sort(key=lambda p: p[0])
        return pairs

    def _longest_increasing_subsequence(self, pairs: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if not pairs:
            return []

        b_indices = [p[1] for p in pairs]
        piles: List[int] = []
        pile_tails: List[int] = []
        predecessors: List[Optional[int]] = [None] * len(pairs)

        for i, val in enumerate(b_indices):
            pos = bisect.bisect_left(pile_tails, val)
            if pos < len(pile_tails):
                pile_tails[pos] = val
                piles[pos] = i
            else:
                pile_tails.append(val)
                piles.append(i)

            if pos > 0:
                predecessors[i] = piles[pos - 1]

        lis: List[Tuple[int, int]] = []
        curr: Optional[int] = piles[-1] if piles else None
        while curr is not None:
            lis.append(pairs[curr])
            curr = predecessors[curr]

        lis.reverse()
        return lis

    def diff_patience(
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

        unique_pairs = self._find_unique_common_lines(a, a_start, a_end, b, b_start, b_end)
        lis_anchors = self._longest_increasing_subsequence(unique_pairs)

        if not lis_anchors:
            middle: List[Dict[str, Any]] = []
            for i in range(a_start, a_end):
                middle.append({"type": "delete", "line": a[i], "old_idx": i})
            for j in range(b_start, b_end):
                middle.append({"type": "insert", "line": b[j], "new_idx": j})
            return prefix_match + middle + suffix_match

        middle_script: List[Dict[str, Any]] = []
        cur_a, cur_b = a_start, b_start

        for anchor_a, anchor_b in lis_anchors:
            sub_diff = self.diff_patience(a, cur_a, anchor_a, b, cur_b, anchor_b)
            middle_script.extend(sub_diff)
            middle_script.append({
                "type": "equal",
                "line": a[anchor_a],
                "old_idx": anchor_a,
                "new_idx": anchor_b,
                "is_anchor": True,
            })
            cur_a = anchor_a + 1
            cur_b = anchor_b + 1

        sub_diff_tail = self.diff_patience(a, cur_a, a_end, b, cur_b, b_end)
        middle_script.extend(sub_diff_tail)

        return prefix_match + middle_script + suffix_match

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: List[str] = payload.get("source_lines", [])
        target: List[str] = payload.get("target_lines", [])

        if isinstance(source, str):
            source = source.splitlines()
        if isinstance(target, str):
            target = target.splitlines()

        unique_pairs = self._find_unique_common_lines(source, 0, len(source), target, 0, len(target))
        script = self.diff_patience(source, 0, len(source), target, 0, len(target))

        return {
            "algorithm": "ALGO-DIFF-148",
            "unique_anchors": len(unique_pairs),
            "edit_script": script,
        }
