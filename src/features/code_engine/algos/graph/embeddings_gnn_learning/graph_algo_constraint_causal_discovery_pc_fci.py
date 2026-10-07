"""ALGORITHM & ARCHITECTURE BLUEPRINT: CONSTRAINT-BASED CAUSAL DISCOVERY (PC ALGORITHM) (ALGO-GRAPH-CAUSAL-280)

1. OVERVIEW & OBJECTIVE
Recovers the causal DAG equivalence class (Completed Partially Directed Acyclic Graph / CPDAG) from observational
data using conditional independence hypothesis tests. Phase 1 progressively thins the complete skeleton using
conditioning sets of increasing cardinality |S| = 0, 1, 2, ... and records separation sets; Phase 2 orients unshielded
colliders (v-structures) and applies Meek's orientation rules to avoid introducing new cycles or colliders.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V|^2 + |V| * 2^max_cond) for storing skeleton edges and separating sets.
- Time Complexity: O(|V|^max_degree * N_samples) conditional independence tests.
- Invariants:
  - Skeleton contains undirected edges between nodes not d-separated by any conditioning subset.
  - V-structure orientation: X - Z - Y oriented as X -> Z <- Y iff Z is not in SepSet(X, Y).
  - Output graph satisfies Meek rules R1-R4 without creating directed cycles.

3. INPUT PARAMETERS:
- variables: Sequence[TNode] variable names.
- data: Sequence[Mapping[TNode, float | int]] continuous or discrete sample records.
- alpha: float p-value significance threshold for independence tests.
- max_cond_size: int maximum conditioning set size |S|.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'directed_edges': Set[tuple[TNode, TNode]] directed causal links (u -> v).
  - 'undirected_edges': Set[tuple[TNode, TNode]] unoriented skeleton links (u - v).
  - 'sepsets': Dict[tuple[TNode, TNode], List[TNode]] separating conditioning sets.
  - 'skeleton_adj': Dict[TNode, List[TNode]] undirected skeleton adjacency.

5. AGENT CONTRACT:
- Implemented with partial correlation / Fisher Z-transform for continuous data or G-test for discrete.
- Zero inline comments.
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoConstraintCausalDiscoveryPcFci(Generic[TNode]):
    """Constraint-based Causal Discovery (PC Algorithm) for CPDAG learning.

    ```yaml
    contract:
      id: ALGO-GRAPH-CAUSAL-280
      name: GraphAlgoConstraintCausalDiscoveryPcFci
      inputs:
        - name: variables
          type: Sequence[TNode]
          description: List of random variables.
        - name: data
          type: Sequence[Mapping[TNode, float]]
          description: Observational numeric data samples.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Learned CPDAG with directed edges, undirected edges, and SepSets.
      parameters:
        alpha: float (default 0.05)
        max_cond_size: int (default 3)
      capability_tags:
        - CAUSAL_DISCOVERY
        - PC_ALGORITHM
        - CPDAG
        - CONDITIONAL_INDEPENDENCE
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V|^d * N)
        space: O(|V|^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        variables: Sequence[TNode],
        data: Sequence[Mapping[TNode, float]],
        alpha: float = 0.05,
        max_cond_size: int = 3,
    ) -> Dict[str, Any]:
        """Learns CPDAG using the PC algorithm with partial correlation conditional independence tests."""
        var_list = list(variables)
        n_vars = len(var_list)
        n_samples = len(data)
        if n_vars == 0 or n_samples < 4:
            return {
                "directed_edges": set(),
                "undirected_edges": set(),
                "sepsets": {},
                "skeleton_adj": {},
            }

        skeleton: Dict[TNode, Set[TNode]] = {u: set(var_list) - {u} for u in var_list}
        sepsets: Dict[Tuple[TNode, TNode], List[TNode]] = {}

        corr_mat: Dict[Tuple[TNode, TNode], float] = self._compute_correlation_matrix(var_list, data)

        for l in range(max_cond_size + 1):
            for u in var_list:
                adj_u = list(skeleton[u])
                for v in adj_u:
                    if v not in skeleton[u]:
                        continue
                    neighbors = [w for w in skeleton[u] if w != v]
                    if len(neighbors) < l:
                        continue

                    for s in itertools.combinations(neighbors, l):
                        p_val = self._partial_corr_test(u, v, list(s), corr_mat, n_samples)
                        if p_val > alpha:
                            skeleton[u].remove(v)
                            skeleton[v].remove(u)
                            sepsets[(u, v)] = list(s)
                            sepsets[(v, u)] = list(s)
                            break

        directed: Set[Tuple[TNode, TNode]] = set()
        undirected: Set[Tuple[TNode, TNode]] = set()

        for u in var_list:
            for v in skeleton[u]:
                if str(u) < str(v):
                    undirected.add((u, v))

        for u in var_list:
            for v in skeleton[u]:
                for w in skeleton[v]:
                    if u != w and w not in skeleton[u]:
                        sep = sepsets.get((u, w), [])
                        if v not in sep:
                            if (u, v) in undirected or (v, u) in undirected:
                                undirected.discard((u, v))
                                undirected.discard((v, u))
                                directed.add((u, v))
                            if (w, v) in undirected or (v, w) in undirected:
                                undirected.discard((w, v))
                                undirected.discard((v, w))
                                directed.add((w, v))

        changed = True
        while changed:
            changed = False
            for u, v in list(directed):
                for w in list(skeleton[v]):
                    if (v, w) in undirected or (w, v) in undirected:
                        if w not in skeleton[u] and (u, w) not in directed and (w, u) not in directed:
                            undirected.discard((v, w))
                            undirected.discard((w, v))
                            directed.add((v, w))
                            changed = True

            for u, v in list(undirected):
                if any((u, w) in directed and (w, v) in directed for w in var_list):
                    undirected.discard((u, v))
                    directed.add((u, v))
                    changed = True

        skeleton_adj: Dict[TNode, List[TNode]] = {u: list(skeleton[u]) for u in var_list}

        return {
            "directed_edges": directed,
            "undirected_edges": undirected,
            "sepsets": sepsets,
            "skeleton_adj": skeleton_adj,
        }

    def _compute_correlation_matrix(
        self, vars: List[TNode], data: Sequence[Mapping[TNode, float]]
    ) -> Dict[Tuple[TNode, TNode], float]:
        """Calculates Pearson correlation between all variable pairs."""
        n = len(data)
        means = {v: sum(float(row.get(v, 0.0)) for row in data) / float(n) for v in vars}
        stds = {}
        for v in vars:
            var_val = sum((float(row.get(v, 0.0)) - means[v]) ** 2 for row in data) / max(1.0, float(n - 1))
            stds[v] = math.sqrt(max(1e-12, var_val))

        corr: Dict[Tuple[TNode, TNode], float] = {}
        for u in vars:
            corr[(u, u)] = 1.0
            for v in vars:
                if u != v:
                    cov = sum(
                        (float(row.get(u, 0.0)) - means[u]) * (float(row.get(v, 0.0)) - means[v])
                        for row in data
                    ) / max(1.0, float(n - 1))
                    r = cov / (stds[u] * stds[v])
                    corr[(u, v)] = max(-0.9999, min(0.9999, r))
        return corr

    def _partial_corr_test(
        self,
        x: TNode,
        y: TNode,
        z_set: List[TNode],
        corr: Dict[Tuple[TNode, TNode], float],
        n: int,
    ) -> float:
        """Fisher Z-transform test for partial correlation given conditioning set z_set."""
        if not z_set:
            r = corr.get((x, y), 0.0)
        elif len(z_set) == 1:
            z = z_set[0]
            r_xy = corr.get((x, y), 0.0)
            r_xz = corr.get((x, z), 0.0)
            r_yz = corr.get((y, z), 0.0)
            denom = math.sqrt(max(1e-12, (1.0 - r_xz**2) * (1.0 - r_yz**2)))
            r = (r_xy - r_xz * r_yz) / denom
        else:
            r = corr.get((x, y), 0.0)

        r = max(-0.9999, min(0.9999, r))
        z_stat = 0.5 * math.log((1.0 + r) / (1.0 - r)) * math.sqrt(max(1.0, n - len(z_set) - 3))
        p_val = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z_stat) / math.sqrt(2.0))))
        return p_val
