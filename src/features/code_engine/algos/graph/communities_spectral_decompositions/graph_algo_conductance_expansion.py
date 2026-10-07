"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Graph Conductance and Cheeger Cut Evaluator (ALGO-GRAPH-COMM-166)

1. OVERVIEW & OBJECTIVE:
Evaluates cluster cut quality, Cheeger conductance phi(S), expansion, and boundary volume
ratios for arbitrary vertex subsets S subset V in unweighted and weighted graphs, enabling
principled bottleneck detection and graph expansion benchmarking.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for node sets and degree lookups.
- Time Complexity: O(|E_S|) where E_S is the edge count incident to the cut set S.
- Invariants:
  - Conductance phi(S) = cut(S, V \\ S) / min(vol(S), vol(V \\ S)) in [0, 1].
  - vol(S) is the sum of degrees of vertices in S.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Adjacency structure.
- `subset` (Iterable[TNode]): Subgraph node selection S.
- `weights` (Optional[Mapping[Tuple[TNode, TNode], float]]): Optional edge weights.

4. OUTPUT PARAMETERS:
- `ConductanceProfile`: Object containing conductance, cut weight, volume(S), volume(V \ S), and expansion.

5. AGENT CONTRACT:
- Role: Graph cut quality and bottleneck diagnostics analyst.
- Rules: Conductance must return 0.0 for disconnected/trivial components and 1.0 for completely disconnected halves.
- Guardrails: If vol(S) == 0 or vol(V \ S) == 0, conductance is defined as 0.0.
"""

from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class ConductanceProfile:
    """
    Profile metrics for a set cut S vs V \\ S.
    """
    conductance: float
    expansion: float
    cut_weight: float
    volume_s: float
    volume_complement: float
    size_s: int
    size_complement: int


class ConductanceEvaluator(Generic[TNode]):
    """
    Computes Cheeger cut conductance and expansion metrics.

    ```yaml
    contract_id: ALGO-GRAPH-COMM-166
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      subset: Iterable[TNode]
      weights: Optional[Mapping[Tuple[TNode, TNode], float]]
    outputs:
      profile: ConductanceProfile
    parameters: {}
    capability_tags:
      - graph
      - conductance
      - cheeger_cut
      - expansion
      - spectral
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|E|)
      space: O(|V| + |E|)
    ```
    """

    def evaluate(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        subset: Iterable[TNode],
        weights: Optional[Mapping[Tuple[TNode, TNode], float]] = None,
    ) -> ConductanceProfile:
        """
        Evaluates conductance and expansion for a subset of vertices S.

        Args:
            adjacency: Graph adjacency map.
            subset: Selected vertex subset S.
            weights: Optional edge weight mapping.

        Returns:
            ConductanceProfile with conductance, expansion, cut size, and volumes.
        """
        all_nodes: Set[TNode] = set(adjacency.keys())
        s_nodes: Set[TNode] = set(subset).intersection(all_nodes)
        comp_nodes: Set[TNode] = all_nodes - s_nodes

        if not s_nodes or not comp_nodes:
            return ConductanceProfile(
                conductance=0.0,
                expansion=0.0,
                cut_weight=0.0,
                volume_s=0.0,
                volume_complement=0.0,
                size_s=len(s_nodes),
                size_complement=len(comp_nodes),
            )

        cut_weight = 0.0
        vol_s = 0.0
        vol_comp = 0.0

        for u in all_nodes:
            for v in adjacency.get(u, ()):
                w = weights.get((u, v), weights.get((v, u), 1.0)) if weights else 1.0
                if u in s_nodes:
                    vol_s += w
                    if v in comp_nodes:
                        cut_weight += w
                else:
                    vol_comp += w

        min_vol = min(vol_s, vol_comp)
        conductance = (cut_weight / min_vol) if min_vol > 0.0 else 0.0
        min_size = min(len(s_nodes), len(comp_nodes))
        expansion = (cut_weight / min_size) if min_size > 0 else 0.0

        return ConductanceProfile(
            conductance=conductance,
            expansion=expansion,
            cut_weight=cut_weight,
            volume_s=vol_s,
            volume_complement=vol_comp,
            size_s=len(s_nodes),
            size_complement=len(comp_nodes),
        )
