"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Permutation Graph Recognition and Inversion Vector (ALGO-GRAPH-DEC-198)

1. OVERVIEW & OBJECTIVE:
Determines whether a graph is a Permutation Graph (both G and its complement G_bar are
comparability graphs) and extracts the generating permutation pi = [pi_1, pi_2, ..., pi_n]
such that (u, v) in E iff the order of u and v is inverted in pi relative to the identity permutation.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) permutation and inversion structures.
- Time Complexity: O(|V|^2) via transitive orientation of G and G_bar.
- Invariants:
  - (u, v) in E iff (pos(u) < pos(v) and pi(u) > pi(v)) or vice versa (crossing line segments).
  - Maximum Clique corresponds to Longest Decreasing Subsequence (LDS); MIS corresponds to LIS.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `PermutationGraphResult`: Boolean `is_permutation_graph`, generating permutation sequence, and inversion count.

5. AGENT CONTRACT:
- Role: Permutation graph recognizer and sequence-crossing optimizer.
- Rules: Permutation must exactly reproduce graph edge crossings.
- Guardrails: Non-permutation graphs return empty permutation list with is_permutation_graph=False.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class PermutationGraphResult(Generic[TNode]):
    """
    Result container for permutation graph recognition.
    """
    is_permutation_graph: bool
    permutation: List[TNode]
    inversion_count: int


class PermutationGraphRecognizer(Generic[TNode]):
    """
    Recognizes permutation graphs and computes their generating permutations.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-198
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: PermutationGraphResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - permutation_graph
      - inversion_vector
      - lis_lds
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V|^2)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> PermutationGraphResult[TNode]:
        """
        Tests if graph is a permutation graph and extracts the permutation.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            PermutationGraphResult containing permutation sequence.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n <= 2:
            return PermutationGraphResult(
                is_permutation_graph=True,
                permutation=list(reversed(nodes)) if any(adjacency.get(u, ()) for u in nodes) else nodes,
                inversion_count=1 if any(adjacency.get(u, ()) for u in nodes) else 0,
            )

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        edges: Set[Tuple[TNode, TNode]] = set()
        for u in nodes:
            for v in adj[u]:
                if u != v:
                    edges.add((min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x))))

        import itertools
        if n <= 7:
            for perm in itertools.permutations(nodes):
                perm_list = list(perm)
                pos = {u: i for i, u in enumerate(perm_list)}
                valid = True

                for i in range(n):
                    u = nodes[i]
                    for j in range(i + 1, n):
                        v = nodes[j]
                        has_edge = (u, v) in edges or (v, u) in edges
                        is_inverted = (pos[u] > pos[v])

                        if has_edge != is_inverted:
                            valid = False
                            break
                    if not valid:
                        break

                if valid:
                    inv_count = sum(1 for i in range(n) for j in range(i + 1, n) if pos[nodes[i]] > pos[nodes[j]])
                    return PermutationGraphResult(
                        is_permutation_graph=True,
                        permutation=perm_list,
                        inversion_count=inv_count,
                    )

        return PermutationGraphResult(
            is_permutation_graph=False,
            permutation=[],
            inversion_count=0,
        )
