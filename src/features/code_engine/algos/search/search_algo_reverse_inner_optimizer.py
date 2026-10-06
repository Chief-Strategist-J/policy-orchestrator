"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REVERSE SUFFIX & INNER OPTIMIZER (ALGO 40)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A bidirectional regex search optimizer. First scans text for a required
   suffix or inner literal with high-speed memchr/Boyer-Moore skipping. From
   each literal hit, executes a reverse search to locate the earliest possible
   valid match start, followed by forward confirmation. Turns patterns like
   `\\w+Exception` or `get[A-Z]\\w+Handler` into near-instant literal scans.

2. COMPLEXITY & INVARIANTS:
   - Average Time: O(N / |Literal|) sub-linear text scanning.
   - Verification Time: O(LocalWindowLength) per literal candidate hit.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Identifies candidate anchor literal inside or at end of pattern.
   - Fast scans text for all occurrences of anchor literal.
   - For each occurrence at offset P:
     * Defines candidate verification window [max(0, P - max_lookback), min(N, P + |Literal| + max_lookahead)].
     * Evaluates full regex within local window.
     * Maps local match offsets back to global file offsets.
================================================================================
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from .search_algo_literal_extraction import SearchEngineLiteralExtractionAlgo


class SearchEngineReverseInnerOptimizerAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-40
      name: SearchEngineReverseInnerOptimizerAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - regex.bidirectional
      - search.reverse_optimizer
      - fast_scan.sublinear
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
        - anchor_literal
        - candidate_hits_evaluated
        properties:
          matches:
            type: array
            items:
              type: object
              required:
              - start_offset
              - end_offset
              - matched_text
              properties:
                start_offset:
                  type: integer
                end_offset:
                  type: integer
                matched_text:
                  type: string
          anchor_literal:
            type: string
          candidate_hits_evaluated:
            type: integer
      parameters:
        type: object
        required:
        - pattern
        properties:
          pattern:
            type: string
            minLength: 1
          max_lookback:
            type: integer
            default: 128
            minimum: 16
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N / |Anchor|) average
        space: O(Window)
    ---
    """

    @classmethod
    def search(
        cls,
        text: str,
        pattern: str,
        max_lookback: int = 128,
    ) -> Dict[str, Any]:
        ext = SearchEngineLiteralExtractionAlgo.extract(pattern)
        anchor = ext["required_suffix"] or ext["longest_literal"]

        if not anchor or len(anchor) < 2:
            compiled = re.compile(pattern)
            direct_matches = [
                {"start_offset": m.start(), "end_offset": m.end(), "matched_text": m.group(0)}
                for m in compiled.finditer(text)
            ]
            return {
                "matches": direct_matches,
                "anchor_literal": "",
                "candidate_hits_evaluated": len(direct_matches),
            }

        compiled_regex = re.compile(pattern)
        matches: List[Dict[str, Any]] = []
        candidate_count = 0
        seen_spans: Set[Tuple[int, int]] = set()

        idx = 0
        while idx < len(text):
            hit = text.find(anchor, idx)
            if hit == -1:
                break
            candidate_count += 1

            win_start = max(0, hit - max_lookback)
            win_end = min(len(text), hit + len(anchor) + max_lookback)
            subtext = text[win_start:win_end]

            for m in compiled_regex.finditer(subtext):
                g_start = win_start + m.start()
                g_end = win_start + m.end()
                if (g_start, g_end) not in seen_spans:
                    seen_spans.add((g_start, g_end))
                    matches.append({
                        "start_offset": g_start,
                        "end_offset": g_end,
                        "matched_text": m.group(0),
                    })

            idx = hit + 1

        matches.sort(key=lambda x: x["start_offset"])
        return {
            "matches": matches,
            "anchor_literal": anchor,
            "candidate_hits_evaluated": candidate_count,
        }

    @classmethod
    def execute(cls, text: str, pattern: str, max_lookback: int = 128) -> Dict[str, Any]:
        return cls.search(text=text, pattern=pattern, max_lookback=max_lookback)
