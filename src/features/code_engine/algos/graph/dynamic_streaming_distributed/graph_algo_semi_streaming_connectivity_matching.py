"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Semi-Streaming Connectivity and Matching (ALGO-GRAPH-STRM-206)

1. OVERVIEW & OBJECTIVE:
Processes unbounded graph edge streams in a single pass using restricted semi-streaming space
O(|V| * polylog(|V|)) to maintain connected components (Union-Find) and compute a 1/2-approximate
maximal matching without storing all edges in memory.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V|) memory for disjoint set parents and matching endpoint sets.
- Time Complexity: O(1) amortized per streamed edge arrival.
- Invariants:
  - Memory strictly bounded by O(|V|) regardless of stream length |E|.
  - Maximal matching output has cardinality >= (1/2) * |Maximum Matching|.

3. INPUT PARAMETERS:
- None for initialization.

4. OUTPUT PARAMETERS:
- `StreamingStateResult`: Number of connected components, matching size, and matched edge set.

5. AGENT CONTRACT:
- Role: Single-pass streaming stream processor for massive graph streams.
- Rules: Zero inline comments in method bodies.
- Guardrails: If vertices in stream exceed expected bounds, automatically scales parent arrays.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class StreamingStateResult(Generic[TNode]):
    """
    Result container for semi-streaming graph queries.
    """
    num_components: int
    matching_size: int
    maximal_matching: Set[Tuple[TNode, TNode]]


class GraphAlgoSemiStreamingConnectivityMatching(Generic[TNode]):
    """
    Maintains connectivity and maximal matching in O(|V|) space over edge streams.

    ```yaml
    contract_id: ALGO-GRAPH-STRM-206
    inputs: {}
    outputs:
      result: StreamingStateResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - streaming
      - semi_streaming
      - disjoint_set
      - matching
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(1) amortized per edge
      space: O(|V|)
    ```
    """

    def __init__(self) -> None:
        self._parent: Dict[TNode, TNode] = {}
        self._matched_nodes: Set[TNode] = set()
        self._matching_edges: Set[Tuple[TNode, TNode]] = set()
        self._component_count: int = 0

    def _find(self, u: TNode) -> TNode:
        if u not in self._parent:
            self._parent[u] = u
            self._component_count += 1
            return u
        if self._parent[u] != u:
            self._parent[u] = self._find(self._parent[u])
        return self._parent[u]

    def _union(self, u: TNode, v: TNode) -> None:
        ru = self._find(u)
        rv = self._find(v)
        if ru != rv:
            self._parent[ru] = rv
            self._component_count -= 1

    def process_edge(self, u: TNode, v: TNode) -> None:
        """
        Ingests a streamed edge (u, v) in single-pass O(1) time.

        Args:
            u: First endpoint.
            v: Second endpoint.
        """
        if u == v:
            return

        self._union(u, v)

        if u not in self._matched_nodes and v not in self._matched_nodes:
            self._matched_nodes.add(u)
            self._matched_nodes.add(v)
            edge = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
            self._matching_edges.add(edge)

    def process_stream(self, stream: Iterable[Tuple[TNode, TNode]]) -> StreamingStateResult[TNode]:
        """
        Streams a sequence of edges and returns the final state.

        Args:
            stream: Iterable of (u, v) edges.

        Returns:
            StreamingStateResult with component count and matching.
        """
        for u, v in stream:
            self.process_edge(u, v)

        return self.get_summary()

    def get_summary(self) -> StreamingStateResult[TNode]:
        """
        Returns the current streaming summary state.

        Returns:
            StreamingStateResult container.
        """
        return StreamingStateResult(
            num_components=self._component_count,
            matching_size=len(self._matching_edges),
            maximal_matching=set(self._matching_edges),
        )
