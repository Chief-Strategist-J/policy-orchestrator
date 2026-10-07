"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Biconnected Components and Cut Vertices (ALGO-GRAPH-DEC-191)

1. OVERVIEW & OBJECTIVE:
Decomposes an undirected graph into its 2-vertex-connected maximal subgraphs (blocks) and
identifies all articulation points (cut vertices) and bridges in linear time O(|V| + |E|)
using Hopcroft-Tarjan DFS discovery low-link traversal with an explicit edge stack.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) DFS low-link and edge stack buffers.
- Time Complexity: O(|V| + |E|) single-pass DFS.
- Invariants:
  - Every edge belongs to exactly one biconnected component (block).
  - A vertex is an articulation point iff it belongs to >= 2 biconnected components.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `BiconnectedResult`: List of biconnected component edge sets, set of articulation points, and list of bridges.

5. AGENT CONTRACT:
- Role: Fault tolerance, single-point-of-failure, and structural robustness analyst.
- Rules: Block-cut tree equivalence must hold across all components.
- Guardrails: Handle disconnected graphs seamlessly by traversing all forest roots.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class BiconnectedResult(Generic[TNode]):
    """
    Result container for biconnected component decomposition.
    """
    blocks: List[Set[Tuple[TNode, TNode]]]
    articulation_points: Set[TNode]
    bridges: Set[Tuple[TNode, TNode]]
    num_blocks: int


class BiconnectedComponentsHopcroft(Generic[TNode]):
    """
    Computes biconnected components, articulation points, and bridges via DFS low-link.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-191
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: BiconnectedResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - biconnected_components
      - articulation_points
      - bridges
      - hopcroft_tarjan
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E|)
      space: O(|V| + |E|)
    ```
    """

    def decompose(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> BiconnectedResult[TNode]:
        """
        Decomposes graph into 2-connected blocks and cut vertices.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            BiconnectedResult with blocks and articulation points.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return BiconnectedResult(blocks=[], articulation_points=set(), bridges=set(), num_blocks=0)

        adj: Dict[TNode, List[TNode]] = {
            u: sorted(list(set(adjacency.get(u, ()))), key=lambda x: str(x)) for u in nodes
        }

        tin: Dict[TNode, int] = {}
        low: Dict[TNode, int] = {}
        timer = 0

        edge_stack: List[Tuple[TNode, TNode]] = []
        blocks: List[Set[Tuple[TNode, TNode]]] = []
        cut_vertices: Set[TNode] = set()
        bridges: Set[Tuple[TNode, TNode]] = set()

        def dfs(u: TNode, parent: Optional[TNode] = None) -> None:
            nonlocal timer
            tin[u] = timer
            low[u] = timer
            timer += 1
            children = 0

            for v in adj[u]:
                if v == parent:
                    continue
                canonical_edge = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))

                if v in tin:
                    low[u] = min(low[u], tin[v])
                    if tin[v] < tin[u]:
                        edge_stack.append(canonical_edge)
                else:
                    edge_stack.append(canonical_edge)
                    children += 1
                    dfs(v, u)
                    low[u] = min(low[u], low[v])

                    if low[v] > tin[u]:
                        bridges.add(canonical_edge)

                    if (parent is not None and low[v] >= tin[u]) or (parent is None and children > 1):
                        cut_vertices.add(u)

                    if low[v] >= tin[u]:
                        block: Set[Tuple[TNode, TNode]] = set()
                        while edge_stack:
                            top_edge = edge_stack.pop()
                            block.add(top_edge)
                            if top_edge == canonical_edge:
                                break
                        if block:
                            blocks.append(block)

        for root in nodes:
            if root not in tin:
                dfs(root, None)
                if edge_stack:
                    block = set(edge_stack)
                    edge_stack.clear()
                    blocks.append(block)

        return BiconnectedResult(
            blocks=blocks,
            articulation_points=cut_vertices,
            bridges=bridges,
            num_blocks=len(blocks),
        )
