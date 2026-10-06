"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FZF FUZZY SUBSEQUENCE SCORER (ALGO 32)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements an fzf-style fuzzy subsequence alignment and scoring algorithm.
   Evaluates how well a query string aligns as a subsequence within candidate
   file paths or symbol names, rewarding consecutive runs, word boundaries
   (slashes, underscores, hyphens, dots), and camelCase humps.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|Query| * |Target|) DP matrix scoring.
   - Space Complexity: O(|Query| * |Target|) for alignment matrix.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Function bodies are comment-free.

3. EXECUTION FLOW:
   - Verifies subsequence existence; if not a subsequence, returns score 0 / no match.
   - Computes dynamic programming score matrix S[i][j]:
     * Character match bonus: base score.
     * Boundary bonus: +8 if preceding character is '/', '_', '-', '.', space.
     * CamelCase bonus: +7 if current char is uppercase and previous is lowercase.
     * Consecutive match bonus: +10 per consecutive character run.
     * Gap penalty: -3 leading gap, -1 middle gap.
   - Extracts optimal alignment match positions and sorts candidates by score.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class SearchEngineFzfFuzzyAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-32
      name: SearchEngineFzfFuzzyAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.fuzzy
      - scoring.subsequence
      - path.matcher
      inputs:
        type: object
        required:
        - candidates
        - query
        properties:
          candidates:
            type: array
            items:
              type: string
          query:
            type: string
      outputs:
        type: array
        items:
          type: object
          required:
          - candidate
          - score
          - match_positions
          properties:
            candidate:
              type: string
            score:
              type: integer
            match_positions:
              type: array
              items:
                type: integer
      parameters:
        type: object
        properties:
          case_sensitive:
            type: boolean
            default: false
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N * |Query| * |Target|)
        space: O(|Query| * |Target|)
    ---
    """

    BONUS_BOUNDARY = 8
    BONUS_CAMEL = 7
    BONUS_CONSECUTIVE = 10
    BONUS_FIRST_CHAR = 6
    PENALTY_GAP_START = -3
    PENALTY_GAP_EXTENSION = -1

    @classmethod
    def _is_boundary(cls, prev_char: str) -> bool:
        return prev_char in "/_-. :\\"

    @classmethod
    def _is_camel_hump(cls, curr_char: str, prev_char: str) -> bool:
        return curr_char.isupper() and prev_char.islower()

    @classmethod
    def score_candidate(
        cls,
        query: str,
        target: str,
        case_sensitive: bool = False,
    ) -> Optional[Tuple[int, List[int]]]:
        if not query:
            return 0, []

        q_norm = query if case_sensitive else query.lower()
        t_norm = target if case_sensitive else target.lower()

        q_len = len(q_norm)
        t_len = len(t_norm)

        if q_len > t_len:
            return None

        t_idx = 0
        for q_char in q_norm:
            found = t_norm.find(q_char, t_idx)
            if found == -1:
                return None
            t_idx = found + 1

        dp = [[-100000] * (t_len + 1) for _ in range(q_len + 1)]
        consec = [[0] * (t_len + 1) for _ in range(q_len + 1)]

        dp[0][0] = 0
        for j in range(1, t_len + 1):
            dp[0][j] = 0

        for i in range(1, q_len + 1):
            for j in range(i, t_len + 1):
                if q_norm[i - 1] == t_norm[j - 1]:
                    char_bonus = 10
                    if j == 1:
                        char_bonus += cls.BONUS_FIRST_CHAR
                    else:
                        prev_t = target[j - 2]
                        curr_t = target[j - 1]
                        if cls._is_boundary(prev_t):
                            char_bonus += cls.BONUS_BOUNDARY
                        elif cls._is_camel_hump(curr_t, prev_t):
                            char_bonus += cls.BONUS_CAMEL

                    prev_consec = consec[i - 1][j - 1]
                    if prev_consec > 0:
                        char_bonus += cls.BONUS_CONSECUTIVE * prev_consec

                    match_score = dp[i - 1][j - 1] + char_bonus
                    gap_score = dp[i][j - 1] + (cls.PENALTY_GAP_START if consec[i][j - 1] == 0 else cls.PENALTY_GAP_EXTENSION)

                    if match_score >= gap_score:
                        dp[i][j] = match_score
                        consec[i][j] = prev_consec + 1
                    else:
                        dp[i][j] = gap_score
                        consec[i][j] = 0
                else:
                    dp[i][j] = dp[i][j - 1] + (cls.PENALTY_GAP_START if consec[i][j - 1] == 0 else cls.PENALTY_GAP_EXTENSION)
                    consec[i][j] = 0

        best_score = max(dp[q_len][j] for j in range(q_len, t_len + 1))
        if best_score <= -50000:
            return None

        positions: List[int] = []
        curr_i = q_len
        curr_j = t_len

        while curr_i > 0 and curr_j > 0:
            if q_norm[curr_i - 1] == t_norm[curr_j - 1] and dp[curr_i][curr_j] == max(dp[curr_i][k] for k in range(curr_i, curr_j + 1)):
                positions.append(curr_j - 1)
                curr_i -= 1
                curr_j -= 1
            else:
                curr_j -= 1

        positions.reverse()
        if len(positions) != q_len:
            positions = []
            c_idx = 0
            for q_char in q_norm:
                c_idx = t_norm.find(q_char, c_idx)
                positions.append(c_idx)
                c_idx += 1

        return best_score, positions

    @classmethod
    def execute(
        cls,
        candidates: List[str],
        query: str,
        case_sensitive: bool = False,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for candidate in candidates:
            res = cls.score_candidate(query, candidate, case_sensitive)
            if res is not None:
                score, positions = res
                results.append({
                    "candidate": candidate,
                    "score": score,
                    "match_positions": positions,
                })

        results.sort(key=lambda x: (x["score"], -len(x["candidate"])), reverse=True)
        return results
