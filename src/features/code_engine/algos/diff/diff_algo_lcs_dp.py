"""
================================================================================
ALGORITHM BLUEPRINT: LONGEST COMMON SUBSEQUENCE (LCS DYNAMIC PROGRAMMING DIFF)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates the Longest Common Subsequence between two sequence arrays
   (or line lists) A and B using dynamic programming with matrix memoization.
   Constructs the minimal edit script (insertions, deletions, and equalities)
   by backtracking along the optimal path in the DP grid.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Recurrence Invariant:
     If A[i] == B[j]: LCS[i, j] = 1 + LCS[i-1, j-1]
     Else: LCS[i, j] = max(LCS[i-1, j], LCS[i, j-1])
   - Backtracking Determinism: Backtracks from (len(A), len(B)) down to (0, 0)
     to yield exact sequence transformations.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(M * N) where M = len(A), N = len(B)
   - Space Complexity: O(M * N) for table reconstruction
   - Suitable for small-to-medium files or token-level sub-diffs.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Tuple


class CodeEngineLcsDpDiffAlgo:
    """
    --- contract:
      id: ALGO-DIFF-145
      name: CodeEngineLcsDpDiffAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(M * N)
        space: O(M * N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.lcs_dp
      - sequence.longest_common_subsequence
      - text.edit_script
      input_schema:
        source_lines: array
        target_lines: array
      output_schema:
        algorithm: string
        lcs_length: integer
        edit_script: array
        similarity_ratio: float
    ---
    """

    def compute_lcs_table(self, a: List[str], b: List[str]) -> List[List[int]]:
        m: int = len(a)
        n: int = len(b)
        dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp

    def backtrack_diff(self, dp: List[List[int]], a: List[str], b: List[str]) -> List[Dict[str, Any]]:
        i: int = len(a)
        j: int = len(b)
        script: List[Dict[str, Any]] = []

        while i > 0 or j > 0:
            if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
                script.append({"type": "equal", "line": a[i - 1], "old_idx": i - 1, "new_idx": j - 1})
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                script.append({"type": "insert", "line": b[j - 1], "new_idx": j - 1})
                j -= 1
            elif i > 0 and (j == 0 or dp[i][j - 1] < dp[i - 1][j]):
                script.append({"type": "delete", "line": a[i - 1], "old_idx": i - 1})
                i -= 1

        script.reverse()
        return script

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: List[str] = payload.get("source_lines", [])
        target: List[str] = payload.get("target_lines", [])

        if isinstance(source, str):
            source = source.splitlines()
        if isinstance(target, str):
            target = target.splitlines()

        dp = self.compute_lcs_table(source, target)
        lcs_len: int = dp[len(source)][len(target)]
        edit_script = self.backtrack_diff(dp, source, target)

        total_lines = len(source) + len(target)
        similarity = (2.0 * lcs_len) / total_lines if total_lines > 0 else 1.0

        return {
            "algorithm": "ALGO-DIFF-145",
            "lcs_length": lcs_len,
            "edit_script": edit_script,
            "similarity_ratio": round(similarity, 4),
        }
