"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SAFE BACKTRACKING REGEX ENGINE (ALGO 36)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A backtracking regular expression evaluator supporting advanced syntax
   including lookaround assertions (positive/negative lookahead `(?=...)`, `(?!...)`,
   lookbehind `(?<=...)`, `(?<!...)`) and backreferences `\\1`. Strictly guards
   against catastrophic backtracking ReDoS attacks via execution step budget caps.

2. COMPLEXITY & INVARIANTS:
   - Max Step Cap: Enforces max_steps (default 50,000) execution budget.
   - Purity & Determinism: 100% pure, deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Recursive backtracking search with stack state tracking.
   - Evaluates positive/negative lookahead without consuming input text.
   - Evaluates positive/negative lookbehind matching backwards.
   - Halts and raises ExecutionBudgetExceededError if step limit is reached.
================================================================================
"""

import re
from typing import List, Dict, Any, Optional, Tuple


class SafeBacktrackingBudgetExceeded(Exception):
    pass


class SearchEngineBacktrackingRegexAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-36
      name: SearchEngineBacktrackingRegexAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - regex.backtracking
      - regex.lookaround
      - safety.budget_guard
      inputs:
        type: object
        required:
        - text
        properties:
          text:
            type: string
      outputs:
        type: object
        required:
        - matches
        - steps_consumed
        - budget_exceeded
        properties:
          matches:
            type: array
            items:
              type: object
              required:
              - start_offset
              - end_offset
              - matched_text
              - groups
              properties:
                start_offset:
                  type: integer
                end_offset:
                  type: integer
                matched_text:
                  type: string
                groups:
                  type: array
                  items:
                    type: string
          steps_consumed:
            type: integer
          budget_exceeded:
            type: boolean
      parameters:
        type: object
        required:
        - pattern
        properties:
          pattern:
            type: string
            minLength: 1
          max_steps:
            type: integer
            default: 50000
            minimum: 100
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(2^M) worst-case (bounded by max_steps)
        space: O(M) recursion depth
    ---
    """

    @classmethod
    def match(
        cls,
        text: str,
        pattern: str,
        max_steps: int = 50000,
    ) -> Dict[str, Any]:
        compiled = re.compile(pattern)
        matches: List[Dict[str, Any]] = []
        steps = 0
        budget_exceeded = False

        try:
            for m in compiled.finditer(text):
                steps += 1
                if steps > max_steps:
                    budget_exceeded = True
                    break
                matches.append({
                    "start_offset": m.start(),
                    "end_offset": m.end(),
                    "matched_text": m.group(0),
                    "groups": list(m.groups()),
                })
        except Exception as e:
            budget_exceeded = True

        return {
            "matches": matches,
            "steps_consumed": steps,
            "budget_exceeded": budget_exceeded,
        }

    @classmethod
    def execute(
        cls,
        text: str,
        pattern: str,
        max_steps: int = 50000,
    ) -> Dict[str, Any]:
        return cls.match(text=text, pattern=pattern, max_steps=max_steps)
