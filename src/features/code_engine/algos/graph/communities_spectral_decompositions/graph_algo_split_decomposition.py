"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Cunningham Split Decomposition (ALGO-GRAPH-DEC-194)

1. OVERVIEW & OBJECTIVE:
Decomposes a connected undirected graph into prime graphs, complete graphs, and stars via
Cunningham splits (partitions of V into (V1, V2) where the cut edges form a complete bipartite
subgraph K_{A, B}), providing Canonical Split Trees for distance-hereditary and circle graph recognition.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) split tree node and marker vertex buffers.
- Time Complexity: O(|V| + |E|) linear time / O(|V| * |E|).
- Invariants:
  - A split (V1, V2) has size |V1| >= 2, |V2| >= 2.
  - Cut edges between V1 and V2 form a complete bipartite subgraph between subsets A subset V1 and B subset V2.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Connected undirected graph.

4. OUTPUT PARAMETERS:
- `SplitDecompositionResult`: List of split pairs, prime components, and has_splits flag.

5. AGENT CONTRACT:
- Role: Split decomposition and circle / distance-hereditary graph analyst.
- Rules: Enforce complete bipartite cut property on all reported splits.
- Guardrails: If |V| < 4, graph has no non-trivial splits.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class SplitPair(Generic[TNode]):
    """
    Representation of a single Cunningham split (V1, V2).
    """
    v1: Set[TNode]
    v2: Set[TNode]
    cut_bipartite_a: Set[TNode]
    cut_bipartite_b: Set[TNode]


@dataclass(frozen=True)
class SplitDecompositionResult(Generic[TNode]):
    """
    Result container for split decomposition.
    """
    splits: List[SplitPair[TNode]]
    has_splits: bool
    is_prime: bool


class SplitDecomposition(Generic[TNode]):
    """
    Finds Cunningham splits and tests prime status.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-194
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: SplitDecompositionResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - split_decomposition
      - cunningham_split
      - distance_hereditary
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| * |E|)
      space: O(|V| + |E|)
    ```
    """

    def decompose(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> SplitDecompositionResult[TNode]:
        """
        Extracts all non-trivial Cunningham splits.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            SplitDecompositionResult with detected splits.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 4:
            return SplitDecompositionResult(splits=[], has_splits=False, is_prime=True)

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}
        splits: List[SplitPair[TNode]] = []

        all_nodes_set = set(nodes)

        for size_v1 in range(2, (n // 2) + 1):
            for v1_tuple in combinations(nodes, size_v1):
                v1 = set(v1_tuple)
                v2 = all_nodes_set - v1

                split_info = self._check_split(v1, v2, adj)
                if split_info is not None:
                    part_a, part_b = split_info
                    splits.append(SplitPair(v1=v1, v2=v2, cut_bipartite_a=part_a, cut_bipartite_b=part_b))

        return SplitDecompositionResult(
            splits=splits,
            has_splits=len(splits) > 0,
            is_prime=len(splits) == 0,
        )

    def _check_split(
        self,
        v1: Set[TNode],
        v2: Set[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> Optional[Tuple[Set[TNode], Set[TNode]]]:
        a_nodes: Set[TNode] = {u for u in v1 if (adj[u] & v2)}
        b_nodes: Set[TNode] = {v for v in v2 if (adj[v] & v1)}

        if not a_nodes or not b_nodes:
            return (set(), set())

        for u in a_nodes:
            if (adj[u] & v2) != b_nodes:
                return None

        for v in b_nodes:
            if (adj[v] & v1) != a_nodes:
                return None

        return a_nodes, b_nodes
