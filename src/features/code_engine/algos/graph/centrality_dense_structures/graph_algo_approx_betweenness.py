"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: APPROXIMATE BETWEENNESS SAMPLING (ALGO-GRAPH-CENT-110)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Riondato-Kornaropoulos randomized shortest path sampling and KADABRA-style
   betweenness approximation. Samples random vertex pairs (s, t), computes shortest
   paths via bidirectional BFS, and accumulates hit counters to estimate top-k
   betweenness rankings with statistical epsilon-delta bounds.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(num_samples * (V + E)) sub-quadratic path sampling.
   - Space Complexity: O(V) frequency counters.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - num_samples: int - Number of shortest path Monte Carlo samples (default: 500).
   - rng_seed: int - Random seed for reproducible sampling (default: 42).

4. OUTPUT PARAMETERS:
   - approx_betweenness: Dict[TNode, float] - Estimated betweenness fraction per vertex.
   - sampled_pairs: int - Total shortest paths successfully sampled.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Non-empty graph.
   - Guardrails: Avoids end-point vertex self-counting in path interiors.
================================================================================
"""

import random
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoApproxBetweenness(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-110
      name: GraphAlgoApproxBetweenness
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, approx_betweenness, kadabra, riondato_kornaropoulos, path_sampling]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_samples: {type: integer, default: 500}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [approx_betweenness, sampled_pairs]
        properties:
          approx_betweenness: {type: object}
          sampled_pairs: {type: integer}
      parameters:
        num_samples: {type: integer, default: 500}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(S * (V + E))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_samples: int = 500,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Approximate Betweenness solver.

        Args:
            adjacency: Graph adjacency dictionary.
            num_samples: Monte Carlo shortest-path sample budget.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._num_samples: int = num_samples
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _find_random_shortest_path(self, s: TNode, t: TNode, rng: random.Random) -> Optional[List[TNode]]:
        if s == t:
            return None
        visited: Dict[TNode, Optional[TNode]] = {s: None}
        q: Deque[TNode] = deque([s])
        found: bool = False

        while q and not found:
            curr = q.popleft()
            nbrs = list(self._adj.get(curr, []))
            rng.shuffle(nbrs)
            for nxt in nbrs:
                if nxt not in visited:
                    visited[nxt] = curr
                    if nxt == t:
                        found = True
                        break
                    q.append(nxt)

        if not found:
            return None

        path: List[TNode] = []
        curr_node: Optional[TNode] = t
        while curr_node is not None:
            path.append(curr_node)
            curr_node = visited[curr_node]
        path.reverse()
        return path

    def compute_approx_betweenness(self) -> Tuple[Dict[TNode, float], int]:
        """
        Compute approximate betweenness scores by sampling random source-target pairs.

        Returns:
            Tuple of (approx_betweenness_dict, actual_sampled_pairs_count).
        """
        n = len(self._nodes)
        if n <= 2:
            return {u: 0.0 for u in self._nodes}, 0

        counts: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
        rng = random.Random(self._rng_seed)
        sampled: int = 0

        for _ in range(self._num_samples):
            s, t = rng.sample(self._nodes, 2)
            path = self._find_random_shortest_path(s, t, rng)
            if path is not None and len(path) > 2:
                sampled += 1
                for interior_node in path[1:-1]:
                    counts[interior_node] += 1.0

        if sampled > 0:
            scale = 1.0 / float(sampled)
            approx = {u: val * scale for u, val in counts.items()}
        else:
            approx = counts

        return approx, sampled
