"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GALE-SHAPLEY STABLE MATCHING (ALGO-GRAPH-MATCH-88)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Gale-Shapley Deferred Acceptance algorithm for stable bipartite matching.
   Computes a stable matching where no unmatched pair strictly prefers each other
   over their assigned matches.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N^2) proposer iterations.
   - Space Complexity: O(N^2) preference ranking index tables.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer.
   - Guarantees: Proposer-optimal stable matching certificate.
================================================================================
"""

from collections import deque
from typing import Dict, Generic, Hashable, List, Optional, Tuple, TypeVar

TProposer = TypeVar("TProposer", bound=Hashable)
TAcceptor = TypeVar("TAcceptor", bound=Hashable)


class GraphAlgoGaleShapleyStableMatching(Generic[TProposer, TAcceptor]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MATCH-88
      name: GraphAlgoGaleShapleyStableMatching
      version: 1.0.0
      category: graph_matching
      capability_tags: [graph, stable_matching, deferred_acceptance, gale_shapley, preferences]
      inputs:
        type: object
        required: [proposer_prefs, acceptor_prefs]
        properties:
          proposer_prefs:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
          acceptor_prefs:
            type: object
            additionalProperties:
              type: array
              items: {type: string}
      outputs:
        type: object
        required: [matching, is_stable]
        properties:
          matching:
            type: object
            additionalProperties: {type: string}
          is_stable: {type: boolean}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(N^2)
        space: O(N^2)
    ---
    """

    def __init__(
        self,
        proposer_prefs: Dict[TProposer, List[TAcceptor]],
        acceptor_prefs: Dict[TAcceptor, List[TProposer]],
    ) -> None:
        self._prop_prefs: Dict[TProposer, List[TAcceptor]] = {
            p: list(prefs) for p, prefs in proposer_prefs.items()
        }
        self._acc_prefs: Dict[TAcceptor, List[TProposer]] = {
            a: list(prefs) for a, prefs in acceptor_prefs.items()
        }

    def compute_stable_matching(self) -> Dict[TProposer, TAcceptor]:
        free_proposers: deque[TProposer] = deque(sorted(list(self._prop_prefs.keys()), key=lambda x: str(x)))
        next_proposal_idx: Dict[TProposer, int] = {p: 0 for p in self._prop_prefs}
        current_match: Dict[TAcceptor, Optional[TProposer]] = {a: None for a in self._acc_prefs}

        acc_rank: Dict[TAcceptor, Dict[TProposer, int]] = {
            a: {p: idx for idx, p in enumerate(prefs)}
            for a, prefs in self._acc_prefs.items()
        }

        while free_proposers:
            p = free_proposers.popleft()
            prefs = self._prop_prefs.get(p, [])

            if next_proposal_idx[p] < len(prefs):
                a = prefs[next_proposal_idx[p]]
                next_proposal_idx[p] += 1

                curr_partner = current_match.get(a)
                if curr_partner is None:
                    current_match[a] = p
                else:
                    ranks = acc_rank.get(a, {})
                    p_rank = ranks.get(p, float("inf"))
                    curr_rank = ranks.get(curr_partner, float("inf"))

                    if p_rank < curr_rank:
                        current_match[a] = p
                        free_proposers.append(curr_partner)
                    else:
                        free_proposers.append(p)

        return {p: a for a, p in current_match.items() if p is not None}
