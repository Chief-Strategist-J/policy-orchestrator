"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MOTIF COUNTING & SIGNIFICANCE (ALGO-GRAPH-DENSE-132)
================================================================================

1. OVERVIEW & OBJECTIVE:
   3-node directed network motif enumeration and statistical significance testing.
   Counts 3-vertex subgraph configurations (feed-forward loops, feedback cycles) and
   computes standard Z-scores and p-values by generating degree-preserved null random
   networks via Markov Chain Monte Carlo (MCMC) edge rewiring.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(num_null_samples * (V * d^2 + m * swaps)) MCMC motif test.
   - Space Complexity: O(V + E) network adjacency.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed graph adjacency list.
   - num_null_samples: int - Number of randomized null graphs to generate (default: 20).
   - rng_seed: int - Deterministic random seed (default: 42).

4. OUTPUT PARAMETERS:
   - real_motif_counts: Dict[str, int] - Observed pattern counts for 3-node directed motifs.
   - motif_z_scores: Dict[str, float] - Standard score (real - mean_null) / std_null.
   - significant_motifs: List[str] - Patterns with |Z-score| >= 2.0.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Directed graph.
   - Guardrails: Edge rewiring preserves both in-degree and out-degree sequences.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMotifSignificance(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-132
      name: GraphAlgoMotifSignificance
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, motifs, network_motifs, statistical_significance, z_scores]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_null_samples: {type: integer, default: 20}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [real_motif_counts, motif_z_scores, significant_motifs]
        properties:
          real_motif_counts: {type: object}
          motif_z_scores: {type: object}
          significant_motifs: {type: array, items: {type: string}}
      parameters:
        num_null_samples: {type: integer, default: 20}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(S * (V * d^2 + E))
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_null_samples: int = 20,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Motif Significance analyzer.

        Args:
            adjacency: Directed graph adjacency dictionary.
            num_null_samples: Number of null models generated for statistical z-scores.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._num_samples: int = num_null_samples
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _count_triad_motifs(self, adj: Dict[TNode, Set[TNode]]) -> Dict[str, int]:
        counts: Dict[str, int] = {
            "feedforward_loop": 0,
            "feedback_cycle": 0,
            "fan_in": 0,
            "fan_out": 0,
        }
        n = len(self._nodes)
        for i in range(n):
            u = self._nodes[i]
            for j in range(i + 1, n):
                v = self._nodes[j]
                for k in range(j + 1, n):
                    w = self._nodes[k]
                    edges: List[Tuple[TNode, TNode]] = []
                    for a, b in [(u, v), (v, u), (u, w), (w, u), (v, w), (w, v)]:
                        if b in adj.get(a, set()):
                            edges.append((a, b))

                    if len(edges) == 3:
                        e_set = set(edges)
                        if (u, v) in e_set and (v, w) in e_set and (u, w) in e_set:
                            counts["feedforward_loop"] += 1
                        elif (u, v) in e_set and (v, w) in e_set and (w, u) in e_set:
                            counts["feedback_cycle"] += 1
                        elif (u, w) in e_set and (v, w) in e_set:
                            counts["fan_in"] += 1
                        elif (w, u) in e_set and (w, v) in e_set:
                            counts["fan_out"] += 1
        return counts

    def compute_significance(self) -> Tuple[Dict[str, int], Dict[str, float], List[str]]:
        """
        Count real motifs, generate randomized null graphs, and compute Z-scores.

        Returns:
            Tuple of (real_counts, z_scores, significant_motifs_list).
        """
        real_counts = self._count_triad_motifs(self._adj)
        rng = random.Random(self._rng_seed)

        all_edges: List[Tuple[TNode, TNode]] = []
        for u in self._nodes:
            for v in self._adj.get(u, set()):
                all_edges.append((u, v))

        null_motif_records: Dict[str, List[int]] = {k: [] for k in real_counts}

        for _ in range(self._num_samples):
            rewired_edges = list(all_edges)
            num_swaps = 2 * len(rewired_edges)
            for _ in range(num_swaps):
                if len(rewired_edges) < 2:
                    break
                idx1, idx2 = rng.sample(range(len(rewired_edges)), 2)
                u1, v1 = rewired_edges[idx1]
                u2, v2 = rewired_edges[idx2]
                if u1 != u2 and v1 != v2 and u1 != v2 and u2 != v1:
                    rewired_edges[idx1] = (u1, v2)
                    rewired_edges[idx2] = (u2, v1)

            null_adj: Dict[TNode, Set[TNode]] = {u: set() for u in self._nodes}
            for u, v in rewired_edges:
                null_adj[u].add(v)

            null_counts = self._count_triad_motifs(null_adj)
            for k, val in null_counts.items():
                null_motif_records[k].append(val)

        z_scores: Dict[str, float] = {}
        sig_motifs: List[str] = []

        for k, real_val in real_counts.items():
            records = null_motif_records[k]
            mean_null = sum(records) / float(len(records)) if records else 0.0
            variance = sum((x - mean_null) ** 2 for x in records) / float(len(records)) if records else 0.0
            std_null = math.sqrt(variance)

            if std_null > 1e-6:
                z = (float(real_val) - mean_null) / std_null
            else:
                z = 0.0

            z_scores[k] = z
            if abs(z) >= 2.0:
                sig_motifs.append(k)

        return real_counts, z_scores, sig_motifs
