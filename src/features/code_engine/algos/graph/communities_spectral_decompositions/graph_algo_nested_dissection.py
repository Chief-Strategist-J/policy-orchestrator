"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Nested Dissection Sparse Ordering (ALGO-GRAPH-DEC-190)

1. OVERVIEW & OBJECTIVE:
Recursively partitions a symmetric sparse matrix sparsity graph by finding balanced vertex
separators S, ordering the disconnected components A and B recursively, and numbering separator
vertices S last, minimizing matrix fill-in during Cholesky and LU factorizations.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) recursion ordering buffers.
- Time Complexity: O(|V|^(3/2)) for planar graphs; O(|V| * |E|) general graphs.
- Invariants:
  - For each separator S splitting A and B, all vertices in A and B receive permutation indices strictly smaller than indices of vertices in S.
  - Zero fill-in occurs between independent blocks A and B in sparse factorization.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Sparse matrix adjacency structure.

4. OUTPUT PARAMETERS:
- `NestedDissectionResult`: Permutation ordering list and inverse permutation mapping.

5. AGENT CONTRACT:
- Role: Sparse matrix elimination and fill-in minimization optimizer.
- Rules: Enforce strict bijection in permutation mappings.
- Guardrails: If |V| < 3, returns trivial natural ordering.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class NestedDissectionResult(Generic[TNode]):
    """
    Result container for nested dissection ordering.
    """
    ordering: List[TNode]
    permutation_indices: Dict[TNode, int]
    num_separators_found: int


class NestedDissectionOrderer(Generic[TNode]):
    """
    Computes fill-reducing permutation orderings via recursive separator dissection.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-190
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: NestedDissectionResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - nested_dissection
      - sparse_matrix
      - cholesky_ordering
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| * |E|)
      space: O(|V| + |E|)
    ```
    """

    def order(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> NestedDissectionResult[TNode]:
        """
        Computes the nested dissection elimination ordering.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            NestedDissectionResult containing vertex ordering.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if len(nodes) < 3:
            return NestedDissectionResult(
                ordering=nodes,
                permutation_indices={u: idx for idx, u in enumerate(nodes)},
                num_separators_found=0,
            )

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        ordered_list: List[TNode] = []
        separator_count = 0

        def dissect(sub_nodes: List[TNode]) -> None:
            nonlocal separator_count
            if len(sub_nodes) <= 3:
                ordered_list.extend(sub_nodes)
                return

            sub_set = set(sub_nodes)
            sub_adj = {u: adj[u] & sub_set for u in sub_nodes}

            sep, part_a, part_b = self._find_vertex_separator(sub_nodes, sub_adj)
            if not sep or not part_a or not part_b:
                ordered_list.extend(sub_nodes)
                return

            separator_count += 1
            dissect(list(part_a))
            dissect(list(part_b))
            ordered_list.extend(list(sep))

        dissect(nodes)

        perm_idx = {u: i for i, u in enumerate(ordered_list)}
        return NestedDissectionResult(
            ordering=ordered_list,
            permutation_indices=perm_idx,
            num_separators_found=separator_count,
        )

    def _find_vertex_separator(
        self,
        nodes: List[TNode],
        sub_adj: Dict[TNode, Set[TNode]],
    ) -> Tuple[Set[TNode], Set[TNode], Set[TNode]]:
        n = len(nodes)
        start = min(nodes, key=lambda u: (len(sub_adj[u]), str(u)))

        level: Dict[TNode, int] = {start: 0}
        queue = [start]
        while queue:
            curr = queue.pop(0)
            for v in sub_adj[curr]:
                if v not in level:
                    level[v] = level[curr] + 1
                    queue.append(v)

        max_lvl = max(level.values()) if level else 0
        if max_lvl < 2:
            return set(), set(), set()

        mid_lvl = max_lvl // 2
        separator = {u for u in nodes if level.get(u, 0) == mid_lvl}
        part_a = {u for u in nodes if level.get(u, 0) < mid_lvl}
        part_b = {u for u in nodes if level.get(u, 0) > mid_lvl}

        return separator, part_a, part_b
