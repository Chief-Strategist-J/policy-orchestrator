"""
================================================================================
ALGORITHM BLUEPRINT: ERROR-FEEDBACK RETRY (COMPILER/LINTER FEEDBACK CONVERGENCE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Feeds structured compiler, linter, or test failure diagnostics back into the
   agent's refinement pipeline. Parses compiler error outputs (file, line, col,
   error code, message), tracks failure signatures across iterative attempts,
   enforces retry budgets, and detects error loops/thrashing to trigger safe
   rollback and escalation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Budget Enforcement: Strict max-attempts ceiling (default 3); raises threshold
     escalation when exceeded.
   - Loop & Stagnation Detection: Identifies recurring identical errors across
     successive attempts to prevent degradation.
   - Purity: Operates as deterministic state tracker and diagnostic analyzer.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Log_Length + History_Size)
   - Space Complexity: O(History_Size)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, Any, List, Optional


class CodeEngineErrorFeedbackRetryAlgo:
    """
    --- contract:
      id: ALGO-ATMC-201
      name: CodeEngineErrorFeedbackRetryAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(N)
        space: O(H)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - error_feedback.retry
      - diagnostic.parser
      - convergence.guard
      input_schema:
        error_output: string
        attempt_history: array
        max_attempts: integer
      output_schema:
        algorithm: string
        parsed_errors: array
        can_retry: boolean
        exhausted_budget: boolean
        detected_loop: boolean
        recommendation: string
        error_signature: string
    ---
    """

    ERROR_PATTERNS = [
        re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+)?:\s*(?:error|warning|fatal):\s*(?P<msg>.+)$", re.MULTILINE),
        re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):\s*(?P<msg>.+)$", re.MULTILINE),
        re.compile(r"File \"(?P<file>[^\"]+)\", line (?P<line>\d+).*?\n(?P<msg>[A-Za-z0-9_]+Error: .*)$", re.MULTILINE),
    ]

    def parse_diagnostics(self, error_output: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        lines = error_output.strip().splitlines()
        for line in lines:
            matched = False
            for pat in self.ERROR_PATTERNS:
                m = pat.match(line)
                if m:
                    d = m.groupdict()
                    results.append({
                        "file": d.get("file", "").strip(),
                        "line": int(d.get("line", 0)) if d.get("line") else 0,
                        "col": int(d.get("col", 0)) if d.get("col") else 0,
                        "message": d.get("msg", "").strip(),
                    })
                    matched = True
                    break
            if not matched and "Error:" in line:
                results.append({
                    "file": "unknown",
                    "line": 0,
                    "col": 0,
                    "message": line.strip(),
                })
        if not results and error_output.strip():
            results.append({
                "file": "unknown",
                "line": 0,
                "col": 0,
                "message": error_output.strip().splitlines()[-1],
            })
        return results

    def evaluate_retry_state(
        self,
        error_output: str,
        attempt_history: List[Dict[str, Any]],
        max_attempts: int = 3,
    ) -> Dict[str, Any]:
        parsed = self.parse_diagnostics(error_output)
        error_sig = "|".join([f"{e['file']}:{e['line']}:{e['message']}" for e in parsed])
        current_attempt = len(attempt_history) + 1

        past_signatures = [h.get("signature", "") for h in attempt_history]
        identical_repetitions = past_signatures.count(error_sig)
        detected_loop = identical_repetitions >= 2

        exhausted = current_attempt >= max_attempts
        can_retry = (not exhausted) and (not detected_loop) and bool(parsed)

        if not parsed:
            rec = "SUCCESS_NO_ERRORS"
        elif detected_loop:
            rec = "ABORT_AND_ROLLBACK_DETECTED_LOOP"
        elif exhausted:
            rec = "ABORT_EXHAUSTED_ATTEMPT_BUDGET"
        else:
            rec = "APPLY_TARGETED_FIX_AND_RETRY"

        return {
            "algorithm": "ALGO-ATMC-201",
            "parsed_errors": parsed,
            "attempt_number": current_attempt,
            "can_retry": can_retry,
            "exhausted_budget": exhausted,
            "detected_loop": detected_loop,
            "recommendation": rec,
            "error_signature": error_sig,
        }
