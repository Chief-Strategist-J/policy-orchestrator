"""
================================================================================
ALGORITHM BLUEPRINT: WORD- AND CHARACTER-LEVEL DIFF REFINEMENT
================================================================================

1. OVERVIEW & OBJECTIVE:
   Takes paired line deletions and additions from a line-level diff and computes
   fine-grained token-level or character-level sub-diffs. Identifies exact
   in-place word mutations (e.g. `foo(a, b)` -> `foo(a, c)`) rather than
   presenting the entire line as deleted and replaced.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Word Tokenizer Invariant: Splits on whitespace and word boundaries `\b`
     while preserving whitespace tokens for faithful reconstruction.
   - LCS Sub-Matching: Computes LCS on intra-line word sequences to highlight
     exact changed substrings.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(W_old * W_new) per paired line where W is word count
   - Space Complexity: O(W_old * W_new)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, Any, List, Tuple


class CodeEngineWordCharRefinementAlgo:
    """
    --- contract:
      id: ALGO-DIFF-151
      name: CodeEngineWordCharRefinementAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(W1 * W2)
        space: O(W1 * W2)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.word_char_refinement
      - intra_line.word_diff
      - fine_grained.sub_hunks
      input_schema:
        old_line: string
        new_line: string
      output_schema:
        algorithm: string
        refined_spans: array
        similarity: float
    ---
    """

    WORD_SPLIT_REGEX = re.compile(r"(\w+|\s+|[^\w\s])")

    def tokenize_words(self, line: str) -> List[str]:
        return [m for m in self.WORD_SPLIT_REGEX.findall(line) if m]

    def compute_word_diff(self, old_line: str, new_line: str) -> List[Dict[str, Any]]:
        w_old = self.tokenize_words(old_line)
        w_new = self.tokenize_words(new_line)

        m, n = len(w_old), len(w_new)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if w_old[i - 1] == w_new[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        spans: List[Dict[str, Any]] = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and w_old[i - 1] == w_new[j - 1]:
                spans.append({"type": "equal", "text": w_old[i - 1]})
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                spans.append({"type": "insert", "text": w_new[j - 1]})
                j -= 1
            elif i > 0 and (j == 0 or dp[i][j - 1] < dp[i - 1][j]):
                spans.append({"type": "delete", "text": w_old[i - 1]})
                i -= 1

        spans.reverse()
        return spans

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        old_line: str = str(payload.get("old_line", ""))
        new_line: str = str(payload.get("new_line", ""))

        spans = self.compute_word_diff(old_line, new_line)
        matched = sum(len(s["text"]) for s in spans if s["type"] == "equal")
        total = max(len(old_line), len(new_line), 1)

        return {
            "algorithm": "ALGO-DIFF-151",
            "refined_spans": spans,
            "similarity": round(matched / total, 4),
        }
