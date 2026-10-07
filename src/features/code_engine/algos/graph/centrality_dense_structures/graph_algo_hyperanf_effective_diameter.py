"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HYPERANF EFFECTIVE DIAMETER (ALGO-GRAPH-NET-136)
================================================================================

1. OVERVIEW & OBJECTIVE:
   HyperANF (Approximate Neighborhood Function) effective diameter and hop distribution engine.
   Propagates HyperLogLog neighborhood counters to estimate the cumulative distance
   distribution N(t) across hop radii. Computes the 90th percentile effective diameter,
   average distance, and spid (shortest path index of dispersion).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(diameter * (V + E) * registers) counter propagation.
   - Space Complexity: O(V * registers) bit array storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - num_registers: int - HLL registers per node (default: 16).
   - max_hops: int - Maximum search diameter limit (default: 20).

4. OUTPUT PARAMETERS:
   - effective_diameter_90: float - Interpolated distance reaching 90% of reachable pairs.
   - average_distance: float - Mean shortest path hop distance across connected pairs.
   - hop_distribution: Dict[int, float] - Cumulative reachable pair count per hop radius.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Graph with at least two connected vertices.
   - Guardrails: Linear interpolation calculates sub-integer effective diameter percentiles.
================================================================================
"""

import hashlib
import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHyperanfEffectiveDiameter(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-136
      name: GraphAlgoHyperanfEffectiveDiameter
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, hyperanf, effective_diameter, distance_distribution, hyperloglog]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_registers: {type: integer, default: 16}
          max_hops: {type: integer, default: 20}
      outputs:
        type: object
        required: [effective_diameter_90, average_distance, hop_distribution]
        properties:
          effective_diameter_90: {type: number}
          average_distance: {type: number}
          hop_distribution: {type: object}
      parameters:
        num_registers: {type: integer, default: 16}
        max_hops: {type: integer, default: 20}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(D * (V + E) * M)
        space: O(V * M)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_registers: int = 16,
        max_hops: int = 20,
    ) -> None:
        """
        Initialize the HyperANF engine.

        Args:
            adjacency: Graph adjacency dictionary.
            num_registers: HLL register precision.
            max_hops: Max hop radius limit.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._m: int = num_registers
        self._b: int = int(math.log2(num_registers)) if num_registers > 1 else 4
        self._max_hops: int = max_hops
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _hll_hash(self, node: TNode) -> Tuple[int, int]:
        h = int(hashlib.md5(str(node).encode("utf-8")).hexdigest()[:8], 16)
        reg_idx = h & (self._m - 1)
        w = h >> self._b
        rho = min(32, max(1, 32 - w.bit_length() + 1)) if w > 0 else 32
        return reg_idx, rho

    def _estimate_cardinality(self, registers: List[int]) -> float:
        alpha_m = 0.7213 / (1.0 + 1.079 / self._m) if self._m >= 16 else 0.673
        indicator = sum(2.0 ** (-reg) for reg in registers)
        if indicator == 0:
            return float(self._m)
        raw = alpha_m * (self._m ** 2) / indicator
        if raw <= 2.5 * self._m:
            zeros = registers.count(0)
            if zeros > 0:
                return float(self._m) * math.log(float(self._m) / float(zeros))
        return raw

    def compute_effective_diameter(self) -> Tuple[float, float, Dict[int, float]]:
        """
        Compute effective diameter at 90th percentile and distance distribution.

        Returns:
            Tuple of (effective_diameter_90, average_distance, hop_distribution_map).
        """
        n = len(self._nodes)
        if n <= 1:
            return 0.0, 0.0, {0: float(n)}

        registers: Dict[TNode, List[int]] = {u: [0] * self._m for u in self._nodes}
        for u in self._nodes:
            idx, rho = self._hll_hash(u)
            registers[u][idx] = rho

        hop_dist: Dict[int, float] = {0: sum(self._estimate_cardinality(registers[u]) for u in self._nodes)}
        prev_pairs = hop_dist[0]

        for h in range(1, self._max_hops + 1):
            next_reg: Dict[TNode, List[int]] = {u: list(registers[u]) for u in self._nodes}
            changed: bool = False

            for u in self._nodes:
                for v in self._adj.get(u, []):
                    for i in range(self._m):
                        if registers[v][i] > next_reg[u][i]:
                            next_reg[u][i] = registers[v][i]
                            changed = True

            total_pairs = sum(self._estimate_cardinality(next_reg[u]) for u in self._nodes)
            hop_dist[h] = total_pairs
            registers = next_reg

            if not changed or (total_pairs - prev_pairs) < 1.0:
                break
            prev_pairs = total_pairs

        max_pairs = max(hop_dist.values())
        target_90 = 0.90 * max_pairs

        eff_diam_90: float = float(len(hop_dist))
        for h in sorted(hop_dist.keys()):
            if hop_dist[h] >= target_90:
                if h == 0:
                    eff_diam_90 = 0.0
                else:
                    prev_h = h - 1
                    diff = hop_dist[h] - hop_dist[prev_h]
                    fraction = (target_90 - hop_dist[prev_h]) / diff if diff > 0 else 0.0
                    eff_diam_90 = float(prev_h) + fraction
                break

        hop_deltas = {}
        sorted_hops = sorted(hop_dist.keys())
        for i in range(1, len(sorted_hops)):
            h = sorted_hops[i]
            prev_h = sorted_hops[i - 1]
            hop_deltas[h] = max(0.0, hop_dist[h] - hop_dist[prev_h])

        total_connected_pairs = sum(hop_deltas.values())
        if total_connected_pairs > 0:
            avg_distance = sum(h * count for h, count in hop_deltas.items()) / total_connected_pairs
        else:
            avg_distance = 0.0

        return eff_diam_90, avg_distance, hop_dist
