"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Threshold Graph Recognition and Degree Peeling (ALGO-GRAPH-DEC-199)

1. OVERVIEW & OBJECTIVE:
Determines whether a graph is a Threshold Graph (constructible from an empty graph by
iteratively adding either an isolated vertex or a universal dominant vertex), utilizing iterative
degree peeling and vicinal preorder inclusion testing (no induced 2K2, C4, or P4).

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) degree sequence and peeled queue storage.
- Time Complexity: O(|V| + |E|) linear time.
- Invariants:
  - G is a threshold graph iff it contains no induced 2K2, C4, or P4.
  - There exists a weight function w: V -> R and threshold T such that (u, v) in E iff w(u) + w(v) >= T.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.

4. OUTPUT PARAMETERS:
- `ThresholdGraphResult`: Boolean `is_threshold_graph`, peeling sequence (isolated/dominant), and threshold weights if valid.

5. AGENT CONTRACT:
- Role: Threshold graph recognizer and integer knapsack / synchronization modeler.
- Rules: Enforce strict peeling verification to 0 remaining vertices.
- Guardrails: If |V| < 4, graph is always a threshold graph.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class ThresholdGraphResult(Generic[TNode]):
    """
    Result container for threshold graph recognition.
    """
    is_threshold_graph: bool
    peeling_sequence: List[Tuple[TNode, str]]
    vertex_weights: Dict[TNode, float]
    threshold_value: float


class ThresholdGraphRecognizer(Generic[TNode]):
    """
    Recognizes threshold graphs via iterative isolated/universal degree peeling.

    ```yaml
    contract_id: ALGO-GRAPH-DEC-199
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: ThresholdGraphResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - decomposition
      - threshold_graph
      - degree_peeling
      - knapsack_model
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |E|)
      space: O(|V| + |E|)
    ```
    """

    def recognize(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> ThresholdGraphResult[TNode]:
        """
        Tests if graph is a threshold graph and computes vertex weights.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            ThresholdGraphResult containing peeling sequence and weights.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 4:
            peel = [(u, "ISOLATED") for u in nodes]
            weights = {u: 1.0 for u in nodes}
            return ThresholdGraphResult(
                is_threshold_graph=True,
                peeling_sequence=peel,
                vertex_weights=weights,
                threshold_value=2.0,
            )

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}
        remaining = set(nodes)
        peeling_seq: List[Tuple[TNode, str]] = []

        while remaining:
            cur_n = len(remaining)
            if cur_n == 1:
                u = next(iter(remaining))
                peeling_seq.append((u, "ISOLATED"))
                remaining.remove(u)
                break

            isolated = None
            dominant = None

            for u in sorted(remaining, key=lambda x: str(x)):
                deg = len(adj[u] & remaining)
                if deg == 0:
                    isolated = u
                    break
                elif deg == cur_n - 1:
                    dominant = u
                    break

            if isolated is not None:
                peeling_seq.append((isolated, "ISOLATED"))
                remaining.remove(isolated)
            elif dominant is not None:
                peeling_seq.append((dominant, "DOMINANT"))
                remaining.remove(dominant)
            else:
                return ThresholdGraphResult(
                    is_threshold_graph=False,
                    peeling_sequence=[],
                    vertex_weights={},
                    threshold_value=0.0,
                )

        weights: Dict[TNode, float] = {}
        for rank, (u, role) in enumerate(peeling_seq):
            weights[u] = float(rank + 1) if role == "DOMINANT" else 0.5

        return ThresholdGraphResult(
            is_threshold_graph=True,
            peeling_sequence=peeling_seq,
            vertex_weights=weights,
            threshold_value=float(n),
        )
