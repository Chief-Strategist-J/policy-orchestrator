"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LEVENSHTEIN AUTOMATON (ALGO 29)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a deterministic parametric automaton that accepts all strings
   within Levenshtein edit distance K of a target string. Allows checking
   candidate strings or traversing tries / FST dictionaries in O(|Candidate|)
   time per candidate without per-character DP tables.

2. COMPLEXITY & INVARIANTS:
   - State Complexity: State count depends on K and |Pattern|, bounded by O(|Pattern| * K).
   - Traversal Time: O(|Candidate|) linear per test word.
   - Purity & Determinism: 100% pure, deterministic.
   - Zero-Inline-Comment Doctrine: Function bodies are comment-free.

3. EXECUTION FLOW:
   - State representation: set of tuples (pattern_pos, errors_spent).
   - Start state: {(0, 0), (0, 1), ..., (0, k)}.
   - On character 'c':
     * Exact match: (i+1, e) if pattern[i] == c.
     * Deletion (in target): (i+1, e+1).
     * Insertion (in target): (i, e+1).
     * Substitution: (i+1, e+1).
   - Closes states by adding subsequent insertion/deletion transitions where e <= k.
   - Accepts if any state in active set has pattern_pos == |Pattern|.
================================================================================
"""

from typing import List, Dict, Any, Set, Tuple, Optional


class LevenshteinAutomatonState:
    def __init__(self, positions: Set[Tuple[int, int]]) -> None:
        self.positions: Set[Tuple[int, int]] = frozenset(positions)

    def is_match(self, pattern_len: int) -> bool:
        return any(pos == pattern_len for pos, err in self.positions)

    def min_errors(self, pattern_len: int) -> Optional[int]:
        matching_errs = [err for pos, err in self.positions if pos == pattern_len]
        return min(matching_errs) if matching_errs else None


class SearchEngineLevenshteinAutomatonAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-29
      name: SearchEngineLevenshteinAutomatonAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.fuzzy
      - automaton.levenshtein
      - dictionary.filtering
      inputs:
        type: object
        required:
        - candidates
        properties:
          candidates:
            type: array
            items:
              type: string
      outputs:
        type: array
        items:
          type: object
          required:
          - candidate
          - distance
          - accepted
          properties:
            candidate:
              type: string
            distance:
              type: integer
            accepted:
              type: boolean
      parameters:
        type: object
        required:
        - pattern
        properties:
          pattern:
            type: string
            minLength: 1
          max_distance:
            type: integer
            default: 2
            minimum: 0
            maximum: 5
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(TotalCandidateChars)
        space: O(|Pattern| * K)
    ---
    """

    def __init__(self, pattern: str, max_distance: int = 2) -> None:
        self.pattern = pattern
        self.k = max_distance
        self.p_len = len(pattern)

    def _start_state(self) -> LevenshteinAutomatonState:
        positions: Set[Tuple[int, int]] = set()
        for err in range(self.k + 1):
            positions.add((0, err))
        return LevenshteinAutomatonState(positions)

    def _step(self, state: LevenshteinAutomatonState, char: str) -> LevenshteinAutomatonState:
        new_positions: Set[Tuple[int, int]] = set()

        for pos, err in state.positions:
            if pos < self.p_len:
                if self.pattern[pos] == char:
                    new_positions.add((pos + 1, err))
                else:
                    if err < self.k:
                        new_positions.add((pos + 1, err + 1))
                        new_positions.add((pos, err + 1))
                        new_positions.add((pos + 1, err + 1))
            else:
                if err < self.k:
                    new_positions.add((pos, err + 1))

        closure: Set[Tuple[int, int]] = set(new_positions)
        changed = True
        while changed:
            changed = False
            additions: Set[Tuple[int, int]] = set()
            for pos, err in closure:
                if pos < self.p_len and err < self.k:
                    candidate = (pos + 1, err + 1)
                    if candidate not in closure:
                        additions.add(candidate)
                        changed = True
            closure.update(additions)

        return LevenshteinAutomatonState(closure)

    def evaluate_word(self, word: str) -> Tuple[bool, Optional[int]]:
        state = self._start_state()
        for char in word:
            state = self._step(state, char)
            if not state.positions:
                return False, None

        min_err = state.min_errors(self.p_len)
        if min_err is not None and min_err <= self.k:
            return True, min_err
        return False, None

    @classmethod
    def filter_candidates(
        cls,
        pattern: str,
        candidates: List[str],
        max_distance: int = 2,
    ) -> List[Dict[str, Any]]:
        automaton = cls(pattern=pattern, max_distance=max_distance)
        results: List[Dict[str, Any]] = []

        for candidate in candidates:
            accepted, dist = automaton.evaluate_word(candidate)
            if accepted and dist is not None:
                results.append({
                    "candidate": candidate,
                    "distance": dist,
                    "accepted": True,
                })

        results.sort(key=lambda x: (x["distance"], len(x["candidate"])))
        return results

    @classmethod
    def execute(
        cls,
        pattern: str,
        candidates: List[str],
        max_distance: int = 2,
    ) -> List[Dict[str, Any]]:
        return cls.filter_candidates(
            pattern=pattern,
            candidates=candidates,
            max_distance=max_distance,
        )
