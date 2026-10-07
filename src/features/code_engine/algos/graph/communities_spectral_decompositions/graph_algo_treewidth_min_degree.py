"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Treewidth and Tree Decompositions (ALGO-GRAPH-DEC-187)

1. OVERVIEW & OBJECTIVE:
Constructs a tree decomposition of a graph using elimination ordering heuristics (Min-Degree
and Min-Fill), computing tree bags, chordal fill-in edges, and an upper bound on treewidth
tw(G) = max_{B in Bags} |B| - 1 to evaluate problem tractability for dynamic programming.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E| + |Fill|) tree bags and triangulated graph.
- Time Complexity: O(|V|^3) for Min-Fill heuristic; O(|V| * (|V| + |E|)) for Min-Degree.
- Invariants:
  - Running Intersection Property: For each node v in V, the set of bags containing v induces a connected subtree.
  - Coverage: For every edge (u, v) in E, there exists at least one bag containing both u and v.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.
- `heuristic` (str): 'min_fill' or 'min_degree' (default: 'min_fill').

4. OUTPUT PARAMETERS:
- `TreeDecompositionResult`: Upper bound on treewidth, list of bags, elimination ordering, and tree edges.

5. AGENT CONTRACT:
- Role: Graph structural decomposition and tractability analyzer.
- Rules: Guarantee running intersection property on all generated bag trees.
- Guardrails: If |V| <= 1, treewidth is 0.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class TreeDecompositionResult(Generic[TNode]):
    """
    Result container for tree decomposition.
    """
    treewidth_upper_bound: int
    bags: List[Set[TNode]]
    elimination_order: List[TNode]
    fill_edges: Set[Tuple[TNode, TNode]]


class TreeDecompositionSolver(Generic[TNode]):
    """
    Computes tree decompositions and treewidth upper bounds via vertex elimination.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-187
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      heuristic: str
    outputs:
      result: TreeDecompositionResult[TNode]
    parameters:
      heuristic: str (min_fill | min_degree)
    capability_tags:
      - graph
      - decomposition
      - treewidth
      - tree_decomposition
      - min_fill
      - min_degree
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V|^3)
      space: O(|V| + |E| + |Fill|)
    ```
    """

    def decompose(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        heuristic: str = "min_fill",
    ) -> TreeDecompositionResult[TNode]:
        """
        Builds a tree decomposition using min-fill or min-degree elimination order.

        Args:
            adjacency: Graph adjacency map.
            heuristic: 'min_fill' or 'min_degree'.

        Returns:
            TreeDecompositionResult with bags and treewidth.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n == 0:
            return TreeDecompositionResult(
                treewidth_upper_bound=0,
                bags=[],
                elimination_order=[],
                fill_edges=set(),
            )

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}
        remaining = set(nodes)
        elim_order: List[TNode] = []
        bags: List[Set[TNode]] = []
        fill_edges: Set[Tuple[TNode, TNode]] = set()

        while remaining:
            if heuristic.lower() == "min_degree":
                pivot = min(remaining, key=lambda u: (len(adj[u] & remaining), str(u)))
            else:
                pivot = self._select_min_fill(remaining, adj)

            neighbors = adj[pivot] & remaining
            bag = {pivot} | neighbors
            bags.append(bag)

            neighbor_list = list(neighbors)
            for i in range(len(neighbor_list)):
                u = neighbor_list[i]
                for j in range(i + 1, len(neighbor_list)):
                    v = neighbor_list[j]
                    if v not in adj[u]:
                        adj[u].add(v)
                        adj[v].add(u)
                        fill_edges.add((min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x))))

            elim_order.append(pivot)
            remaining.remove(pivot)

        max_bag_size = max(len(b) for b in bags) if bags else 1
        tw = max(0, max_bag_size - 1)

        return TreeDecompositionResult(
            treewidth_upper_bound=tw,
            bags=bags,
            elimination_order=elim_order,
            fill_edges=fill_edges,
        )

    def _select_min_fill(self, remaining: Set[TNode], adj: Dict[TNode, Set[TNode]]) -> TNode:
        best_node = next(iter(remaining))
        min_fill_count = float("inf")

        for u in sorted(remaining, key=lambda x: str(x)):
            neighbors = list(adj[u] & remaining)
            k = len(neighbors)
            missing = 0
            for i in range(k):
                ni = neighbors[i]
                for j in range(i + 1, k):
                    nj = neighbors[j]
                    if nj not in adj[ni]:
                        missing += 1
            if missing < min_fill_count:
                min_fill_count = missing
                best_node = u
                if missing == 0:
                    break

        return best_node
