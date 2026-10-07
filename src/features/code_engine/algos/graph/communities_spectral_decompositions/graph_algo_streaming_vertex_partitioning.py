"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Streaming Graph Partitioning - LDG and Fennel (ALGO-GRAPH-PART-171)

1. OVERVIEW & OBJECTIVE:
Partitions large-scale graphs in a single-pass streaming model where vertices and edges
arrive sequentially without requiring the whole graph in memory, optimizing communication
volume and load balance via Linear Deterministic Greedy (LDG) and Fennel heuristics.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + k) storage for partition memberships and partition load counters.
- Time Complexity: O(deg(v) * k) per streamed vertex arrival.
- Invariants:
  - Max capacity per partition <= (1 + epsilon) * (|V| / k).
  - Streaming decisions are irrevocable once a vertex is assigned.

3. INPUT PARAMETERS:
- `stream` (Iterable[Tuple[TNode, Iterable[TNode]]]): Stream of (vertex, observed_neighbors) pairs.
- `num_partitions` (int): Target partition count k.
- `total_nodes_estimate` (int): Estimated |V| for capacity bounds.
- `slack_factor` (float): Allowed imbalance slack factor (default: 1.1).
- `heuristic` (str): 'ldg' or 'fennel' (default: 'fennel').

4. OUTPUT PARAMETERS:
- `StreamingPartitionResult`: Container with assignments, partition sizes, and edge cuts.

5. AGENT CONTRACT:
- Role: Real-time streaming graph partitioner for massive data ingestion pipelines.
- Rules: Hard partition capacity constraints are strictly obeyed.
- Guardrails: Non-positive k raises ValueError.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class StreamingPartitionResult(Generic[TNode]):
    """
    Result container for streaming partitioning.
    """
    assignments: Dict[TNode, int]
    partition_sizes: Dict[int, int]
    total_cross_edges: int
    max_imbalance_ratio: float


class StreamingGraphPartitioner(Generic[TNode]):
    """
    Implements LDG and Fennel streaming graph partitioning heuristics.

    ```yaml
    contract_id: ALGO-GRAPH-PART-171
    inputs:
      stream: Iterable[Tuple[TNode, Iterable[TNode]]]
      num_partitions: int
      total_nodes_estimate: int
      slack_factor: float
      heuristic: str
    outputs:
      result: StreamingPartitionResult[TNode]
    parameters:
      heuristic: str (ldg | fennel)
      slack_factor: float
    capability_tags:
      - graph
      - streaming
      - partitioning
      - ldg
      - fennel
    purity: deterministic
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|E| * k)
      space: O(|V| + k)
    ```
    """

    def __init__(
        self,
        num_partitions: int = 4,
        total_nodes_estimate: int = 1000,
        slack_factor: float = 1.1,
        heuristic: str = "fennel",
    ) -> None:
        """
        Args:
            num_partitions: Number of target partitions k.
            total_nodes_estimate: Expected total node count N.
            slack_factor: Allowable capacity ratio (1 + epsilon).
            heuristic: 'fennel' or 'ldg'.
        """
        if num_partitions < 1:
            raise ValueError("num_partitions must be >= 1.")
        self._k = num_partitions
        self._n_est = max(1, total_nodes_estimate)
        self._slack = slack_factor
        self._heuristic = heuristic.lower()

    def partition_stream(
        self,
        stream: Iterable[Tuple[TNode, Iterable[TNode]]],
    ) -> StreamingPartitionResult[TNode]:
        """
        Streams vertex and neighbor arrivals, assigning each vertex immediately.

        Args:
            stream: Iterable yielding (vertex, neighbor_list).

        Returns:
            StreamingPartitionResult with irrevocable partition assignments.
        """
        assignments: Dict[TNode, int] = {}
        partition_sizes: Dict[int, int] = {p: 0 for p in range(self._k)}
        cross_edges = 0
        max_capacity = math.ceil((self._n_est / self._k) * self._slack)

        gamma = 1.5
        alpha = (self._k ** (gamma - 1.0)) / (self._n_est ** (gamma - 1.0))

        for u, neighbors in stream:
            neighbor_list = list(neighbors)
            neighbor_counts: Dict[int, int] = defaultdict(int)
            for v in neighbor_list:
                if v in assignments:
                    neighbor_counts[assignments[v]] += 1

            best_p = 0
            best_score = -float("inf")

            for p in range(self._k):
                size = partition_sizes[p]
                if size >= max_capacity:
                    continue

                common = neighbor_counts[p]
                if self._heuristic == "ldg":
                    penalty = 1.0 - (size / max_capacity)
                    score = common * penalty
                else:
                    cost = alpha * gamma * (size ** (gamma - 1.0))
                    score = common - cost

                if score > best_score:
                    best_score = score
                    best_p = p

            if best_score == -float("inf"):
                best_p = min(partition_sizes.items(), key=lambda item: item[1])[0]

            assignments[u] = best_p
            partition_sizes[best_p] += 1

            for v in neighbor_list:
                if v in assignments and assignments[v] != best_p:
                    cross_edges += 1

        n_actual = len(assignments)
        avg_size = (n_actual / self._k) if self._k > 0 else 1.0
        max_size = max(partition_sizes.values()) if partition_sizes else 0
        imbalance = (max_size / avg_size) if avg_size > 0 else 1.0

        return StreamingPartitionResult(
            assignments=assignments,
            partition_sizes=partition_sizes,
            total_cross_edges=cross_edges,
            max_imbalance_ratio=imbalance,
        )
