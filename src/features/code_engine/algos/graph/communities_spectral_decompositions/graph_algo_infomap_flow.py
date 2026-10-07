"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: INFOMAP FLOW COMMUNITIES (ALGO-GRAPH-COMM-155)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Infomap information-theoretic community detection based on the Map Equation (Rosvall-Bergstrom).
   Minimizes the expected description length of a random walk trajectory using a two-level
   coding scheme: module transitions (inter-community flow) and vertex visits (intra-community flow).
   Optimizes L(M) = q_exit * H(Q) + sum_m p_circle_m * H(P_m).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * (V + E)) flow-based local movement.
   - Space Complexity: O(V + E) random walk stationary distribution.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed or undirected graph adjacency list.
   - max_iter: int - Optimization passes (default: 15).
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - partition: Dict[TNode, int] - Node to module assignment map.
   - code_length: float - Map equation codelength in bits.
   - num_modules: int - Count of discovered flow modules.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected graph for stationary random walk flow.
   - Guardrails: Shannon entropy H(P) evaluated with base-2 logarithm.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoInfomapFlow(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-155
      name: GraphAlgoInfomapFlow
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, infomap, map_equation, information_theory, random_walk_flow]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_iter: {type: integer, default: 15}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [partition, code_length, num_modules]
        properties:
          partition: {type: object}
          code_length: {type: number}
          num_modules: {type: integer}
      parameters:
        max_iter: {type: integer, default: 15}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(I * (V + E))
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        max_iter: int = 15,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Infomap flow optimizer.

        Args:
            adjacency: Graph adjacency dictionary.
            max_iter: Maximum optimization iterations.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._max_iter: int = max_iter
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _plogp(self, p: float) -> float:
        return p * math.log2(p) if p > 1e-12 else 0.0

    def detect_modules(self) -> Tuple[Dict[TNode, int], float, int]:
        """
        Optimize the Map Equation code length to identify flow modules.

        Returns:
            Tuple of (partition_map, code_length_bits, total_modules_count).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, 0.0, 0

        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        total_deg = sum(degrees.values())
        if total_deg == 0:
            return {u: 0 for u in self._nodes}, 0.0, 1

        p_node: Dict[TNode, float] = {u: float(degrees[u]) / float(total_deg) for u in self._nodes}

        rng = random.Random(self._rng_seed)
        part: Dict[TNode, int] = {u: i for i, u in enumerate(self._nodes)}

        def _calculate_codelength(current_part: Dict[TNode, int]) -> float:
            mod_nodes: Dict[int, List[TNode]] = {}
            for u, m in current_part.items():
                if m not in mod_nodes:
                    mod_nodes[m] = []
                mod_nodes[m].append(u)

            q_exit_total: float = 0.0
            q_exit_m: Dict[int, float] = {}

            for m, members in mod_nodes.items():
                m_set = set(members)
                exit_flow = 0.0
                for u in members:
                    for v in self._adj.get(u, set()):
                        if v not in m_set:
                            exit_flow += (p_node[u] / float(degrees[u])) if degrees[u] > 0 else 0.0
                q_exit_m[m] = exit_flow
                q_exit_total += exit_flow

            if q_exit_total <= 0:
                return 0.0

            h_q: float = 0.0
            for m in mod_nodes:
                p_exit = q_exit_m[m] / q_exit_total if q_exit_total > 0 else 0.0
                h_q -= self._plogp(p_exit)

            index_term = q_exit_total * h_q
            module_term = 0.0

            for m, members in mod_nodes.items():
                p_circle_m = q_exit_m[m] + sum(p_node[u] for u in members)
                if p_circle_m > 0:
                    h_p = -self._plogp(q_exit_m[m] / p_circle_m)
                    for u in members:
                        h_p -= self._plogp(p_node[u] / p_circle_m)
                    module_term += p_circle_m * h_p

            return index_term + module_term

        best_codelength = _calculate_codelength(part)

        for _ in range(self._max_iter):
            improved = False
            shuffled = list(self._nodes)
            rng.shuffle(shuffled)

            for u in shuffled:
                curr_m = part[u]
                candidate_modules = {part[v] for v in self._adj.get(u, set())}
                candidate_modules.add(curr_m)

                best_m = curr_m
                for cand_m in candidate_modules:
                    if cand_m == curr_m:
                        continue
                    part[u] = cand_m
                    cl = _calculate_codelength(part)
                    if cl < best_codelength:
                        best_codelength = cl
                        best_m = cand_m
                        improved = True
                    part[u] = curr_m

                part[u] = best_m

            if not improved:
                break

        unique_m = sorted(list(set(part.values())))
        compact = {old: new for new, old in enumerate(unique_m)}
        final_part = {u: compact[part[u]] for u in self._nodes}

        return final_part, best_codelength, len(unique_m)
