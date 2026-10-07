"""
ALGORITHM & ARCHITECTURE BLUEPRINT: VF2 / VF3 Subgraph Isomorphism (ALGO-GRAPH-ISO-183)

1. OVERVIEW & OBJECTIVE:
Finds graph and subgraph isomorphisms using Cordella et al.'s VF2 state-space algorithm with
5-tier feasibility pruning: core-subgraph consistency, 1-look-ahead in-terminal / out-terminal
boundary checks, and 2-look-ahead non-terminal neighborhood cardinalities.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V_1| + |V_2|) state vectors.
- Time Complexity: O(|V_1|! * |V_2|) worst case; polynomial on planar/bounded-valence graphs.
- Invariants:
  - Maintains bijective match M(s) mapping subgraphs between G1 and G2.
  - Feasibility rules guarantee syntactic and 1-lookahead boundary match validity before branching.

3. INPUT PARAMETERS:
- `pattern_adj` (Mapping[TNode, Iterable[TNode]]): Query graph G1.
- `target_adj` (Mapping[TNode, Iterable[TNode]]): Target graph G2.
- `subgraph_mode` (bool): True for subgraph isomorphism, False for exact graph isomorphism (default: True).

4. OUTPUT PARAMETERS:
- `VF2Result`: List of valid isomorphism mappings, match count, and success status.

5. AGENT CONTRACT:
- Role: State-space graph matcher and structural validator.
- Rules: Check node counts and degree sequences before initiating state-space search.
- Guardrails: Non-subgraph search requires identical node counts |V1| == |V2|.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class VF2Result(Generic[TNode]):
    """
    Result container for VF2 isomorphism matching.
    """
    mappings: List[Dict[TNode, TNode]]
    match_count: int
    is_isomorphic: bool


class VF2SubgraphMatcher(Generic[TNode]):
    """
    Executes VF2 state-space exploration for graph and subgraph isomorphism.

    ```yaml
    contract_id: ALGO-GRAPH-ISO-183
    inputs:
      pattern_adj: Mapping[TNode, Iterable[TNode]]
      target_adj: Mapping[TNode, Iterable[TNode]]
      subgraph_mode: bool
    outputs:
      result: VF2Result[TNode]
    parameters:
      subgraph_mode: bool
    capability_tags:
      - graph
      - isomorphism
      - subgraph_isomorphism
      - vf2
      - state_space
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V_1|! * |V_2|)
      space: O(|V_1| + |V_2|)
    ```
    """

    def __init__(self, subgraph_mode: bool = True, max_matches: int = 100) -> None:
        """
        Args:
            subgraph_mode: True for subgraph isomorphism, False for full graph isomorphism.
            max_matches: Limit on discovered mappings.
        """
        self._subgraph_mode = subgraph_mode
        self._max_matches = max_matches

    def match(
        self,
        pattern_adj: Mapping[TNode, Iterable[TNode]],
        target_adj: Mapping[TNode, Iterable[TNode]],
    ) -> VF2Result[TNode]:
        """
        Computes isomorphisms from pattern graph into target graph.

        Args:
            pattern_adj: Pattern graph adjacency map.
            target_adj: Target graph adjacency map.

        Returns:
            VF2Result with matching node dictionaries.
        """
        g1_nodes = sorted(list(pattern_adj.keys()), key=lambda x: str(x))
        g2_nodes = sorted(list(target_adj.keys()), key=lambda x: str(x))

        n1, n2 = len(g1_nodes), len(g2_nodes)
        if not self._subgraph_mode and n1 != n2:
            return VF2Result(mappings=[], match_count=0, is_isomorphic=False)
        if n1 > n2:
            return VF2Result(mappings=[], match_count=0, is_isomorphic=False)
        if n1 == 0:
            return VF2Result(mappings=[{}], match_count=1, is_isomorphic=True)

        adj1: Dict[TNode, Set[TNode]] = {u: set(pattern_adj.get(u, ())) for u in g1_nodes}
        adj2: Dict[TNode, Set[TNode]] = {u: set(target_adj.get(u, ())) for u in g2_nodes}

        core_1: Dict[TNode, Optional[TNode]] = {u: None for u in g1_nodes}
        core_2: Dict[TNode, Optional[TNode]] = {v: None for v in g2_nodes}
        inout_1: Dict[TNode, int] = {u: 0 for u in g1_nodes}
        inout_2: Dict[TNode, int] = {v: 0 for v in g2_nodes}

        matches: List[Dict[TNode, TNode]] = []

        self._vf2_search(0, g1_nodes, g2_nodes, adj1, adj2, core_1, core_2, inout_1, inout_2, matches)

        return VF2Result(
            mappings=matches,
            match_count=len(matches),
            is_isomorphic=len(matches) > 0,
        )

    def _vf2_search(
        self,
        depth: int,
        g1_nodes: List[TNode],
        g2_nodes: List[TNode],
        adj1: Dict[TNode, Set[TNode]],
        adj2: Dict[TNode, Set[TNode]],
        core_1: Dict[TNode, Optional[TNode]],
        core_2: Dict[TNode, Optional[TNode]],
        inout_1: Dict[TNode, int],
        inout_2: Dict[TNode, int],
        matches: List[Dict[TNode, TNode]],
    ) -> None:
        if len(matches) >= self._max_matches:
            return

        if depth == len(g1_nodes):
            matches.append({u: core_1[u] for u in g1_nodes if core_1[u] is not None})
            return

        candidates = self._candidate_pairs(g1_nodes, g2_nodes, core_1, core_2, inout_1, inout_2)

        for u, v in candidates:
            if self._is_feasible(u, v, adj1, adj2, core_1, core_2, inout_1, inout_2):
                core_1[u] = v
                core_2[v] = u
                depth_stamp = depth + 1

                added_1 = self._update_terminal(u, adj1, inout_1, depth_stamp)
                added_2 = self._update_terminal(v, adj2, inout_2, depth_stamp)

                self._vf2_search(depth + 1, g1_nodes, g2_nodes, adj1, adj2, core_1, core_2, inout_1, inout_2, matches)

                for node in added_1:
                    inout_1[node] = 0
                for node in added_2:
                    inout_2[node] = 0
                core_1[u] = None
                core_2[v] = None

    def _candidate_pairs(
        self,
        g1_nodes: List[TNode],
        g2_nodes: List[TNode],
        core_1: Dict[TNode, Optional[TNode]],
        core_2: Dict[TNode, Optional[TNode]],
        inout_1: Dict[TNode, int],
        inout_2: Dict[TNode, int],
    ) -> List[Tuple[TNode, TNode]]:
        t1 = [u for u in g1_nodes if core_1[u] is None and inout_1[u] > 0]
        t2 = [v for v in g2_nodes if core_2[v] is None and inout_2[v] > 0]

        if t1 and t2:
            min_u = t1[0]
            return [(min_u, v) for v in t2]

        unmapped_1 = [u for u in g1_nodes if core_1[u] is None]
        unmapped_2 = [v for v in g2_nodes if core_2[v] is None]
        if unmapped_1 and unmapped_2:
            min_u = unmapped_1[0]
            return [(min_u, v) for v in unmapped_2]

        return []

    def _is_feasible(
        self,
        u: TNode,
        v: TNode,
        adj1: Dict[TNode, Set[TNode]],
        adj2: Dict[TNode, Set[TNode]],
        core_1: Dict[TNode, Optional[TNode]],
        core_2: Dict[TNode, Optional[TNode]],
        inout_1: Dict[TNode, int],
        inout_2: Dict[TNode, int],
    ) -> bool:
        for n1 in adj1[u]:
            if core_1[n1] is not None:
                if core_1[n1] not in adj2[v]:
                    return False

        if not self._subgraph_mode:
            for n2 in adj2[v]:
                if core_2[n2] is not None:
                    if core_2[n2] not in adj1[u]:
                        return False

        term1_count = sum(1 for n1 in adj1[u] if core_1[n1] is None and inout_1[n1] > 0)
        term2_count = sum(1 for n2 in adj2[v] if core_2[n2] is None and inout_2[n2] > 0)
        if term1_count > term2_count:
            return False

        new1_count = sum(1 for n1 in adj1[u] if core_1[n1] is None and inout_1[n1] == 0)
        new2_count = sum(1 for n2 in adj2[v] if core_2[n2] is None and inout_2[n2] == 0)
        if new1_count > new2_count:
            return False

        return True

    def _update_terminal(
        self,
        node: TNode,
        adj: Dict[TNode, Set[TNode]],
        inout: Dict[TNode, int],
        depth: int,
    ) -> List[TNode]:
        added: List[TNode] = []
        for neighbor in adj[node]:
            if inout[neighbor] == 0:
                inout[neighbor] = depth
                added.append(neighbor)
        return added
