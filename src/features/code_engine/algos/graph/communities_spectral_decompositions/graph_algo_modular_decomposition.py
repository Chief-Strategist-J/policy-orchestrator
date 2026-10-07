"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Modular Decomposition Tree (ALGO-GRAPH-DEC-193)

1. OVERVIEW & OBJECTIVE:
Computes the Modular Decomposition Tree of an undirected graph, factoring vertices into
modules M subset V (where all vertices outside M see all vertices in M identically), classifying
internal tree nodes into Parallel (disconnected), Series (complete join), and Prime (indecomposable).

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) modular tree representation.
- Time Complexity: O(|V| + |E|) linear / O(|V|^2) quotient factoring.
- Invariants:
  - Parallel modules correspond to connected components of G.
  - Series modules correspond to connected components of the graph complement G_bar.
  - Prime modules have no non-trivial module partitions.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `ModularDecompositionResult`: Modular tree nodes (Prime/Series/Parallel/Leaf) and hierarchy.

5. AGENT CONTRACT:
- Role: Structural quotient factoring and graph grammar analyzer.
- Rules: Classification must strictly match module neighborhood definitions.
- Guardrails: Single vertex inputs return a single Leaf module node.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class ModuleNode(Generic[TNode]):
    """
    Representation of a node in the Modular Decomposition Tree.
    """
    module_id: int
    module_type: str
    members: Set[TNode]
    children_ids: List[int]


@dataclass(frozen=True)
class ModularDecompositionResult(Generic[TNode]):
    """
    Result container for modular decomposition.
    """
    nodes: Dict[int, ModuleNode[TNode]]
    root_id: int
    is_cograph: bool


class ModularDecomposition(Generic[TNode]):
    """
    Constructs the Modular Decomposition Tree of a graph.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-193
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: ModularDecompositionResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - modular_decomposition
      - modules
      - cograph
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V|^2)
      space: O(|V| + |E|)
    ```
    """

    def decompose(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> ModularDecompositionResult[TNode]:
        """
        Computes the modular tree decomposition.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            ModularDecompositionResult with modular tree hierarchy.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            empty_node = ModuleNode(module_id=0, module_type="LEAF", members=set(), children_ids=[])
            return ModularDecompositionResult(nodes={0: empty_node}, root_id=0, is_cograph=True)

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        node_map: Dict[int, ModuleNode[TNode]] = {}
        counter = 0

        def build_tree(subset: List[TNode]) -> int:
            nonlocal counter
            my_id = counter
            counter += 1

            if len(subset) == 1:
                node_map[my_id] = ModuleNode(
                    module_id=my_id,
                    module_type="LEAF",
                    members=set(subset),
                    children_ids=[],
                )
                return my_id

            sub_set = set(subset)
            sub_adj = {u: adj[u] & sub_set for u in subset}

            components = self._get_components(subset, sub_adj)
            if len(components) > 1:
                child_ids = [build_tree(comp) for comp in components]
                node_map[my_id] = ModuleNode(
                    module_id=my_id,
                    module_type="PARALLEL",
                    members=sub_set,
                    children_ids=child_ids,
                )
                return my_id

            comp_adj = {u: (sub_set - {u}) - sub_adj[u] for u in subset}
            co_components = self._get_components(subset, comp_adj)
            if len(co_components) > 1:
                child_ids = [build_tree(comp) for comp in co_components]
                node_map[my_id] = ModuleNode(
                    module_id=my_id,
                    module_type="SERIES",
                    members=sub_set,
                    children_ids=child_ids,
                )
                return my_id

            child_ids = [build_tree([u]) for u in subset]
            node_map[my_id] = ModuleNode(
                module_id=my_id,
                module_type="PRIME",
                members=sub_set,
                children_ids=child_ids,
            )
            return my_id

        root_id = build_tree(nodes)
        has_prime = any(node.module_type == "PRIME" for node in node_map.values())

        return ModularDecompositionResult(
            nodes=node_map,
            root_id=root_id,
            is_cograph=not has_prime,
        )

    def _get_components(self, nodes: List[TNode], adj: Dict[TNode, Set[TNode]]) -> List[List[TNode]]:
        visited: Set[TNode] = set()
        components: List[List[TNode]] = []

        for u in nodes:
            if u not in visited:
                comp: List[TNode] = []
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
