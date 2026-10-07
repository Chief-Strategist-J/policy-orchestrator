"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Ullmann Subgraph Isomorphism (ALGO-GRAPH-ISO-182)

1. OVERVIEW & OBJECTIVE:
Finds all exact subgraph isomorphism mappings (injective homomorphisms) from a pattern
graph P = (V_p, E_p) into a target graph T = (V_t, E_t) using Ullmann's candidate compatibility
matrix M and recursive refinement filtering.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V_p| * |V_t|) candidate matrix storage.
- Time Complexity: O(|V_p|! * |V_t|^|V_p|) worst case; pruned significantly by degree consistency.
- Invariants:
  - Every mapping f: V_p -> V_t is injective (distinct pattern nodes map to distinct target nodes).
  - For all (u, v) in E_p, (f(u), f(v)) in E_t (subgraph homomorphism).

3. INPUT PARAMETERS:
- `pattern_adj` (Mapping[TNode, Iterable[TNode]]): Small query pattern graph P.
- `target_adj` (Mapping[TNode, Iterable[TNode]]): Larger host target graph T.
- `max_matches` (int): Maximum isomorphism mappings to find (default: 100).
- `induced` (bool): Whether non-edges in pattern must also be non-edges in target (default: False).

4. OUTPUT PARAMETERS:
- `SubgraphIsomorphismResult`: List of match dictionaries mapping pattern nodes to target nodes.

5. AGENT CONTRACT:
- Role: Pattern matching and structural query engine.
- Rules: Enforce strict candidate filtering using neighborhood degrees.
- Guardrails: If |V_p| > |V_t|, returns 0 matches immediately.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class SubgraphIsomorphismResult(Generic[TNode]):
    """
    Result container for subgraph isomorphism matching.
    """
    matches: List[Dict[TNode, TNode]]
    match_count: int
    is_subgraph: bool


class UllmannSubgraphMatcher(Generic[TNode]):
    """
    Implements Ullmann's exact subgraph isomorphism search.

    ```yaml
    contract_id: ALGO-GRAPH-ISO-182
    inputs:
      pattern_adj: Mapping[TNode, Iterable[TNode]]
      target_adj: Mapping[TNode, Iterable[TNode]]
      max_matches: int
      induced: bool
    outputs:
      result: SubgraphIsomorphismResult[TNode]
    parameters:
      max_matches: int
      induced: bool
    capability_tags:
      - graph
      - isomorphism
      - subgraph_isomorphism
      - ullmann
      - pattern_mining
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V_p|! * |V_t|^|V_p|)
      space: O(|V_p| * |V_t|)
    ```
    """

    def __init__(self, max_matches: int = 100, induced: bool = False) -> None:
        """
        Args:
            max_matches: Search limit for discovered isomorphisms.
            induced: If True, search for induced subgraphs.
        """
        self._max_matches = max_matches
        self._induced = induced

    def find_matches(
        self,
        pattern_adj: Mapping[TNode, Iterable[TNode]],
        target_adj: Mapping[TNode, Iterable[TNode]],
    ) -> SubgraphIsomorphismResult[TNode]:
        """
        Enumerates isomorphic embeddings of pattern into target graph.

        Args:
            pattern_adj: Pattern graph adjacency map.
            target_adj: Target graph adjacency map.

        Returns:
            SubgraphIsomorphismResult containing list of valid node mappings.
        """
        p_nodes = sorted(list(pattern_adj.keys()), key=lambda x: str(x))
        t_nodes = sorted(list(target_adj.keys()), key=lambda x: str(x))

        if not p_nodes:
            return SubgraphIsomorphismResult(matches=[{}], match_count=1, is_subgraph=True)
        if len(p_nodes) > len(t_nodes):
            return SubgraphIsomorphismResult(matches=[], match_count=0, is_subgraph=False)

        p_adj: Dict[TNode, Set[TNode]] = {u: set(pattern_adj.get(u, ())) for u in p_nodes}
        t_adj: Dict[TNode, Set[TNode]] = {u: set(target_adj.get(u, ())) for u in t_nodes}

        m_matrix: Dict[TNode, Set[TNode]] = {}
        for p_u in p_nodes:
            candidates: Set[TNode] = set()
            deg_p = len(p_adj[p_u])
            for t_v in t_nodes:
                if len(t_adj[t_v]) >= deg_p:
                    candidates.add(t_v)
            m_matrix[p_u] = candidates

        self._refine_matrix(p_nodes, p_adj, t_adj, m_matrix)

        matches: List[Dict[TNode, TNode]] = []
        mapping: Dict[TNode, TNode] = {}
        used_target: Set[TNode] = set()

        self._backtrack(0, p_nodes, p_adj, t_adj, m_matrix, mapping, used_target, matches)

        return SubgraphIsomorphismResult(
            matches=matches,
            match_count=len(matches),
            is_subgraph=len(matches) > 0,
        )

    def _refine_matrix(
        self,
        p_nodes: List[TNode],
        p_adj: Dict[TNode, Set[TNode]],
        t_adj: Dict[TNode, Set[TNode]],
        m_matrix: Dict[TNode, Set[TNode]],
    ) -> None:
        changed = True
        while changed:
            changed = False
            for p_u in p_nodes:
                to_remove = set()
                for t_v in m_matrix[p_u]:
                    for p_x in p_adj[p_u]:
                        if not any(t_y in m_matrix[p_x] for t_y in t_adj[t_v]):
                            to_remove.add(t_v)
                            break
                if to_remove:
                    m_matrix[p_u] -= to_remove
                    changed = True

    def _backtrack(
        self,
        depth: int,
        p_nodes: List[TNode],
        p_adj: Dict[TNode, Set[TNode]],
        t_adj: Dict[TNode, Set[TNode]],
        m_matrix: Dict[TNode, Set[TNode]],
        mapping: Dict[TNode, TNode],
        used_target: Set[TNode],
        matches: List[Dict[TNode, TNode]],
    ) -> None:
        if len(matches) >= self._max_matches:
            return

        if depth == len(p_nodes):
            matches.append(dict(mapping))
            return

        p_u = p_nodes[depth]
        for t_v in m_matrix[p_u]:
            if t_v in used_target:
                continue

            valid = True
            for i in range(depth):
                p_prev = p_nodes[i]
                t_prev = mapping[p_prev]

                if p_prev in p_adj[p_u]:
                    if t_prev not in t_adj[t_v]:
                        valid = False
                        break
                elif self._induced:
                    if t_prev in t_adj[t_v]:
                        valid = False
                        break

            if valid:
                mapping[p_u] = t_v
                used_target.add(t_v)
                self._backtrack(depth + 1, p_nodes, p_adj, t_adj, m_matrix, mapping, used_target, matches)
                used_target.remove(t_v)
                del mapping[p_u]
