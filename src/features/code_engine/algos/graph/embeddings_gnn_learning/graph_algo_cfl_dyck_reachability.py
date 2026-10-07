"""ALGORITHM & ARCHITECTURE BLUEPRINT: CFL-REACHABILITY (DYCK CONTEXT-FREE REACHABILITY) (ALGO-GRAPH-PROG-298)

1. OVERVIEW & OBJECTIVE
Context-Free Language (CFL) reachability on edge-labeled directed graphs G = (V, E, Sigma) determines
whether there exists a path between u and v whose edge label concatenation forms a valid word in a given
formal CFL grammar L(G) (such as the balanced-parentheses Dyck language Dyck_k). Employs dynamic programming
closure (Chomsky Normal Form productions A -> B C, A -> a, A -> epsilon) to add non-terminal summary edges.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V|^2 * |NonTerminals|) derived edge relation storage.
- Time Complexity: O(|V|^3 * |Grammar|) cubic dynamic programming matrix closure.
- Invariants:
  - If (u, v) is labeled with nonterminal A, there exists a path u ~> v generating string w in L(A).
  - All valid Dyck paths preserve balanced parenthesis nesting (e.g. open_i ... close_i).

3. INPUT PARAMETERS:
- labeled_edges: Sequence[tuple[TNode, TNode, str]] directed edges with grammar terminal or non-terminal labels.
- grammar_rules: Sequence[tuple[str, Sequence[str]]] production rules in Chomsky Normal Form: A -> [B, C] or A -> [a].
- query_pairs: Optional[Sequence[tuple[TNode, TNode]]] specific (u, v) endpoint reachability queries.
- target_nonterminal: str start symbol (default 'S').

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'reachable_pairs': Set[tuple[TNode, TNode]] all vertex pairs connected by paths in L(target_nonterminal).
  - 'derived_edges': Dict[str, Set[tuple[TNode, TNode]]] all added summary edges keyed by non-terminal symbol.
  - 'total_summary_edges': int count of inferred non-terminal edges.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCflDyckReachability(Generic[TNode]):
    """CFL and Dyck-k graph reachability using dynamic programming transitive closure.

    ```yaml
    contract:
      id: ALGO-GRAPH-PROG-298
      name: GraphAlgoCflDyckReachability
      inputs:
        - name: labeled_edges
          type: Sequence[tuple[TNode, TNode, str]]
          description: Directed edges with string labels (u, v, label).
        - name: grammar_rules
          type: Sequence[tuple[str, Sequence[str]]]
          description: CNF grammar productions (lhs, [rhs1, rhs2]) or (lhs, [terminal]).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Reachable pairs under target non-terminal and all derived summary edges.
      parameters:
        target_nonterminal: str (default 'S')
        query_pairs: Optional[Sequence[tuple[TNode, TNode]]] (default None)
      capability_tags:
        - STATIC_ANALYSIS
        - CFL_REACHABILITY
        - DYCK_LANGUAGE
        - CONTEXT_FREE_GRAMMAR
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V|^3 * |Grammar|)
        space: O(|V|^2 * |NonTerminals|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        labeled_edges: Sequence[Tuple[TNode, TNode, str]],
        grammar_rules: Sequence[Tuple[str, Sequence[str]]],
        target_nonterminal: str = "S",
        query_pairs: Optional[Sequence[Tuple[TNode, TNode]]] = None,
    ) -> Dict[str, Any]:
        """Calculates CFL transitive closure over the labeled graph."""
        edges_by_sym: Dict[str, Set[Tuple[TNode, TNode]]] = collections.defaultdict(set)
        all_nodes: Set[TNode] = set()

        for u, v, sym in labeled_edges:
            edges_by_sym[sym].add((u, v))
            all_nodes.add(u)
            all_nodes.add(v)

        worklist: collections.deque[Tuple[str, TNode, TNode]] = collections.deque()

        for lhs, rhs in grammar_rules:
            if len(rhs) == 1:
                term = rhs[0]
                for u, v in edges_by_sym.get(term, []):
                    if (u, v) not in edges_by_sym[lhs]:
                        edges_by_sym[lhs].add((u, v))
                        worklist.append((lhs, u, v))
            elif len(rhs) == 0:
                for u in all_nodes:
                    if (u, u) not in edges_by_sym[lhs]:
                        edges_by_sym[lhs].add((u, u))
                        worklist.append((lhs, u, u))

        for u, v, sym in labeled_edges:
            worklist.append((sym, u, v))

        outgoing: Dict[str, Dict[TNode, Set[TNode]]] = collections.defaultdict(lambda: collections.defaultdict(set))
        incoming: Dict[str, Dict[TNode, Set[TNode]]] = collections.defaultdict(lambda: collections.defaultdict(set))

        for sym, pair_set in edges_by_sym.items():
            for u, v in pair_set:
                outgoing[sym][u].add(v)
                incoming[sym][v].add(u)

        binary_rules = [
            (lhs, rhs[0], rhs[1]) for lhs, rhs in grammar_rules if len(rhs) == 2
        ]

        while worklist:
            sym, u, v = worklist.popleft()

            for lhs, b, c in binary_rules:
                if sym == b:
                    for w in outgoing[c].get(v, []):
                        if (u, w) not in edges_by_sym[lhs]:
                            edges_by_sym[lhs].add((u, w))
                            outgoing[lhs][u].add(w)
                            incoming[lhs][w].add(u)
                            worklist.append((lhs, u, w))

                if sym == c:
                    for w in incoming[b].get(u, []):
                        if (w, v) not in edges_by_sym[lhs]:
                            edges_by_sym[lhs].add((w, v))
                            outgoing[lhs][w].add(v)
                            incoming[lhs][v].add(w)
                            worklist.append((lhs, w, v))

        target_pairs = edges_by_sym.get(target_nonterminal, set())

        total_edges = sum(len(p_set) for p_set in edges_by_sym.values())

        return {
            "reachable_pairs": target_pairs,
            "derived_edges": {sym: edges_by_sym[sym] for sym in edges_by_sym},
            "total_summary_edges": total_edges,
        }
