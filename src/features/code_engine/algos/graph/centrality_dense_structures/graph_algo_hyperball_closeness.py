"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HYPERBALL CLOSENESS & HARMONIC (ALGO-GRAPH-CENT-111)
================================================================================

1. OVERVIEW & OBJECTIVE:
   HyperBall closeness and harmonic centrality engine using HyperLogLog probabilistic
   neighborhood estimation. Propagates bounded-memory cardinality registers across
   graph rounds to estimate all-pairs distance distributions and harmonic centrality
   for large networks.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(diameter * (V + E) * registers) round-based bit propagation.
   - Space Complexity: O(V * registers) bit register matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - num_registers: int - HyperLogLog registers per vertex (default: 16).
   - max_rounds: int - Maximum BFS ball expansion diameter rounds (default: 20).

4. OUTPUT PARAMETERS:
   - harmonic_centrality: Dict[TNode, float] - Estimated harmonic centrality sum_v (1 / d(u, v)).
   - reachable_sizes: Dict[TNode, float] - Estimated total reachable component size per node.
   - rounds_executed: int - Total propagation iterations until stabilization.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Adjacency represents directed or undirected network.
   - Guardrails: Standard HyperLogLog alpha-m bias correction applied for cardinality calculation.
================================================================================
"""

import hashlib
import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHyperBallCloseness(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-111
      name: GraphAlgoHyperBallCloseness
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, closeness, harmonic, hyperball, hyperloglog]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_registers: {type: integer, default: 16}
          max_rounds: {type: integer, default: 20}
      outputs:
        type: object
        required: [harmonic_centrality, reachable_sizes, rounds_executed]
        properties:
          harmonic_centrality: {type: object}
          reachable_sizes: {type: object}
          rounds_executed: {type: integer}
      parameters:
        num_registers: {type: integer, default: 16}
        max_rounds: {type: integer, default: 20}
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
        max_rounds: int = 20,
    ) -> None:
        """
        Initialize the HyperBall closeness engine.

        Args:
            adjacency: Graph adjacency mapping.
            num_registers: Number of HLL registers (power of 2, e.g. 16, 32).
            max_rounds: Maximum hop expansion diameter rounds.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._m: int = num_registers
        self._b: int = int(math.log2(num_registers)) if num_registers > 1 else 4
        self._max_rounds: int = max_rounds
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
        leading_zeros = (w.bit_length() ^ 32) if w > 0 else 32
        rho = min(32, max(1, 32 - w.bit_length() + 1)) if w > 0 else 32
        return reg_idx, rho

    def _estimate_cardinality(self, registers: List[int]) -> float:
        alpha_m = 0.7213 / (1.0 + 1.079 / self._m) if self._m >= 16 else 0.673
        indicator = sum(2.0 ** (-reg) for reg in registers)
        if indicator == 0:
            return float(self._m)
        raw_est = alpha_m * (self._m ** 2) / indicator
        if raw_est <= 2.5 * self._m:
            zeros = registers.count(0)
            if zeros > 0:
                return float(self._m) * math.log(float(self._m) / float(zeros))
        return raw_est

    def compute_centrality(self) -> Tuple[Dict[TNode, float], Dict[TNode, float], int]:
        """
        Run HyperBall neighborhood counter propagation.

        Returns:
            Tuple of (harmonic_centrality_dict, reachable_sizes_dict, rounds_executed).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}, 0

        registers: Dict[TNode, List[int]] = {u: [0] * self._m for u in self._nodes}
        for u in self._nodes:
            idx, rho = self._hll_hash(u)
            registers[u][idx] = rho

        prev_sizes: Dict[TNode, float] = {u: self._estimate_cardinality(registers[u]) for u in self._nodes}
        harmonic: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
        rounds_executed: int = 0

        for r in range(1, self._max_rounds + 1):
            rounds_executed = r
            next_registers: Dict[TNode, List[int]] = {u: list(registers[u]) for u in self._nodes}
            changed: bool = False

            for u in self._nodes:
                for v in self._adj.get(u, []):
                    for idx in range(self._m):
                        if registers[v][idx] > next_registers[u][idx]:
                            next_registers[u][idx] = registers[v][idx]
                            changed = True

            current_sizes: Dict[TNode, float] = {}
            for u in self._nodes:
                c_size = self._estimate_cardinality(next_registers[u])
                current_sizes[u] = c_size
                delta = max(0.0, c_size - prev_sizes[u])
                harmonic[u] += delta / float(r)

            registers = next_registers
            prev_sizes = current_sizes

            if not changed:
                break

        return harmonic, prev_sizes, rounds_executed
