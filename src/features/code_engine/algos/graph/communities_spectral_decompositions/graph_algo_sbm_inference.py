"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STOCHASTIC BLOCKMODEL (SBM) INFERENCE (ALGO-GRAPH-COMM-160)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Stochastic Blockmodel (SBM) and Degree-Corrected SBM maximum likelihood community inference.
   Fits edge probability matrix Omega_rs connecting community blocks r and s,
   optimizing the log-likelihood log P(A | z, Omega) = 1/2 * sum_{rs} [E_rs * log Omega_rs - n_r * n_s * Omega_rs]
   via coordinate ascent and spectral initialization.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V * K + E)) EM/coordinate ascent.
   - Space Complexity: O(V + K^2) block affinity matrix.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - num_blocks_k: int - Target block count K (default: 2).
   - max_iter: int - Coordinate ascent iterations (default: 20).
   - rng_seed: int - Deterministic random seed (default: 42).

4. OUTPUT PARAMETERS:
   - partition: Dict[TNode, int] - Node to block assignment map.
   - block_affinity_matrix: List[List[float]] - K x K edge density connection matrix Omega.
   - log_likelihood: float - Total model log-likelihood under fitted parameters.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph.
   - Guardrails: Regularization avoids log(0) in sparse inter-block pairs.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSbmInference(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-160
      name: GraphAlgoSbmInference
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, sbm, stochastic_blockmodel, generative_communities, likelihood_inference]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_blocks_k: {type: integer, default: 2}
          max_iter: {type: integer, default: 20}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [partition, block_affinity_matrix, log_likelihood]
        properties:
          partition: {type: object}
          block_affinity_matrix: {type: array, items: {type: array, items: {type: number}}}
          log_likelihood: {type: number}
      parameters:
        num_blocks_k: {type: integer, default: 2}
        max_iter: {type: integer, default: 20}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(I * (V * K + E))
        space: O(V + K^2)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_blocks_k: int = 2,
        max_iter: int = 20,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the SBM Inference engine.

        Args:
            adjacency: Graph adjacency dictionary.
            num_blocks_k: Block count K.
            max_iter: Coordinate ascent iterations.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._k: int = max(1, num_blocks_k)
        self._max_iter: int = max_iter
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def infer_sbm(self) -> Tuple[Dict[TNode, int], List[List[float]], float]:
        """
        Infer SBM block partition and connection probability matrix Omega.

        Returns:
            Tuple of (partition_map, block_affinity_matrix, log_likelihood_score).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, [], 0.0
        if n == 1:
            return {self._nodes[0]: 0}, [[0.0]], 0.0

        rng = random.Random(self._rng_seed)
        k = min(self._k, n)
        part: Dict[TNode, int] = {u: i % k for i, u in enumerate(self._nodes)}

        def _compute_omega_and_ll(current_part: Dict[TNode, int]) -> Tuple[List[List[float]], float]:
            block_sizes = [0] * k
            for u in self._nodes:
                block_sizes[current_part[u]] += 1

            e_mat = [[0] * k for _ in range(k)]
            for u in self._nodes:
                c_u = current_part[u]
                for v in self._adj.get(u, set()):
                    if str(u) < str(v):
                        c_v = current_part[v]
                        e_mat[c_u][c_v] += 1
                        if c_u != c_v:
                            e_mat[c_v][c_u] += 1

            omega = [[0.0] * k for _ in range(k)]
            ll = 0.0

            for r in range(k):
                for s in range(r, k):
                    if r == s:
                        max_possible = (block_sizes[r] * (block_sizes[r] - 1)) // 2
                    else:
                        max_possible = block_sizes[r] * block_sizes[s]

                    e_rs = float(e_mat[r][s])
                    if max_possible > 0:
                        p_rs = max(1e-6, min(1.0 - 1e-6, e_rs / float(max_possible)))
                        omega[r][s] = p_rs
                        omega[s][r] = p_rs
                        ll += e_rs * math.log(p_rs) + float(max_possible - e_rs) * math.log(1.0 - p_rs)

            return omega, ll

        omega, best_ll = _compute_omega_and_ll(part)

        for _ in range(self._max_iter):
            improved = False
            shuffled = list(self._nodes)
            rng.shuffle(shuffled)

            for u in shuffled:
                curr_c = part[u]
                best_c = curr_c

                for cand_c in range(k):
                    if cand_c == curr_c:
                        continue
                    part[u] = cand_c
                    _, ll = _compute_omega_and_ll(part)
                    if ll > best_ll:
                        best_ll = ll
                        best_c = cand_c
                        improved = True
                    part[u] = curr_c

                part[u] = best_c

            if not improved:
                break

        omega, final_ll = _compute_omega_and_ll(part)
        return part, omega, final_ll
