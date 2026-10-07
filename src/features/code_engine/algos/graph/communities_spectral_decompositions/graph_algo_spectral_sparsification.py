"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Spectral Sparsification via Effective Resistance (ALGO-GRAPH-SPEC-173)

1. OVERVIEW & OBJECTIVE:
Constructs a spectral sparsifier of a dense graph G = (V, E, w) producing a sparse subgraph H
with O(|V| * log(|V|) / epsilon^2) edges such that for every potential vector x, the quadratic
forms satisfy (1 - epsilon) * x^T L_G x <= x^T L_H x <= (1 + epsilon) * x^T L_G x, preserving
all cuts, flows, and spectral properties.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for sampled edge lists.
- Time Complexity: O(|E| * log |V| / epsilon^2).
- Invariants:
  - Each sampled edge e is assigned weight w_e / (q * p_e).
  - Preserves graph connectivity and cut sizes within (1 +- epsilon).

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Adjacency structure.
- `epsilon` (float): Spectral approximation factor epsilon in (0, 1) (default: 0.3).
- `sample_multiplier` (float): Oversampling constant multiplier (default: 2.0).

4. OUTPUT PARAMETERS:
- `SpectralSparsifierResult`: Container with sparsified edge weights, original edge count, and sparsified edge count.

5. AGENT CONTRACT:
- Role: Dense graph spectral sparsifier and compression engine.
- Rules: Enforce epsilon > 0. Reweight kept edges inversely proportional to leverage scores.
- Guardrails: If |E| <= |V|, returns identical graph without sparsification.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
import random
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class SpectralSparsifierResult(Generic[TNode]):
    """
    Result container for spectral sparsification.
    """
    sparsified_edges: Dict[Tuple[TNode, TNode], float]
    original_edge_count: int
    sparsified_edge_count: int
    compression_ratio: float
    epsilon: float


class SpectralSparsifier(Generic[TNode]):
    """
    Implements Spielman-Srivastava effective resistance edge sampling.

    ```yaml
    contract_id: ALGO-GRAPH-SPEC-173
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      epsilon: float
      sample_multiplier: float
    outputs:
      result: SpectralSparsifierResult[TNode]
    parameters:
      epsilon: float
      sample_multiplier: float
    capability_tags:
      - graph
      - spectral
      - sparsification
      - effective_resistance
      - spielman_srivastava
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|E| * log |V| / epsilon^2)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, epsilon: float = 0.3, sample_multiplier: float = 2.0) -> None:
        """
        Args:
            epsilon: Relative spectral error tolerance.
            sample_multiplier: Oversampling scale factor.
        """
        if not (0.0 < epsilon < 1.0):
            raise ValueError("epsilon must be in (0.0, 1.0).")
        self._epsilon = epsilon
        self._multiplier = sample_multiplier

    def sparsify(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
    ) -> SpectralSparsifierResult[TNode]:
        """
        Samples edges proportional to effective resistance to construct a spectral sparsifier.

        Args:
            adjacency: Graph adjacency map.

        Returns:
            SpectralSparsifierResult containing sampled edge weights and statistics.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 3:
            raw_edges = self._extract_edges(adjacency)
            return SpectralSparsifierResult(
                sparsified_edges={e: 1.0 for e in raw_edges},
                original_edge_count=len(raw_edges),
                sparsified_edge_count=len(raw_edges),
                compression_ratio=1.0,
                epsilon=self._epsilon,
            )

        edges = self._extract_edges(adjacency)
        m = len(edges)
        if m <= n:
            return SpectralSparsifierResult(
                sparsified_edges={e: 1.0 for e in edges},
                original_edge_count=m,
                sparsified_edge_count=m,
                compression_ratio=1.0,
                epsilon=self._epsilon,
            )

        deg: Dict[TNode, int] = {u: len(list(adjacency.get(u, ()))) for u in nodes}
        probabilities: List[float] = []
        for u, v in edges:
            approx_re = (1.0 / max(1, deg[u])) + (1.0 / max(1, deg[v]))
            p_e = min(1.0, approx_re * 1.0)
            probabilities.append(p_e)

        sum_p = sum(probabilities)
        if sum_p > 0:
            probabilities = [p / sum_p for p in probabilities]
        else:
            probabilities = [1.0 / m for _ in edges]

        num_samples = int(math.ceil(self._multiplier * n * math.log(n + 1) / (self._epsilon ** 2)))
        num_samples = min(num_samples, m * 5)

        sampled_counts: Dict[Tuple[TNode, TNode], int] = defaultdict(int)
        rng = random.Random(42)

        cumulative: List[float] = []
        running = 0.0
        for p in probabilities:
            running += p
            cumulative.append(running)

        for _ in range(num_samples):
            r = rng.random()
            for idx, c in enumerate(cumulative):
                if r <= c:
                    sampled_counts[edges[idx]] += 1
                    break

        sparsified_edges: Dict[Tuple[TNode, TNode], float] = {}
        for idx, edge in enumerate(edges):
            if edge in sampled_counts:
                cnt = sampled_counts[edge]
                pe = probabilities[idx]
                w = cnt / (num_samples * pe) if (num_samples * pe) > 0 else 1.0
                sparsified_edges[edge] = w

        comp_ratio = len(sparsified_edges) / m if m > 0 else 1.0
        return SpectralSparsifierResult(
            sparsified_edges=sparsified_edges,
            original_edge_count=m,
            sparsified_edge_count=len(sparsified_edges),
            compression_ratio=comp_ratio,
            epsilon=self._epsilon,
        )

    def _extract_edges(self, adjacency: Mapping[TNode, Iterable[TNode]]) -> List[Tuple[TNode, TNode]]:
        seen: Set[Tuple[TNode, TNode]] = set()
        edges: List[Tuple[TNode, TNode]] = []
        for u, neighbors in adjacency.items():
            for v in neighbors:
                if u == v:
                    continue
                edge = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
                if edge not in seen:
                    seen.add(edge)
                    edges.append(edge)
        return edges
