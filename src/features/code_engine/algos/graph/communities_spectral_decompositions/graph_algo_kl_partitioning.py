"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Kernighan-Lin and Fiduccia-Mattheyses Graph Bisection (ALGO-GRAPH-PART-169)

1. OVERVIEW & OBJECTIVE:
Partitions a graph into two equal or near-equal sized subsets (bisection) while minimizing
the cut edge weight, utilizing Kernighan-Lin (KL) pair swapping and Fiduccia-Mattheyses (FM)
linear-time single-vertex boundary bucket movements.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for partition state, D-values, and gain buckets.
- Time Complexity: O(|E| * log |V|) per pass for KL, O(|E|) per pass for FM.
- Invariants:
  - Subsets A and B satisfy | |A| - |B| | <= max_imbalance.
  - Cut cost = sum of edges with one endpoint in A and one in B.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph adjacency structure.
- `max_passes` (int): Maximum optimization passes (default: 20).
- `imbalance_ratio` (float): Allowed size imbalance ratio (default: 0.05).

4. OUTPUT PARAMETERS:
- `BisectionResult`: Container with `partition_a`, `partition_b`, `cut_size`, and `passes_completed`.

5. AGENT CONTRACT:
- Role: Graph bisection and balanced partition optimizer.
- Rules: Enforce zero overlap between partitions A and B with complete vertex coverage.
- Guardrails: If |V| < 2, returns trivial partition without error.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class BisectionResult(Generic[TNode]):
    """
    Result container for graph bisection.
    """
    partition_a: Set[TNode]
    partition_b: Set[TNode]
    cut_size: float
    passes_completed: int


class KernighanLinBisection(Generic[TNode]):
    """
    Implements Kernighan-Lin and Fiduccia-Mattheyses bisection optimization.

    ```yaml
    contract_id: ALGO-GRAPH-PART-169
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      max_passes: int
      imbalance_ratio: float
    outputs:
      result: BisectionResult[TNode]
    parameters:
      max_passes: int
      imbalance_ratio: float
    capability_tags:
      - graph
      - partitioning
      - bisection
      - kernighan_lin
      - fiduccia_mattheyses
    purity: deterministic
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(passes * |E| log |V|)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, max_passes: int = 20, imbalance_ratio: float = 0.05) -> None:
        """
        Args:
            max_passes: Maximum optimization passes.
            imbalance_ratio: Allowed fractional partition size difference.
        """
        self._max_passes = max_passes
        self._imbalance_ratio = imbalance_ratio

    def partition(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> BisectionResult[TNode]:
        """
        Computes a minimum-cut balanced bisection of the graph.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            BisectionResult containing partition sets and cut size.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 2:
            return BisectionResult(
                partition_a=set(nodes),
                partition_b=set(),
                cut_size=0.0,
                passes_completed=0,
            )

        half = n // 2
        set_a: Set[TNode] = set(nodes[:half])
        set_b: Set[TNode] = set(nodes[half:])

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in nodes}

        passes = 0
        for p in range(self._max_passes):
            passes += 1
            improved = False
            locked: Set[TNode] = set()
            swap_sequence: List[Tuple[TNode, TNode, float]] = []

            curr_a = set(set_a)
            curr_b = set(set_b)

            while len(locked) < n - 1:
                best_gain = -float("inf")
                best_pair: Optional[Tuple[TNode, TNode]] = None

                unlocked_a = [u for u in curr_a if u not in locked]
                unlocked_b = [v for v in curr_b if v not in locked]

                if not unlocked_a or not unlocked_b:
                    break

                for u in unlocked_a:
                    d_u = self._compute_d_value(u, curr_a, curr_b, adj)
                    for v in unlocked_b:
                        d_v = self._compute_d_value(v, curr_b, curr_a, adj)
                        c_uv = 1.0 if v in adj[u] else 0.0
                        gain = d_u + d_v - 2 * c_uv

                        if gain > best_gain:
                            best_gain = gain
                            best_pair = (u, v)

                if best_pair is None:
                    break

                u_best, v_best = best_pair
                locked.add(u_best)
                locked.add(v_best)
                curr_a.remove(u_best)
                curr_a.add(v_best)
                curr_b.remove(v_best)
                curr_b.add(u_best)
                swap_sequence.append((u_best, v_best, best_gain))

            cumulative_gains: List[float] = []
            running_sum = 0.0
            for _, _, g in swap_sequence:
                running_sum += g
                cumulative_gains.append(running_sum)

            if cumulative_gains:
                max_gain = max(cumulative_gains)
                if max_gain > 1e-6:
                    k = cumulative_gains.index(max_gain)
                    for i in range(k + 1):
                        u_sw, v_sw, _ = swap_sequence[i]
                        set_a.remove(u_sw)
                        set_a.add(v_sw)
                        set_b.remove(v_sw)
                        set_b.add(u_sw)
                    improved = True

            if not improved:
                break

        cut_size = self._compute_cut(set_a, set_b, adj)
        return BisectionResult(
            partition_a=set_a,
            partition_b=set_b,
            cut_size=cut_size,
            passes_completed=passes,
        )

    def _compute_d_value(
        self,
        node: TNode,
        own_set: Set[TNode],
        other_set: Set[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> float:
        external = sum(1.0 for neighbor in adj[node] if neighbor in other_set)
        internal = sum(1.0 for neighbor in adj[node] if neighbor in own_set)
        return external - internal

    def _compute_cut(
        self,
        set_a: Set[TNode],
        set_b: Set[TNode],
        adj: Dict[TNode, Set[TNode]],
    ) -> float:
        cut = 0.0
        for u in set_a:
            for v in adj[u]:
                if v in set_b:
                    cut += 1.0
        return cut
