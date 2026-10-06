"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: THOMPSON NFA CONSTRUCTION (ALGO 34)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a Non-deterministic Finite Automaton (NFA) from regular expressions
   using Ken Thompson's structural construction. Guarantees that the resulting
   NFA has at most O(|Pattern|) states and O(|Pattern|) transitions with at most
   2 out-edges per state, ensuring immunity to catastrophic backtracking.

2. COMPLEXITY & INVARIANTS:
   - Construction Time: O(|Pattern|) linear time.
   - Space Complexity: O(|Pattern|) states and transitions.
   - Guaranteed Invariant: No state has more than 2 transitions.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Builds small NFA fragments with one entry state and one exit state.
   - Literal / Class: single transition (start -> end).
   - Concatenation: merges exit state of fragment 1 with entry of fragment 2.
   - Alternation: split start state with epsilon transitions to both fragments,
     joining at a single common end state.
   - Kleene Star (*): loopback epsilon transitions from exit to entry and start to end.
================================================================================
"""

from typing import List, Dict, Any, Optional, Set, Tuple


class NfaState:
    _id_counter = 0

    def __init__(self, is_match: bool = False) -> None:
        self.state_id = NfaState._id_counter
        NfaState._id_counter += 1
        self.is_match = is_match
        self.transitions: List[Tuple[Optional[str], NfaState]] = []

    def add_transition(self, char: Optional[str], target: "NfaState") -> None:
        self.transitions.append((char, target))


class NfaFragment:
    def __init__(self, start: NfaState, end: NfaState) -> None:
        self.start = start
        self.end = end


class SearchEngineThompsonNfaAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-34
      name: SearchEngineThompsonNfaAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - regex.compiler
      - automaton.nfa
      - thompson.construction
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
        - state_count
        - start_state_id
        - match_state_id
        - states
        properties:
          state_count:
            type: integer
          start_state_id:
            type: integer
          match_state_id:
            type: integer
          states:
            type: array
            items:
              type: object
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

    @classmethod
    def compile_pattern(cls, pattern: str) -> Tuple[NfaState, NfaState, List[NfaState]]:
        NfaState._id_counter = 0
        all_states: List[NfaState] = []

        def create_state(is_match: bool = False) -> NfaState:
            st = NfaState(is_match=is_match)
            all_states.append(st)
            return st

        def build_fragment(p: str) -> NfaFragment:
            if not p:
                s = create_state()
                e = create_state()
                s.add_transition(None, e)
                return NfaFragment(s, e)

            fragments: List[NfaFragment] = []
            idx = 0
            while idx < len(p):
                c = p[idx]
                if c == "\\":
                    idx += 1
                    esc = p[idx] if idx < len(p) else ""
                    s = create_state()
                    e = create_state()
                    s.add_transition(esc, e)
                    fragments.append(NfaFragment(s, e))
                elif c == "(":
                    depth = 1
                    sub_start = idx + 1
                    idx += 1
                    while idx < len(p) and depth > 0:
                        if p[idx] == "(":
                            depth += 1
                        elif p[idx] == ")":
                            depth -= 1
                        idx += 1
                    sub_frag = build_fragment(p[sub_start:idx - 1])
                    fragments.append(sub_frag)
                    continue
                elif c == "|":
                    left_frag = cls._concat_fragments(fragments, create_state)
                    right_frag = build_fragment(p[idx + 1:])
                    s = create_state()
                    e = create_state()
                    s.add_transition(None, left_frag.start)
                    s.add_transition(None, right_frag.start)
                    left_frag.end.add_transition(None, e)
                    right_frag.end.add_transition(None, e)
                    return NfaFragment(s, e)
                elif c == "*":
                    if fragments:
                        target = fragments.pop()
                        s = create_state()
                        e = create_state()
                        s.add_transition(None, target.start)
                        s.add_transition(None, e)
                        target.end.add_transition(None, target.start)
                        target.end.add_transition(None, e)
                        fragments.append(NfaFragment(s, e))
                elif c == "+":
                    if fragments:
                        target = fragments.pop()
                        s = create_state()
                        e = create_state()
                        s.add_transition(None, target.start)
                        target.end.add_transition(None, target.start)
                        target.end.add_transition(None, e)
                        fragments.append(NfaFragment(s, e))
                elif c == "?":
                    if fragments:
                        target = fragments.pop()
                        s = create_state()
                        e = create_state()
                        s.add_transition(None, target.start)
                        s.add_transition(None, e)
                        target.end.add_transition(None, e)
                        fragments.append(NfaFragment(s, e))
                else:
                    s = create_state()
                    e = create_state()
                    s.add_transition(c, e)
                    fragments.append(NfaFragment(s, e))
                idx += 1

            return cls._concat_fragments(fragments, create_state)

        full_frag = build_fragment(pattern)
        full_frag.end.is_match = True
        return full_frag.start, full_frag.end, all_states

    @classmethod
    def _concat_fragments(cls, fragments: List[NfaFragment], create_state_fn: Any) -> NfaFragment:
        if not fragments:
            s = create_state_fn()
            e = create_state_fn()
            s.add_transition(None, e)
            return NfaFragment(s, e)
        if len(fragments) == 1:
            return fragments[0]

        for i in range(len(fragments) - 1):
            fragments[i].end.add_transition(None, fragments[i + 1].start)

        return NfaFragment(fragments[0].start, fragments[-1].end)

    @classmethod
    def execute(cls, pattern: str) -> Dict[str, Any]:
        start, end, all_states = cls.compile_pattern(pattern)
        serialized_states = []
        for st in all_states:
            trans = [{"char": c, "target_id": t.state_id} for c, t in st.transitions]
            serialized_states.append({
                "state_id": st.state_id,
                "is_match": st.is_match,
                "transitions": trans,
            })

        return {
            "state_count": len(all_states),
            "start_state_id": start.state_id,
            "match_state_id": end.state_id,
            "states": serialized_states,
        }
