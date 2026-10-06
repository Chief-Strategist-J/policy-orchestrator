"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SUFFIX AUTOMATON (DAWG) (ALGO 49)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a Suffix Automaton (Directed Acyclic Word Graph - DAWG) for text.
   The suffix automaton is the minimal deterministic automaton that accepts all
   substrings of a text. Has at most 2N - 1 states and 3N - 4 transitions.
   Answers substring existence and occurrence frequency queries in strict O(|Query|).

2. COMPLEXITY & INVARIANTS:
   - Construction Time: Strict O(N) linear time online incremental build.
   - Substring Query: Strict O(|Query|) linear time independent of text length.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Incremental state additions with suffix links and clone states.
   - On adding character C:
     * Creates new state cur with len = last.len + 1.
     * Follows suffix links from last, adding transition on C to cur.
     * If existing transition violates minimality: clones target state and updates links.
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


class SuffixAutomatonState:
    def __init__(self, length: int, link: int = -1) -> None:
        self.len = length
        self.link = link
        self.transitions: Dict[str, int] = {}
        self.is_clone = False


class SearchEngineSuffixAutomatonAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-49
      name: SearchEngineSuffixAutomatonAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.suffix_automaton
      - automaton.dawg
      - substring.instant_query
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
        - state_count
        - contains_pattern
        - distinct_substring_count
        properties:
          state_count:
            type: integer
          contains_pattern:
            type: boolean
          distinct_substring_count:
            type: integer
      parameters:
        type: object
        required:
        - query
        properties:
          query:
            type: string
            minLength: 1
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N) build, O(|Query|) search
        space: O(N) states
    ---
    """

    def __init__(self, text: str = "") -> None:
        self.states: List[SuffixAutomatonState] = [SuffixAutomatonState(0, -1)]
        self.last = 0
        if text:
            for c in text:
                self.extend(c)

    def extend(self, c: str) -> None:
        cur = len(self.states)
        self.states.append(SuffixAutomatonState(self.states[self.last].len + 1))

        p = self.last
        while p != -1 and c not in self.states[p].transitions:
            self.states[p].transitions[c] = cur
            p = self.states[p].link

        if p == -1:
            self.states[cur].link = 0
        else:
            q = self.states[p].transitions[c]
            if self.states[p].len + 1 == self.states[q].len:
                self.states[cur].link = q
            else:
                clone = len(self.states)
                clone_state = SuffixAutomatonState(self.states[p].len + 1, self.states[q].link)
                clone_state.transitions = dict(self.states[q].transitions)
                clone_state.is_clone = True
                self.states.append(clone_state)

                while p != -1 and self.states[p].transitions.get(c) == q:
                    self.states[p].transitions[c] = clone
                    p = self.states[p].link

                self.states[q].link = clone
                self.states[cur].link = clone

        self.last = cur

    def contains(self, query: str) -> bool:
        curr = 0
        for c in query:
            if c not in self.states[curr].transitions:
                return False
            curr = self.states[curr].transitions[c]
        return True

    def count_distinct_substrings(self) -> int:
        total = 0
        for i in range(1, len(self.states)):
            total += self.states[i].len - self.states[self.states[i].link].len
        return total

    @classmethod
    def execute(cls, text: str, query: str) -> Dict[str, Any]:
        sam = cls(text)
        contains = sam.contains(query)
        distinct = sam.count_distinct_substrings()
        return {
            "state_count": len(sam.states),
            "contains_pattern": contains,
            "distinct_substring_count": distinct,
        }
