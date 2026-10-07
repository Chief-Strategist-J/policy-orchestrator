"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Clique Tree and Junction Tree Construction (ALGO-GRAPH-DEC-189)

1. OVERVIEW & OBJECTIVE:
Constructs a Junction Tree (Clique Tree) from a chordal graph or triangulated Bayesian/Markov
network using maximal clique listing and Maximum Weight Spanning Tree (MWST) over the clique
intersection graph, guaranteeing the Running Intersection Property (RIP) for message-passing inference.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|MaxCliques| + |E_clique|) junction tree nodes and separator sets.
- Time Complexity: O(|V| + |E| + |MaxCliques|^2) for MWST over clique graph.
- Invariants:
  - Running Intersection Property: For any two cliques C_i and C_j, every clique on the unique tree path between them contains C_i intersect C_j.
  - Separators S_ij = C_i intersect C_j.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Chordal graph adjacency structure.

4. OUTPUT PARAMETERS:
- `JunctionTreeResult`: Maximal cliques (bags), separators on tree edges, and tree adjacency.

5. AGENT CONTRACT:
- Role: Probabilistic graphical model inference tree constructor.
- Rules: Enforce Running Intersection Property across all tree paths.
- Guardrails: Non-chordal graphs should be triangulated prior to junction tree generation.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class JunctionTreeResult(Generic[TNode]):
    """
    Result container for Junction Tree / Clique Tree.
    """
    cliques: List[Set[TNode]]
    tree_edges: List[Tuple[int, int]]
    separators: Dict[Tuple[int, int], Set[TNode]]
    num_cliques: int


class JunctionTreeBuilder(Generic[TNode]):
    """
    Constructs Junction Trees satisfying the Running Intersection Property.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-189
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: JunctionTreeResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - junction_tree
      - clique_tree
      - rip
      - probabilistic_graphical_models
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E| + |C|^2)
      space: O(|C|^2)
    ```
    """

    def build(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> JunctionTreeResult[TNode]:
        """
        Extracts maximal cliques and builds the junction tree.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            JunctionTreeResult with tree edges and separators.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return JunctionTreeResult(cliques=[], tree_edges=[], separators={}, num_cliques=0)

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        cliques = self._find_maximal_cliques(nodes, adj)
        k = len(cliques)
        if k <= 1:
            return JunctionTreeResult(cliques=cliques, tree_edges=[], separators={}, num_cliques=k)

        intersection_edges: List[Tuple[int, int, int]] = []
        for i in range(k):
            for j in range(i + 1, k):
                common = len(cliques[i] & cliques[j])
                if common > 0:
                    intersection_edges.append((i, j, common))

        intersection_edges.sort(key=lambda item: (-item[2], item[0], item[1]))

        parent = list(range(k))

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        tree_edges: List[Tuple[int, int]] = []
        separators: Dict[Tuple[int, int], Set[TNode]] = {}

        for i, j, weight in intersection_edges:
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                tree_edges.append((i, j))
                sep = cliques[i] & cliques[j]
                separators[(i, j)] = sep
                separators[(j, i)] = sep
                if len(tree_edges) == k - 1:
                    break

        return JunctionTreeResult(
            cliques=cliques,
            tree_edges=tree_edges,
            separators=separators,
            num_cliques=k,
        )

    def _find_maximal_cliques(
        self,
        nodes: List[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> List[Set[TNode]]:
        cliques: List[Set[TNode]] = []
        
        for start in nodes:
            c: Set[TNode] = {start}
            for u in nodes:
                if u not in c and all(member in adj[u] for member in c):
                    c.add(u)
            
            is_sub = False
            for existing in cliques:
                if c.issubset(existing):
                    is_sub = True
                    break
            if not is_sub:
                cliques = [existing for existing in cliques if not existing.issubset(c)]
                cliques.append(c)

        return cliques
