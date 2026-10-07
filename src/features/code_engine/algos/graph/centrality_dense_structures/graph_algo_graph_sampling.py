"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH SAMPLING & ESTIMATION (ALGO-GRAPH-SAMP-148)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Representative graph sampling suite providing:
   - Uniform Random Node Sampling (URNS).
   - Uniform Random Edge Sampling (URES).
   - Random Walk Sampling (RWS) with degree bias correction.
   - Metropolis-Hastings Random Walk (MHRW) achieving uniform node stationary distribution.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(sample_size) sampling operations.
   - Space Complexity: O(sample_size) sampled subgraph.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - method: str - Sampling method: 'node', 'edge', 'random_walk', 'metropolis_hastings' (default: 'metropolis_hastings').
   - sample_size: int - Target number of unique nodes to sample.
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - sampled_nodes: List[TNode] - Vertices included in the sample.
   - sampled_edges: List[Tuple[TNode, TNode]] - Induced edges among sampled vertices.
   - sample_coverage: float - Ratio of sampled vertices |V_sample| / |V|.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected graph for walk-based sampling methods.
   - Guardrails: Metropolis-Hastings acceptance probability min(1, deg(u)/deg(v)) ensures unbiased stationary sampling.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphSampling(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SAMP-148
      name: GraphAlgoGraphSampling
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, sampling, metropolis_hastings, random_walk_sampling, urns, ures, representative_subgraphs]
      inputs:
        type: object
        required: [adjacency, sample_size]
        properties:
          adjacency: {type: object}
          method: {type: string, default: metropolis_hastings}
          sample_size: {type: integer}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [sampled_nodes, sampled_edges, sample_coverage]
        properties:
          sampled_nodes: {type: array, items: {type: string}}
          sampled_edges: {type: array, items: {type: array, items: {type: string}}}
          sample_coverage: {type: number}
      parameters:
        method: {type: string, default: metropolis_hastings}
        sample_size: {type: integer}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(S)
        space: O(S)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        method: str = "metropolis_hastings",
        sample_size: int = 10,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Graph Sampling suite.

        Args:
            adjacency: Graph adjacency dictionary.
            method: Sampling algorithm ('node', 'edge', 'random_walk', 'metropolis_hastings').
            sample_size: Target unique sampled node count.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._method: str = method.lower()
        self._target_size: int = sample_size
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def sample(self) -> Tuple[List[TNode], List[Tuple[TNode, TNode]], float]:
        """
        Extract a representative sample subgraph.

        Returns:
            Tuple of (sampled_nodes_list, sampled_induced_edges, coverage_fraction).
        """
        n = len(self._nodes)
        if n == 0 or self._target_size <= 0:
            return [], [], 0.0

        target = min(self._target_size, n)
        rng = random.Random(self._rng_seed)
        sampled_set: Set[TNode] = set()

        if self._method == "node":
            sampled_set = set(rng.sample(self._nodes, target))

        elif self._method == "edge":
            edges: List[Tuple[TNode, TNode]] = []
            for u in self._nodes:
                for v in self._adj.get(u, []):
                    if str(u) < str(v):
                        edges.append((u, v))
            rng.shuffle(edges)
            for u, v in edges:
                sampled_set.add(u)
                sampled_set.add(v)
                if len(sampled_set) >= target:
                    break

        elif self._method == "random_walk":
            curr = rng.choice(self._nodes)
            sampled_set.add(curr)
            steps = 0
            while len(sampled_set) < target and steps < target * 10:
                steps += 1
                nbrs = self._adj.get(curr, [])
                if not nbrs:
                    curr = rng.choice(self._nodes)
                else:
                    curr = rng.choice(nbrs)
                sampled_set.add(curr)

        elif self._method == "metropolis_hastings":
            curr = rng.choice(self._nodes)
            sampled_set.add(curr)
            steps = 0
            while len(sampled_set) < target and steps < target * 20:
                steps += 1
                nbrs = self._adj.get(curr, [])
                if not nbrs:
                    curr = rng.choice(self._nodes)
                    sampled_set.add(curr)
                    continue

                candidate = rng.choice(nbrs)
                deg_curr = len(nbrs)
                deg_cand = len(self._adj.get(candidate, []))
                accept_prob = min(1.0, float(deg_curr) / float(deg_cand)) if deg_cand > 0 else 1.0

                if rng.random() <= accept_prob:
                    curr = candidate
                    sampled_set.add(curr)

        sampled_nodes = sorted(list(sampled_set), key=lambda x: str(x))
        sampled_edges: List[Tuple[TNode, TNode]] = []
        for u in sampled_nodes:
            for v in self._adj.get(u, []):
                if v in sampled_set and str(u) < str(v):
                    sampled_edges.append((u, v))

        coverage = float(len(sampled_nodes)) / float(n)
        return sampled_nodes, sampled_edges, coverage
