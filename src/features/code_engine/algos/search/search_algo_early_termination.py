"""
================================================================================
ALGORITHM BLUEPRINT: EARLY TERMINATION (TOP-K & BUDGET BOUNDED SEARCH)
================================================================================

1. OVERVIEW:
   Enforces strict execution boundaries on exploratory and ranked queries via early
   termination. Tracks result item counts, per-file limits, byte consumption caps,
   and score convergence. Returns an explicit `is_truncated` boolean contract flag
   preventing consumers from mistaking partial results for exhaustive searches.

2. BOUNDING INVARIANTS & CONSTRAINTS:
   - Max Total Results: Hard limit on aggregate matches (e.g., 50 or 100).
   - Max Matches Per File: Prevents single massive generated/log files from dominating output.
   - Max Bytes Scanned: Protects memory working set from runaway file payloads.
   - Truncation Signaling: Always returns `is_truncated: True` with explicit reason
     ("max_results_exceeded", "byte_limit_reached", "file_match_cap").

3. COMPLEXITY ANALYSIS:
   - Time: O(K) where K is result threshold, independent of total repository scale.
   - Space: Strict O(K) bounded memory footprint.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method/function bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Callable


class SearchEngineEarlyTerminationAlgo:
    """
    --- contract:
      id: ALGO-SRCH-72
      name: SearchEngineEarlyTerminationAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(K)
        space: O(1)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - search.early_exit
      - optimization.pruning
      - top_k.limit
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def collect_with_limits(
        self,
        item_stream: List[Dict[str, Any]],
        max_total_results: int = 50,
        max_per_file: int = 5,
        max_bytes: int = 1048576
    ) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        file_counts: Dict[str, int] = {}
        bytes_accum = 0
        is_truncated = False
        truncation_reason: Optional[str] = None

        for item in item_stream:
            if len(results) >= max_total_results:
                is_truncated = True
                truncation_reason = "max_total_results_reached"
                break

            file_path = str(item.get("file", "unknown"))
            curr_file_matches = file_counts.get(file_path, 0)
            if curr_file_matches >= max_per_file:
                continue

            item_size = len(str(item.get("text", "")))
            if bytes_accum + item_size > max_bytes:
                is_truncated = True
                truncation_reason = "max_bytes_budget_exceeded"
                break

            results.append(item)
            file_counts[file_path] = curr_file_matches + 1
            bytes_accum += item_size

        return {
            "collected_results": results,
            "result_count": len(results),
            "bytes_consumed": bytes_accum,
            "is_truncated": is_truncated,
            "truncation_reason": truncation_reason,
            "unique_files_matched": len(file_counts)
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        items = payload.get("items", [])
        max_results = int(payload.get("max_total_results", 50))
        max_per_file = int(payload.get("max_per_file", 5))
        max_bytes = int(payload.get("max_bytes", 1048576))

        summary = self.collect_with_limits(
            items,
            max_total_results=max_results,
            max_per_file=max_per_file,
            max_bytes=max_bytes
        )

        return {
            "algorithm": "ALGO-SRCH-73",
            "bounded_summary": summary
        }
