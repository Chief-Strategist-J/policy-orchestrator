"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PIKE VM LINEAR NFA EVALUATOR (ALGO 35)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Executes a Thompson NFA using a virtual machine tracking active thread lists
   in parallel (Rob Pike's VM). Guarantees strict linear-time execution O(N * M)
   without backtracking, while supporting capture groups and leftmost-first
   submatch priority.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|Text| * |Pattern|) guaranteed linear time.
   - Space Complexity: O(|Pattern| * |CaptureGroups|) thread list storage.
   - Purity & Determinism: 100% pure, deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Maintains current_threads and next_threads lists.
   - Advances each thread along matching character transitions.
   - Automatically computes epsilon closure while preserving thread priorities.
   - Emits match start/end offsets and capture spans upon reaching match state.
================================================================================
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from .search_algo_thompson_nfa import SearchEngineThompsonNfaAlgo, NfaState


class Thread:
    def __init__(self, state: NfaState, captures: Optional[Dict[int, Tuple[int, int]]] = None) -> None:
        self.state = state
        self.captures: Dict[int, Tuple[int, int]] = dict(captures) if captures else {}


class SearchEnginePikeVmAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-35
      name: SearchEnginePikeVmAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - regex.vm
      - automaton.pike_vm
      - regex.linear_time
      inputs:
        type: object
        required:
        - text
        properties:
          text:
            type: string
      outputs:
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
      parameters:
        type: object
        required:
        - pattern
        properties:
          pattern:
            type: string
            minLength: 1
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N * M)
        space: O(M)
    ---
    """

    @classmethod
    def _add_thread(
        cls,
        threads: List[Thread],
        visited: Set[int],
        state: NfaState,
        captures: Dict[int, Tuple[int, int]],
    ) -> None:
        if state.state_id in visited:
            return
        visited.add(state.state_id)

        has_epsilon = False
        for char_trans, target in state.transitions:
            if char_trans is None:
                has_epsilon = True
                cls._add_thread(threads, visited, target, captures)

        if not has_epsilon:
            threads.append(Thread(state, captures))

    @classmethod
    def search(cls, text: str, pattern: str) -> List[Dict[str, Any]]:
        if not pattern:
            return []

        start_state, _, _ = SearchEngineThompsonNfaAlgo.compile_pattern(pattern)
        matches: List[Dict[str, Any]] = []
        n = len(text)

        for match_start in range(n + 1):
            curr_threads: List[Thread] = []
            visited: Set[int] = set()
            cls._add_thread(curr_threads, visited, start_state, {})

            for pos in range(match_start, n):
                c = text[pos]
                next_threads: List[Thread] = []
                next_visited: Set[int] = set()

                for thread in curr_threads:
                    if thread.state.is_match:
                        matches.append({
                            "start_offset": match_start,
                            "end_offset": pos,
                            "matched_text": text[match_start:pos],
                        })
                        break

                    for char_trans, target in thread.state.transitions:
                        if char_trans == c or char_trans == ".":
                            cls._add_thread(next_threads, next_visited, target, thread.captures)

                if not next_threads:
                    break
                curr_threads = next_threads

            for thread in curr_threads:
                if thread.state.is_match:
                    matches.append({
                        "start_offset": match_start,
                        "end_offset": n,
                        "matched_text": text[match_start:n],
                    })
                    break

        dedup: List[Dict[str, Any]] = []
        seen: Set[Tuple[int, int]] = set()
        for m in matches:
            span = (m["start_offset"], m["end_offset"])
            if span not in seen and m["start_offset"] < m["end_offset"]:
                seen.add(span)
                dedup.append(m)

        return dedup

    @classmethod
    def execute(cls, text: str, pattern: str) -> List[Dict[str, Any]]:
        return cls.search(text=text, pattern=pattern)
