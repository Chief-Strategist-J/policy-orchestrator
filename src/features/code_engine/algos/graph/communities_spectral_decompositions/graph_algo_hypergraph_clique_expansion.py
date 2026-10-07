"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Hypergraph Clique and Star Expansion (ALGO-GRAPH-COMM-165)

1. OVERVIEW & OBJECTIVE:
Provides dual transformation paradigms (Clique Expansion and Star Expansion) to project
higher-order hypergraphs (where hyperedges connect arbitrary subsets of vertices) into
standard graphs suitable for traditional community detection, spectral analysis, and clustering.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + sum(|e|)) for Star Expansion, O(|V| + sum(|e|^2)) for Clique Expansion.
- Time Complexity: O(sum(|e|^2)) for Clique Expansion, O(sum(|e|)) for Star Expansion.
- Invariants:
  - Clique expansion adds an edge between every pair of vertices in a hyperedge with weight 1/(|e|-1) or 1.
  - Star expansion creates auxiliary bipartite vertices for hyperedges.

3. INPUT PARAMETERS:
- `hyperedges` (Iterable[Iterable[TNode]]): List of hyperedges, each an iterable of node identifiers.
- `weighted` (bool): Whether to weight clique edges inversely by hyperedge size (default: True).

4. OUTPUT PARAMETERS:
- `Dict[TNode, Dict[TNode, float]]`: Weighted adjacency representation of the expanded graph.

5. AGENT CONTRACT:
- Role: Hypergraph transformation and projection engine.
- Rules: Preserve vertex set integrity; prune singletons or isolated hyperedges safely.
- Guardrails: Hyperedges of size < 2 are handled gracefully without zero-division errors.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar, Union

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class HypergraphProjectionResult(Generic[TNode]):
    """
    Container for projected graph representation.
    """
    adjacency: Dict[TNode, Dict[TNode, float]]
    node_count: int
    edge_count: int


class HypergraphProjector(Generic[TNode]):
    """
    Transforms hypergraphs via clique expansion or star expansion.

    ```yaml
    contract_id: ALGO-GRAPH-COMM-165
    inputs:
      hyperedges: Iterable[Iterable[TNode]]
      weighted: bool
    outputs:
      result: HypergraphProjectionResult[TNode]
    parameters:
      expansion_mode: str (clique | star)
    capability_tags:
      - graph
      - hypergraph
      - projection
      - expansion
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(sum(|e|^2))
      space: O(|V| + sum(|e|^2))
    ```
    """

    def clique_expansion(
        self,
        hyperedges: Iterable[Iterable[TNode]],
        weighted: bool = True,
    ) -> HypergraphProjectionResult[TNode]:
        """
        Projects hyperedges to a standard graph using pairwise clique expansion.

        Args:
            hyperedges: Collection of hyperedges.
            weighted: If True, edge weights are normalized by 1 / (|e| - 1).

        Returns:
            HypergraphProjectionResult containing weighted adjacency map.
        """
        adj: Dict[TNode, Dict[TNode, float]] = defaultdict(lambda: defaultdict(float))
        nodes: Set[TNode] = set()

        for edge in hyperedges:
            members = list(set(edge))
            for m in members:
                nodes.add(m)
                if m not in adj:
                    adj[m] = defaultdict(float)

            k = len(members)
            if k < 2:
                continue

            weight = 1.0 / (k - 1) if (weighted and k > 1) else 1.0
            for u, v in combinations(members, 2):
                adj[u][v] += weight
                adj[v][u] += weight

        total_edges = sum(len(neighbors) for neighbors in adj.values()) // 2
        return HypergraphProjectionResult(
            adjacency={k: dict(v) for k, v in adj.items()},
            node_count=len(nodes),
            edge_count=total_edges,
        )

    def star_expansion(
        self,
        hyperedges: Iterable[Iterable[TNode]],
    ) -> HypergraphProjectionResult[Union[TNode, str]]:
        """
        Constructs a bipartite star expansion with auxiliary hyperedge nodes.

        Args:
            hyperedges: Collection of hyperedges.

        Returns:
            HypergraphProjectionResult with union of original nodes and auxiliary hyperedge nodes.
        """
        adj: Dict[Union[TNode, str], Dict[Union[TNode, str], float]] = defaultdict(lambda: defaultdict(float))
        nodes: Set[Union[TNode, str]] = set()

        for idx, edge in enumerate(hyperedges):
            hyperedge_node = f"__hyperedge_{idx}__"
            nodes.add(hyperedge_node)
            adj[hyperedge_node] = defaultdict(float)

            members = list(set(edge))
            for m in members:
                nodes.add(m)
                if m not in adj:
                    adj[m] = defaultdict(float)
                adj[m][hyperedge_node] = 1.0
                adj[hyperedge_node][m] = 1.0

        total_edges = sum(len(neighbors) for neighbors in adj.values()) // 2
        return HypergraphProjectionResult(
            adjacency={k: dict(v) for k, v in adj.items()},
            node_count=len(nodes),
            edge_count=total_edges,
        )
