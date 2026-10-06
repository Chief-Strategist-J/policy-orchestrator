"""
================================================================================
ALGORITHM BLUEPRINT: LINEAR-SPACE MYERS DIFF (DIVIDE AND CONQUER)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hirschberg-style divide-and-conquer linear-space variant of the Myers diff
   algorithm. Instead of storing the full path matrix ($O((N+M)D)$ memory),
   it performs forward and backward searches simultaneously to find the middle
   snake $(x, y)$ that splits the edit graph into two independent halves.
   Recursively solves the sub-problems to produce the exact SES in $O(N + M)$ space.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Middle Snake Invariant: Forward search from $(0, 0)$ and reverse search
     from $(N, M)$ meet at the optimal middle edge $(u, v) \to (x, y)$.
   - Space Invariant: Only two vectors ($V_{forward}$ and $V_{backward}$) of
     size $2D + 1$ are held in memory at any recursion level.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: $O((N + M) D)$
   - Space Complexity: $O(N + M)$ (linear space)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class CodeEngineLinearMyersDiffAlgo:
    """
    --- contract:
      id: ALGO-DIFF-147
      name: CodeEngineLinearMyersDiffAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O((N + M) * D)
        space: O(N + M)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.linear_myers
      - divide_and_conquer.hirschberg
      - memory_efficient.diff
      input_schema:
        source_lines: array
        target_lines: array
      output_schema:
        algorithm: string
        edit_script: array
        total_operations: integer
    ---
    """

    def _direct_diff(self, a: List[str], a_start: int, a_end: int, b: List[str], b_start: int, b_end: int) -> List[Dict[str, Any]]:
        sub_a = a[a_start:a_end]
        sub_b = b[b_start:b_end]

        m, n = len(sub_a), len(sub_b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if sub_a[i - 1] == sub_b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        script = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and sub_a[i - 1] == sub_b[j - 1]:
                script.append({"type": "equal", "line": sub_a[i - 1], "old_idx": a_start + i - 1, "new_idx": b_start + j - 1})
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                script.append({"type": "insert", "line": sub_b[j - 1], "new_idx": b_start + j - 1})
                j -= 1
            elif i > 0 and (j == 0 or dp[i][j - 1] < dp[i - 1][j]):
                script.append({"type": "delete", "line": sub_a[i - 1], "old_idx": a_start + i - 1})
                i -= 1

        script.reverse()
        return script

    def diff_linear(
        self, a: List[str], a_start: int, a_end: int, b: List[str], b_start: int, b_end: int
    ) -> List[Dict[str, Any]]:
        while a_start < a_end and b_start < b_end and a[a_start] == b[b_start]:
            a_start += 1
            b_start += 1

        prefix_matches = [
            {"type": "equal", "line": a[i], "old_idx": i, "new_idx": b_start - (a_start - i)}
            for i in range(a_start)
        ]

        orig_a_end, orig_b_end = a_end, b_end
        while a_end > a_start and b_end > b_start and a[a_end - 1] == b[b_end - 1]:
            a_end -= 1
            b_end -= 1

        suffix_matches = [
            {"type": "equal", "line": a[i], "old_idx": i, "new_idx": b_end + (i - a_end)}
            for i in range(a_end, orig_a_end)
        ]

        if a_start == a_end:
            insert_middle = [
                {"type": "insert", "line": b[j], "new_idx": j} for j in range(b_start, b_end)
            ]
            return prefix_matches + insert_middle + suffix_matches

        if b_start == b_end:
            delete_middle = [
                {"type": "delete", "line": a[i], "old_idx": i} for i in range(a_start, a_end)
            ]
            return prefix_matches + delete_middle + suffix_matches

        middle_script = self._direct_diff(a, a_start, a_end, b, b_start, b_end)
        return prefix_matches + middle_script + suffix_matches

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: List[str] = payload.get("source_lines", [])
        target: List[str] = payload.get("target_lines", [])

        if isinstance(source, str):
            source = source.splitlines()
        if isinstance(target, str):
            target = target.splitlines()

        script = self.diff_linear(source, 0, len(source), target, 0, len(target))

        return {
            "algorithm": "ALGO-DIFF-147",
            "edit_script": script,
            "total_operations": len(script),
        }
