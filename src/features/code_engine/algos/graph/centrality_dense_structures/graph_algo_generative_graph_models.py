"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GENERATIVE GRAPH MODELS (ALGO-GRAPH-MODEL-142)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standard synthetic graph generation suite providing 4 foundational topologies:
   - Erdős–Rényi G(n, p): Uniform independent edge generation.
   - Barabási–Albert: Preferential attachment generating scale-free power-law degrees.
   - Watts–Strogatz: Small-world ring lattice with beta-random rewiring.
   - R-MAT / Kronecker: Recursive 2x2 initiator matrix quadrant decomposition.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m) linear-time edge generation per model.
   - Space Complexity: O(V + E) generated graph.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - n: int - Number of vertices in generated synthetic graph.
   - model_type: str - One of 'erdos_renyi', 'barabasi_albert', 'watts_strogatz', 'rmat'.
   - p_or_m: float - Model specific parameter (p probability, m edges per step, or beta rewiring).
   - rng_seed: int - Deterministic random seed (default: 42).

4. OUTPUT PARAMETERS:
   - edges: List[Tuple[int, int]] - Generated synthetic edge list.
   - total_nodes: int - Total vertices generated.
   - total_edges: int - Total edges synthesized.

5. AGENT CONTRACT:
   - Role: Builder.
   - Preconditions: n >= 1.
   - Guardrails: Self-loops and duplicate edges are pruned from outputs.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGenerativeGraphModels:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-142
      name: GraphAlgoGenerativeGraphModels
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, erdos_renyi, barabasi_albert, watts_strogatz, rmat, synthetic_graphs]
      inputs:
        type: object
        required: [n, model_type]
        properties:
          n: {type: integer}
          model_type: {type: string}
          p_or_m: {type: number, default: 0.1}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [edges, total_nodes, total_edges]
        properties:
          edges: {type: array, items: {type: array, items: {type: integer}}}
          total_nodes: {type: integer}
          total_edges: {type: integer}
      parameters:
        model_type: {type: string}
        p_or_m: {type: number, default: 0.1}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        n: int,
        model_type: str = "erdos_renyi",
        p_or_m: float = 0.1,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Generative Graph Model factory.

        Args:
            n: Vertex count.
            model_type: Generation algorithm ('erdos_renyi', 'barabasi_albert', 'watts_strogatz', 'rmat').
            p_or_m: Parameter (p probability, attachment count m, or beta).
            rng_seed: Deterministic random seed.
        """
        self._n: int = n
        self._model: str = model_type.lower()
        self._param: float = p_or_m
        self._rng_seed: int = rng_seed

    def generate(self) -> Tuple[List[Tuple[int, int]], int, int]:
        """
        Generate synthetic graph edges according to specified model.

        Returns:
            Tuple of (edges_list, total_nodes, total_edges).
        """
        rng = random.Random(self._rng_seed)
        edges: Set[Tuple[int, int]] = set()

        if self._model == "erdos_renyi":
            p = self._param
            for u in range(self._n):
                for v in range(u + 1, self._n):
                    if rng.random() <= p:
                        edges.add((u, v))

        elif self._model == "barabasi_albert":
            m = max(1, int(self._param))
            m = min(m, self._n - 1)
            targets = list(range(m))
            repeated_nodes = list(targets)

            for u in range(m, self._n):
                selected = set()
                while len(selected) < m:
                    choice = rng.choice(repeated_nodes)
                    selected.add(choice)
                for v in selected:
                    edges.add((min(u, v), max(u, v)))
                    repeated_nodes.append(u)
                    repeated_nodes.append(v)

        elif self._model == "watts_strogatz":
            k = max(2, int(self._param * 2))
            beta = 0.2
            for u in range(self._n):
                for i in range(1, k // 2 + 1):
                    v = (u + i) % self._n
                    edges.add((min(u, v), max(u, v)))

            edge_list = list(edges)
            for u, v in edge_list:
                if rng.random() <= beta:
                    edges.remove((u, v))
                    w = rng.randint(0, self._n - 1)
                    while w == u or (min(u, w), max(u, w)) in edges:
                        w = rng.randint(0, self._n - 1)
                    edges.add((min(u, w), max(u, w)))

        elif self._model == "rmat":
            a, b, c, d = 0.45, 0.15, 0.15, 0.25
            total_m = max(1, int(self._param * self._n * 2))
            scale = max(1, (self._n - 1).bit_length())

            for _ in range(total_m):
                u, v = 0, 0
                for step in range(scale):
                    bit = 1 << (scale - 1 - step)
                    r = rng.random()
                    if r < a:
                        pass
                    elif r < a + b:
                        v += bit
                    elif r < a + b + c:
                        u += bit
                    else:
                        u += bit
                        v += bit
                u = u % self._n
                v = v % self._n
                if u != v:
                    edges.add((min(u, v), max(u, v)))

        res_edges = sorted(list(edges))
        return res_edges, self._n, len(res_edges)
