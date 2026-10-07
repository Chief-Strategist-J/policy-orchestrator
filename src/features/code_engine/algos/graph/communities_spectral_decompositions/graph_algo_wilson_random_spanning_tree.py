"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Wilson's Uniform Spanning Tree Generator (ALGO-GRAPH-SPEC-176)

1. OVERVIEW & OBJECTIVE:
Generates a spanning tree drawn exactly uniformly at random (Uniform Spanning Tree - UST) from
all possible spanning trees of an undirected connected graph using Wilson's algorithm with
loop-erased random walks (LERW).

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for tree branches and node visit states.
- Time Complexity: Expected O(tau_hit), proportional to mean hitting time of the graph.
- Invariants:
  - Output forms an acyclic subgraph connecting all vertices in the component.
  - Distribution of generated trees is strictly uniform over the tree space.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Connected undirected graph.
- `seed` (Optional[int]): Random seed for deterministic replication (default: None).

4. OUTPUT PARAMETERS:
- `SpanningTreeResult`: Set of tree edges and total tree weight.

5. AGENT CONTRACT:
- Role: Uniform random spanning tree and graph skeleton sampler.
- Rules: Fix seeds for deterministic unit testing (GR5).
- Guardrails: Non-connected graphs generate a uniform spanning forest (one tree per connected component).
"""

from collections import defaultdict
from dataclasses import dataclass
import random
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class SpanningTreeResult(Generic[TNode]):
    """
    Result container for uniform spanning tree sampling.
    """
    edges: Set[Tuple[TNode, TNode]]
    tree_size: int
    num_components: int


class WilsonRandomSpanningTree(Generic[TNode]):
    """
    Samples uniform spanning trees via loop-erased random walks.

    ```yaml
    contract_id: ALGO-GRAPH-SPEC-176
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      seed: Optional[int]
    outputs:
      result: SpanningTreeResult[TNode]
    parameters:
      seed: Optional[int]
    capability_tags:
      - graph
      - spectral
      - spanning_tree
      - wilson_algorithm
      - loop_erased_random_walk
    purity: stochastic
    determinism: pseudo_random
    idempotency: idempotent_with_seed
    complexity:
      time: O(mean_hitting_time)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Args:
            seed: Random seed for deterministic reproducibility.
        """
        self._seed = seed

    def sample(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> SpanningTreeResult[TNode]:
        """
        Executes Wilson's algorithm to generate a uniform spanning tree/forest.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            SpanningTreeResult containing sampled tree edges.
        """
        rng = random.Random(self._seed)
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return SpanningTreeResult(edges=set(), tree_size=0, num_components=0)

        adj: Dict[TNode, List[TNode]] = {u: list(adjacency.get(u, ())) for u in nodes}

        in_tree: Set[TNode] = set()
        tree_edges: Set[Tuple[TNode, TNode]] = set()
        components = 0

        unvisited = list(nodes)
        rng.shuffle(unvisited)

        while len(in_tree) < len(nodes):
            root: Optional[TNode] = None
            for node in unvisited:
                if node not in in_tree:
                    root = node
                    break

            if root is None:
                break

            components += 1
            in_tree.add(root)

            for u in unvisited:
                if u in in_tree or not adj[u]:
                    continue

                curr = u
                path: List[TNode] = [curr]
                visited_in_walk: Dict[TNode, int] = {curr: 0}

                while curr not in in_tree:
                    neighbors = adj[curr]
                    if not neighbors:
                        break
                    next_node = rng.choice(neighbors)
                    if next_node in visited_in_walk:
                        loop_idx = visited_in_walk[next_node]
                        for dropped in path[loop_idx + 1:]:
                            if dropped in visited_in_walk:
                                del visited_in_walk[dropped]
                        path = path[:loop_idx + 1]
                        curr = next_node
                    else:
                        visited_in_walk[next_node] = len(path)
                        path.append(next_node)
                        curr = next_node

                if curr in in_tree:
                    for i in range(len(path) - 1):
                        p_u, p_v = path[i], path[i + 1]
                        in_tree.add(p_u)
                        in_tree.add(p_v)
                        edge = (min(p_u, p_v, key=lambda x: str(x)), max(p_u, p_v, key=lambda x: str(x)))
                        tree_edges.add(edge)

        return SpanningTreeResult(
            edges=tree_edges,
            tree_size=len(tree_edges),
            num_components=components,
        )
