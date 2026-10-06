"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LEVENSHTEIN DYNAMIC PROGRAMMING DISTANCE (ALGO 27)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes the minimum edit distance (insertions, deletions, substitutions)
   between two strings using Wagner-Fischer dynamic programming. Supports full
   matrix generation and optimal alignment traceback reconstruction.

2. COMPLEXITY & INVARIANTS:
   - Full Matrix Time: O(|A| * |B|) | Space O(|A| * |B|).
   - Space-Optimized Time: O(|A| * |B|) | Space O(min(|A|, |B|)).
   - Zero-Inline-Comment Doctrine: Clean execution without inline comments.

3. EXECUTION FLOW:
   - Allocates DP table D of size (N+1) x (M+1).
   - Initializes base cases: D[i][0] = i * del_cost, D[0][j] = j * ins_cost.
   - Recurrence: D[i][j] = min(D[i-1][j] + del, D[i][j-1] + ins, D[i-1][j-1] + (0 if match else sub)).
   - Traceback reconstructs explicit list of edit operations: insert, delete, substitute, match.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class SearchEngineLevenshteinDistanceAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-27
      name: SearchEngineLevenshteinDistanceAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.fuzzy
      - edit_distance.dp
      - string.alignment
      inputs:
        type: object
        required:
        - source
        - target
        properties:
          source:
            type: string
          target:
            type: string
      outputs:
        type: object
        required:
        - distance
        - similarity_ratio
        - operations
        properties:
          distance:
            type: integer
            minimum: 0
          similarity_ratio:
            type: number
            minimum: 0.0
            maximum: 1.0
          operations:
            type: array
            items:
              type: object
              required:
              - type
              - source_pos
              - target_pos
              - char
              properties:
                type:
                  type: string
                  enum: [match, substitute, insert, delete]
                source_pos:
                  type: integer
                target_pos:
                  type: integer
                char:
                  type: string
      parameters:
        type: object
        properties:
          insert_cost:
            type: integer
            default: 1
          delete_cost:
            type: integer
            default: 1
          substitute_cost:
            type: integer
            default: 1
          include_matrix:
            type: boolean
            default: false
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N * M)
        space: O(N * M)
    ---
    """

    @classmethod
    def compute(
        cls,
        source: str,
        target: str,
        insert_cost: int = 1,
        delete_cost: int = 1,
        substitute_cost: int = 1,
        include_matrix: bool = False,
    ) -> Dict[str, Any]:
        n, m = len(source), len(target)
        dp = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i * delete_cost
        for j in range(m + 1):
            dp[0][j] = j * insert_cost

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if source[i - 1] == target[j - 1] else substitute_cost
                dp[i][j] = min(
                    dp[i - 1][j] + delete_cost,
                    dp[i][j - 1] + insert_cost,
                    dp[i - 1][j - 1] + cost,
                )

        distance = dp[n][m]
        max_len = max(n, m)
        similarity = 1.0 if max_len == 0 else max(0.0, 1.0 - (distance / max_len))

        operations = cls._traceback(source, target, dp, insert_cost, delete_cost, substitute_cost)

        result: Dict[str, Any] = {
            "distance": distance,
            "similarity_ratio": round(similarity, 4),
            "operations": operations,
        }

        if include_matrix:
            result["dp_matrix"] = dp

        return result

    @classmethod
    def _traceback(
        cls,
        source: str,
        target: str,
        dp: List[List[int]],
        insert_cost: int,
        delete_cost: int,
        substitute_cost: int,
    ) -> List[Dict[str, Any]]:
        i, j = len(source), len(target)
        ops: List[Dict[str, Any]] = []

        while i > 0 or j > 0:
            if i > 0 and j > 0:
                cost = 0 if source[i - 1] == target[j - 1] else substitute_cost
                if dp[i][j] == dp[i - 1][j - 1] + cost:
                    op_type = "match" if cost == 0 else "substitute"
                    ops.append({
                        "type": op_type,
                        "source_pos": i - 1,
                        "target_pos": j - 1,
                        "char": target[j - 1],
                    })
                    i -= 1
                    j -= 1
                    continue

            if i > 0 and dp[i][j] == dp[i - 1][j] + delete_cost:
                ops.append({
                    "type": "delete",
                    "source_pos": i - 1,
                    "target_pos": j,
                    "char": source[i - 1],
                })
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j - 1] + insert_cost:
                ops.append({
                    "type": "insert",
                    "source_pos": i,
                    "target_pos": j - 1,
                    "char": target[j - 1],
                })
                j -= 1
            else:
                break

        ops.reverse()
        return ops

    @classmethod
    def execute(
        cls,
        source: str,
        target: str,
        insert_cost: int = 1,
        delete_cost: int = 1,
        substitute_cost: int = 1,
        include_matrix: bool = False,
    ) -> Dict[str, Any]:
        return cls.compute(
            source=source,
            target=target,
            insert_cost=insert_cost,
            delete_cost=delete_cost,
            substitute_cost=substitute_cost,
            include_matrix=include_matrix,
        )
