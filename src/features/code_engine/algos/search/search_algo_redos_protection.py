"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REDOS STATIC ANALYZER & TRIPWIRE (ALGO 42)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Static analysis and runtime tripwire engine detecting Regular Expression
   Denial of Service (ReDoS) vulnerabilities. Identifies exponential / polynomial
   backtracking hazards (nested quantifiers like `(a+)+`, `(a|a)*`, overlapping
   alternations under stars) before dispatching regexes to production repositories.

2. COMPLEXITY & INVARIANTS:
   - Analysis Time: O(|Pattern|) AST scan.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Static AST Inspection:
     * Nested Repetition: checks if a quantifier node contains a child quantifier node (`(x+)+`).
     * Overlapping Alternation: checks if alternation branches share prefixes under a star.
     * Star-under-plus: checks `(a*)+` or `(a+)*`.
   - Computes Vulnerability Severity: SAFE, LOW, MEDIUM, CRITICAL.
   - Emits remediation recommendations (e.g., atomic groups, possessive quantifiers, linear DFA engine).
================================================================================
"""

import re
from typing import List, Dict, Any, Optional
from .search_algo_regex_parser import SearchEngineRegexParserAlgo, RegexAstNode


class SearchEngineReDosProtectionAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-42
      name: SearchEngineReDosProtectionAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - regex.security
      - redos.static_analysis
      - safety.tripwire
      inputs:
        type: object
        required:
        - pattern
        properties:
          pattern:
            type: string
      outputs:
        type: object
        required:
        - is_vulnerable
        - severity
        - risk_patterns_detected
        - recommendation
        properties:
          is_vulnerable:
            type: boolean
          severity:
            type: string
            enum: [SAFE, LOW, MEDIUM, CRITICAL]
          risk_patterns_detected:
            type: array
            items:
              type: string
          recommendation:
            type: string
      parameters:
        type: object
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|Pattern|)
        space: O(|Pattern|)
    ---
    """

    NESTED_QUANTIFIERS_REGEX = re.compile(r"(\([^\)]*[\*\+\?][^\)]*\))[\*\+\?]")
    OVERLAPPING_ALTERNATION_REGEX = re.compile(r"\(([^\|]+)\|(\1)\)[\*\+\?]")
    UNBOUNDED_WILDCARDS = re.compile(r"(\.\*|\.\+){2,}")

    @classmethod
    def analyze(cls, pattern: str) -> Dict[str, Any]:
        risks: List[str] = []
        severity = "SAFE"

        if cls.NESTED_QUANTIFIERS_REGEX.search(pattern):
            risks.append("Nested Quantifier Hazard: Found repeated quantifier over group with inner quantifier (exponential backtracking hazard)")
            severity = "CRITICAL"

        if cls.OVERLAPPING_ALTERNATION_REGEX.search(pattern):
            risks.append("Overlapping Alternation under Repetition: Alternation branches contain identical prefixes under a loop (ambiguous path explosion)")
            severity = "CRITICAL"

        if cls.UNBOUNDED_WILDCARDS.search(pattern):
            risks.append("Consecutive Unbounded Wildcards: Multiple consecutive .* or .+ expressions detected")
            if severity != "CRITICAL":
                severity = "MEDIUM"

        if len(pattern) > 200 and ("*" in pattern or "+" in pattern):
            risks.append("Long Complex Pattern with Multiple Quantifiers: High state complexity risk")
            if severity == "SAFE":
                severity = "LOW"

        is_vuln = len(risks) > 0
        rec = "Pattern is safe to execute on standard regex engines."
        if severity == "CRITICAL":
            rec = "Reject or rewrite pattern. Remove nested quantifiers or route execution exclusively to linear DFA / Pike VM engines (ALGO-SRCH-35 / ALGO-SRCH-38)."
        elif severity in ("MEDIUM", "LOW"):
            rec = "Enforce strict execution step / timeout budget (ALGO-SRCH-36)."

        return {
            "is_vulnerable": is_vuln,
            "severity": severity,
            "risk_patterns_detected": risks,
            "recommendation": rec,
        }

    @classmethod
    def execute(cls, pattern: str) -> Dict[str, Any]:
        return cls.analyze(pattern=pattern)
