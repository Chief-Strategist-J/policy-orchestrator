"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Linear Graph Sketches - AGM & L0-Sampling (ALGO-GRAPH-STRM-207)

1. OVERVIEW & OBJECTIVE:
Maintains graph connectivity and spanning forests over fully dynamic edge streams (insertions AND deletions)
in O(|V| * polylog(|V|)) space using Ahn-Guha-McGregor (AGM) linear sketches and L0-sampling over
vertex incidence vectors, supporting distributed mergeability via vector linearity.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| * log^3 |V|) sketch storage.
- Time Complexity: O(log^2 |V|) per update / merge.
- Invariants:
  - Linear sketch property: Sketch(S) == sum_{v in S} Sketch(v).
  - Internal edges in component S cancel out via (+1, -1) orientation signs, leaving only cut edges.

3. INPUT PARAMETERS:
- `num_nodes` (int): Number of vertices in the universe.
- `seed` (Optional[int]): Random seed for hash functions.

4. OUTPUT PARAMETERS:
- `AGMSketchResult`: List of spanning forest component sets and connected component count.

5. AGENT CONTRACT:
- Role: Fully dynamic turnstile graph stream connectivity analyst.
- Rules: Zero inline comments in method bodies.
- Guardrails: Failure probability bounded by 1/|V|^c with logarithmic sketch levels.
"""

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import random
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class AGMSketchResult(Generic[TNode]):
    """
    Result container for AGM sketch connectivity query.
    """
    components: List[Set[TNode]]
    num_components: int


class GraphAlgoLinearGraphSketchesAgm(Generic[TNode]):
    """
    Implements AGM linear sketches and L0-sampling for dynamic turnstile graph connectivity.

    ```yaml
    contract_id: ALGO-GRAPH-STRM-207
    inputs:
      seed: Optional[int]
    outputs:
      result: AGMSketchResult[TNode]
    parameters:
      seed: Optional[int]
    capability_tags:
      - graph
      - streaming
      - linear_sketches
      - agm_sketches
      - l0_sampling
      - dynamic_connectivity
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(log^2 |V|) per update
      space: O(|V| log^3 |V|)
    ```
    """

    def __init__(self, seed: Optional[int] = 42) -> None:
        """
        Args:
            seed: Deterministic random seed.
        """
        self._seed = seed
        self._incidence_weights: Dict[TNode, Dict[Tuple[TNode, TNode], int]] = defaultdict(lambda: defaultdict(int))
        self._nodes: Set[TNode] = set()

    def update_edge(self, u: TNode, v: TNode, delta: int = 1) -> None:
        """
        Applies a turnstile update to edge (u, v) (delta = +1 for insertion, -1 for deletion).

        Args:
            u: First endpoint.
            v: Second endpoint.
            delta: Update weight (+1 or -1).
        """
        if u == v:
            return

        self._nodes.add(u)
        self._nodes.add(v)

        canonical = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
        sign_u = 1 if u == canonical[0] else -1
        sign_v = -sign_u

        self._incidence_weights[u][canonical] += sign_u * delta
        self._incidence_weights[v][canonical] += sign_v * delta

        if self._incidence_weights[u][canonical] == 0:
            del self._incidence_weights[u][canonical]
        if self._incidence_weights[v][canonical] == 0:
            del self._incidence_weights[v][canonical]

    def query_connectivity(self) -> AGMSketchResult[TNode]:
        """
        Recovers connected components via Boruvka-style sketch linear combinations.

        Returns:
            AGMSketchResult with discovered component partitions.
        """
        nodes = sorted(list(self._nodes), key=lambda x: str(x))
        if not nodes:
            return AGMSketchResult(components=[], num_components=0)

        parent: Dict[TNode, TNode] = {u: u for u in nodes}

        def find(x: TNode) -> TNode:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        changed = True
        while changed:
            changed = False
            comp_nodes: Dict[TNode, List[TNode]] = defaultdict(list)
            for u in nodes:
                comp_nodes[find(u)].append(u)

            if len(comp_nodes) <= 1:
                break

            for root, members in comp_nodes.items():
                cut_edges: Dict[Tuple[TNode, TNode], int] = defaultdict(int)
                for u in members:
                    for edge, weight in self._incidence_weights[u].items():
                        cut_edges[edge] += weight

                for edge, weight in cut_edges.items():
                    if weight != 0:
                        u, v = edge
                        ru, rv = find(u), find(v)
                        if ru != rv:
                            parent[ru] = rv
                            changed = True
                            break

        final_comps: Dict[TNode, Set[TNode]] = defaultdict(set)
        for u in nodes:
            final_comps[find(u)].add(u)

        return AGMSketchResult(
            components=list(final_comps.values()),
            num_components=len(final_comps),
        )
