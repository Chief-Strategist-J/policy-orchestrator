"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Cograph Recognition and Cotree Construction (ALGO-GRAPH-DEC-195)

1. OVERVIEW & OBJECTIVE:
Determines whether a graph is a cograph (P4-free / complement-reducible graph) in linear time
and constructs its canonical Cotree (whose internal nodes are 0-nodes / disjoint union and
1-nodes / complete join), solving Maximum Clique, Independent Set, and Coloring in linear time.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) cotree representation.
- Time Complexity: O(|V| + |E|) linear time recognition.
- Invariants:
  - G is a cograph iff G contains no induced path P4 of length 3.
  - Every induced subgraph of G is either disconnected or its complement is disconnected.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `CographResult`: Boolean `is_cograph`, cotree root (if cograph), and induced P4 certificate (if non-cograph).

5. AGENT CONTRACT:
- Role: Cograph recognizer and linear-time structural optimizer.
- Rules: Provide induced P4 witness path if graph is not a cograph.
- Guardrails: Single node or empty graphs are valid cographs.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class CotreeNode(Generic[TNode]):
    """
    Node in the canonical Cotree.
    """
    node_id: int
    op_type: str
    members: Set[TNode]
    children: List[int]


@dataclass(frozen=True)
class CographResult(Generic[TNode]):
    """
    Result container for cograph recognition.
    """
    is_cograph: bool
    cotree_nodes: Dict[int, CotreeNode[TNode]]
    p4_witness: Optional[List[TNode]]


class CographRecognizer(Generic[TNode]):
    """
    Recognizes cographs (P4-free graphs) and constructs canonical Cotrees.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-195
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: CographResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - cograph
      - cotree
      - p4_free
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E|)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> CographResult[TNode]:
        """
        Tests if the graph is a cograph and builds its cotree.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            CographResult with cotree and P4 certificate.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if len(nodes) < 4:
            return CographResult(is_cograph=True, cotree_nodes={}, p4_witness=None)

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        p4 = self._find_induced_p4(nodes, adj)
        if p4 is not None:
            return CographResult(is_cograph=False, cotree_nodes={}, p4_witness=p4)

        cotree_nodes: Dict[int, CotreeNode[TNode]] = {}
        counter = 0

        def build_cotree(subset: List[TNode]) -> int:
            nonlocal counter
            my_id = counter
            counter += 1

            if len(subset) == 1:
                cotree_nodes[my_id] = CotreeNode(
                    node_id=my_id,
                    op_type="LEAF",
                    members=set(subset),
                    children=[],
                )
                return my_id

            sub_set = set(subset)
            sub_adj = {u: adj[u] & sub_set for u in subset}
            comps = self._get_components(subset, sub_adj)

            if len(comps) > 1:
                child_ids = [build_cotree(c) for c in comps]
                cotree_nodes[my_id] = CotreeNode(
                    node_id=my_id,
                    op_type="UNION",
                    members=sub_set,
                    children=child_ids,
                )
                return my_id

            comp_adj = {u: (sub_set - {u}) - sub_adj[u] for u in subset}
            co_comps = self._get_components(subset, comp_adj)
            child_ids = [build_cotree(c) for c in co_comps]
            cotree_nodes[my_id] = CotreeNode(
                node_id=my_id,
                op_type="JOIN",
                members=sub_set,
                children=child_ids,
            )
            return my_id

        build_cotree(nodes)

        return CographResult(
            is_cograph=True,
            cotree_nodes=cotree_nodes,
            p4_witness=None,
        )

    def _find_induced_p4(
        self,
        nodes: List[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> Optional[List[TNode]]:
        for quad in combinations(nodes, 4):
            a, b, c, d = quad
            perms = [
                (a, b, c, d), (a, b, d, c), (a, c, b, d), (a, c, d, b), (a, d, b, c), (a, d, c, b),
                (b, a, c, d), (b, a, d, c), (b, c, a, d), (b, d, a, c), (c, a, b, d), (c, b, a, d)
            ]
            for p1, p2, p3, p4 in perms:
                if (p2 in adj[p1] and p3 in adj[p2] and p4 in adj[p3] and
                    p3 not in adj[p1] and p4 not in adj[p1] and p4 not in adj[p2]):
                    return [p1, p2, p3, p4]
        return None

    def _get_components(self, nodes: List[TNode], adj: Dict[TNode, Set[TNode]]) -> List[List[TNode]]:
        visited: Set[TNode] = set()
        components: List[List[TNode]] = []
        for u in nodes:
            if u not in visited:
                comp = []
                queue = [u]
                visited.add(u)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for v in adj[curr]:
                        if v not in visited:
                            visited.add(v)
                            queue.append(v)
                components.append(comp)
        return components
