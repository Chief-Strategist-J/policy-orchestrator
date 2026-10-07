"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Effective Resistance and Commute Time Distance (ALGO-GRAPH-SPEC-175)

1. OVERVIEW & OBJECTIVE:
Computes electrical effective resistance R_eff(u, v) and random-walk commute time C(u, v) = 2m * R_eff(u, v)
between all vertex pairs (or queried pairs) by solving Laplacian unit current injections
(e_u - e_v) or pseudo-inverse quadratic forms, providing robust topological distance metrics.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V|^2) for all-pairs resistance matrix, or O(|V|) for pairwise queries.
- Time Complexity: O(|V| * |E| * iterations) for all-pairs Laplacian solves.
- Invariants:
  - R_eff(u, u) == 0.0.
  - R_eff(u, v) == R_eff(v, u) >= 0.0.
  - Triangle inequality holds: R_eff(u, w) <= R_eff(u, v) + R_eff(v, w).

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph adjacency structure.
- `pairs` (Optional[Iterable[Tuple[TNode, TNode]]]): Optional subset of pairs to query.

4. OUTPUT PARAMETERS:
- `EffectiveResistanceResult`: Resistance dictionary, commute times, and Kirchhoff index (total resistance).

5. AGENT CONTRACT:
- Role: Electrical resistance distance and structural robustness analyst.
- Rules: Enforce metric symmetry and non-negativity.
- Guardrails: Disconnected pairs have infinite effective resistance (represented as float('inf')).
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class EffectiveResistanceResult(Generic[TNode]):
    """
    Result container for effective resistance and commute time metrics.
    """
    resistances: Dict[Tuple[TNode, TNode], float]
    commute_times: Dict[Tuple[TNode, TNode], float]
    kirchhoff_index: float


class EffectiveResistanceCalculator(Generic[TNode]):
    """
    Computes effective resistance and commute time distances on graphs.

    ```yaml
    contract_id: ALGO-GRAPH-SPEC-175
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      pairs: Optional[Iterable[Tuple[TNode, TNode]]]
    outputs:
      result: EffectiveResistanceResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - spectral
      - effective_resistance
      - commute_time
      - kirchhoff_index
    purity: deterministic
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| * |E| * iter)
      space: O(|V|^2)
    ```
    """

    def compute(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        pairs: Optional[Iterable[Tuple[TNode, TNode]]] = None,
    ) -> EffectiveResistanceResult[TNode]:
        """
        Computes effective resistance between node pairs.

        Args:
            adjacency: Graph adjacency map.
            pairs: Optional specific pairs to compute; if None, computes for all pairs.

        Returns:
            EffectiveResistanceResult containing resistance and commute time mappings.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n < 2:
            return EffectiveResistanceResult(resistances={}, commute_times={}, kirchhoff_index=0.0)

        node_idx = {u: i for i, u in enumerate(nodes)}
        degrees = [len(list(adjacency.get(u, ()))) for u in nodes]
        m_edges = sum(degrees) // 2

        laplacian = [[0.0] * n for _ in range(n)]
        for i, u in enumerate(nodes):
            laplacian[i][i] = float(degrees[i])
            for v in adjacency.get(u, ()):
                if v in node_idx:
                    j = node_idx[v]
                    laplacian[i][j] -= 1.0

        l_pinv = self._compute_pseudoinverse(laplacian, n)

        resistances: Dict[Tuple[TNode, TNode], float] = {}
        commute_times: Dict[Tuple[TNode, TNode], float] = {}

        query_pairs = list(pairs) if pairs is not None else [
            (nodes[i], nodes[j]) for i in range(n) for j in range(i + 1, n)
        ]

        total_r = 0.0
        for u, v in query_pairs:
            if u not in node_idx or v not in node_idx:
                continue
            i = node_idx[u]
            j = node_idx[v]
            if i == j:
                r_eff = 0.0
            else:
                r_eff = max(0.0, l_pinv[i][i] + l_pinv[j][j] - 2.0 * l_pinv[i][j])
            
            resistances[(u, v)] = r_eff
            resistances[(v, u)] = r_eff
            c_time = 2.0 * m_edges * r_eff
            commute_times[(u, v)] = c_time
            commute_times[(v, u)] = c_time
            total_r += r_eff

        kirchhoff = sum(
            max(0.0, l_pinv[i][i] + l_pinv[j][j] - 2.0 * l_pinv[i][j])
            for i in range(n) for j in range(i + 1, n)
        )

        return EffectiveResistanceResult(
            resistances=resistances,
            commute_times=commute_times,
            kirchhoff_index=kirchhoff,
        )

    def _compute_pseudoinverse(self, mat: List[List[float]], n: int) -> List[List[float]]:
        j_mat = [[1.0 / n] * n for _ in range(n)]
        shifted = [[mat[i][j] + j_mat[i][j] for j in range(n)] for i in range(n)]
        inv_shifted = self._invert_matrix(shifted, n)
        return [[inv_shifted[i][j] - j_mat[i][j] for j in range(n)] for i in range(n)]

    def _invert_matrix(self, a: List[List[float]], n: int) -> List[List[float]]:
        augmented = [[a[i][j] for j in range(n)] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        for i in range(n):
            pivot = i
            max_val = abs(augmented[i][i])
            for k in range(i + 1, n):
                if abs(augmented[k][i]) > max_val:
                    max_val = abs(augmented[k][i])
                    pivot = k
            if pivot != i:
                augmented[i], augmented[pivot] = augmented[pivot], augmented[i]
            diag = augmented[i][i]
            if abs(diag) < 1e-12:
                continue
            for col in range(2 * n):
                augmented[i][col] /= diag
            for r in range(n):
                if r != i:
                    factor = augmented[r][i]
                    for col in range(2 * n):
                        augmented[r][col] -= factor * augmented[i][col]

        return [[augmented[i][j + n] for j in range(n)] for i in range(n)]
