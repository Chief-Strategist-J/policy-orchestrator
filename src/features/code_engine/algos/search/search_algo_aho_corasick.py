"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AHO-CORASICK MULTI-PATTERN SCANNER (ALGO 11)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Deterministic Finite Automaton (DFA) / Trie with failure transitions that
   searches an arbitrary dictionary of N keyword patterns across text in a single
   linear O(TextLength) scan.

2. COMPLEXITY & INVARIANTS:
   - Trie Build: Time O(Σ PatternLengths) | Space O(TotalTrieNodes).
   - Search: Time O(TextLength + TotalMatchesFound).
   - Rules Enforced: R1 (Read Before Write), R5 (Resource Caps).

3. EXECUTION FLOW:
   Constructs a prefix trie of all invariant patterns. Computes BFS failure
   links. Steps through input characters, following transitions and outputting
   all matched patterns with exact start/end offsets.
================================================================================
"""

from collections import deque
from typing import List, Dict, Any, Tuple, Optional

class AhoCorasickNode:
    def __init__(self) -> None:
        self.transitions: Dict[str, AhoCorasickNode] = {}
        self.failure: Optional[AhoCorasickNode] = None
        self.outputs: List[str] = []

class SearchEngineAhoCorasickAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-11
      name: SearchEngineAhoCorasickAlgo
      version: 1.2.0
      category: search
      capability_tags:
      - search.multipattern
      - automaton.trie
      - automaton.dfa
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
          - pattern
          properties:
            start_offset:
              type: integer
              minimum: 0
            end_offset:
              type: integer
              minimum: 0
            pattern:
              type: string
      parameters:
        type: object
        required:
        - patterns
        properties:
          patterns:
            type: array
            items:
              type: string
              minLength: 1
            minItems: 1
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|Text| + |Matches|)
        space: O(TotalPatternChars)
      preconditions:
      - len(parameters.patterns) > 0
      - all(len(p) > 0 for p in parameters.patterns)
      postconditions:
      - all(0 <= m.start_offset < m.end_offset <= len(input.text) for m in output)
      compatible_adapters:
      - ADAPTER-OFFSET-TO-SPAN-OBS-16
      - ADAPTER-SNIPPET-WINDOW-SRCH-14
    ---
    """
    def __init__(self, patterns: List[str]) -> None:
        self.root = AhoCorasickNode()
        self._build_trie(patterns)
        self._build_failure_links()

    def _build_trie(self, patterns: List[str]) -> None:
        for pat in patterns:
            if not pat:
                continue
            curr = self.root
            for ch in pat:
                if ch not in curr.transitions:
                    curr.transitions[ch] = AhoCorasickNode()
                curr = curr.transitions[ch]
            curr.outputs.append(pat)

    def _build_failure_links(self) -> None:
        queue = deque()
        for ch, node in self.root.transitions.items():
            node.failure = self.root
            queue.append(node)

        while queue:
            curr = queue.popleft()
            for ch, child in curr.transitions.items():
                fail = curr.failure
                while fail and ch not in fail.transitions:
                    fail = fail.failure
                child.failure = fail.transitions[ch] if fail else self.root
                child.outputs.extend(child.failure.outputs)
                queue.append(child)

    def find_matches(self, text: str) -> List[Tuple[int, int, str]]:
        matches: List[Tuple[int, int, str]] = []
        curr = self.root
        for idx, ch in enumerate(text):
            while curr and ch not in curr.transitions:
                curr = curr.failure
            if not curr:
                curr = self.root
                continue
            curr = curr.transitions[ch]
            for pat in curr.outputs:
                start_idx = idx - len(pat) + 1
                matches.append((start_idx, idx + 1, pat))
        return matches
