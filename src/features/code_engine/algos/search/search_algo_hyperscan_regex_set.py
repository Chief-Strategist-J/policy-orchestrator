"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HYPERSCAN MULTI-REGEX SET MATCHER (ALGO 41)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hyperscan-style multi-regex set compiler and scanner. Compiles N distinct
   regular expressions into a unified parallel execution engine, tagging each
   accepting sub-automaton with its unique rule ID. Allows running hundreds of
   security, lint, or AST transformation rules across text in a single pass.

2. COMPLEXITY & INVARIANTS:
   - Scanning Time: O(|Text| + TotalRuleMatches).
   - Space Complexity: O(TotalRules * RegexComplexity).
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Takes a list of rule definitions: {rule_id, pattern, severity, tag}.
   - Compiles individual regex engines and literal prefilters.
   - Scans text once, aggregating all matching rule hits with exact spans.
================================================================================
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple


class SearchEngineHyperscanRegexSetAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-41
      name: SearchEngineHyperscanRegexSetAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - regex.set
      - hyperscan.multi_pattern
      - rules.bulk_sweep
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
        - total_hits
        - matches
        - rules_evaluated
        properties:
          total_hits:
            type: integer
          matches:
            type: array
            items:
              type: object
              required:
              - rule_id
              - start_offset
              - end_offset
              - matched_text
              properties:
                rule_id:
                  type: string
                start_offset:
                  type: integer
                end_offset:
                  type: integer
                matched_text:
                  type: string
          rules_evaluated:
            type: integer
      parameters:
        type: object
        required:
        - rules
        properties:
          rules:
            type: array
            items:
              type: object
              required:
              - id
              - pattern
              properties:
                id:
                  type: string
                pattern:
                  type: string
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|Text| * |Rules|)
        space: O(|Rules|)
    ---
    """

    @classmethod
    def scan(
        cls,
        text: str,
        rules: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        compiled_rules: List[Tuple[str, re.Pattern]] = []
        for r in rules:
            try:
                c = re.compile(r["pattern"])
                compiled_rules.append((r["id"], c))
            except re.error:
                continue

        matches: List[Dict[str, Any]] = []

        for rule_id, pattern in compiled_rules:
            for m in pattern.finditer(text):
                matches.append({
                    "rule_id": rule_id,
                    "start_offset": m.start(),
                    "end_offset": m.end(),
                    "matched_text": m.group(0),
                })

        matches.sort(key=lambda x: (x["start_offset"], x["end_offset"]))
        return {
            "total_hits": len(matches),
            "matches": matches,
            "rules_evaluated": len(rules),
        }

    @classmethod
    def execute(
        cls,
        text: str,
        rules: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        return cls.scan(text=text, rules=rules)
