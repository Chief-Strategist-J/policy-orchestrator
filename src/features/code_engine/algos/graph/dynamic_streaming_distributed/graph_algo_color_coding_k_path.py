"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: COLOR CODING SIMPLE K-PATH DETECTION (ALGO-GRAPH-ENUM-235)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Color Coding Simple k-Path Decision Engine (Alon, Yuster, Zwick).
   Determines with high probability whether a simple (self-avoiding) path of length
   k - 1 (containing k distinct vertices) exists in a graph in FPT time O(e^k * M).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(e^k * 2^k * M) parameterized by k.
   - Space Complexity: O(2^k * V) bitmask dynamic programming tables.
   - Purity: Stateful randomized decision solver, reproducible with seed.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Target graph adjacency.
   - `k` (int): Number of vertices in desired simple path.
   - `trials` (int): Number of independent random coloring repetitions (defaults to ceil(e^k)).
   - `seed` (Optional[int]): Random seed.

4. OUTPUT PARAMETERS:
   - `find_simple_k_path()` (Optional[List[TNode]]): Concrete k-vertex path if found, else None.
   - `has_simple_k_path()` (bool): Decision flag.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Zero false positives; no self-intersecting cycle vertices in returned path.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoColorCodingKPath(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENUM-235
      name: GraphAlgoColorCodingKPath
      version: 1.0.0
      category: graph_enumeration
      capability_tags: [graph, enumeration, color_coding, k_path, simple_paths, fpt]
      inputs:
        type: object
        required: [adjacency, k]
        properties:
          adjacency: {type: object}
          k: {type: integer, minimum: 2, maximum: 10}
          trials: {type: integer}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          has_path: {type: boolean}
          path: {type: array}
      parameters:
        k: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(e^k * 2^k * M)
        space: O(2^k * V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        k: int = 4,
        trials: Optional[int] = None,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize Color-Coding k-path detection engine.

        Args:
            adjacency: Adjacency map.
            k: Target vertex count in path.
            trials: Number of trials (defaults to ceil(e^k)).
            seed: PRNG seed.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._k: int = max(2, min(10, k))
        self._trials: int = trials if trials is not None else int(math.ceil(math.exp(self._k)))
        self._rng = random.Random(seed)
        self._nodes: List[TNode] = list(self._adj.keys())

    def find_simple_k_path(self) -> Optional[List[TNode]]:
        """
        Search for a simple path of length k-1 (k distinct vertices).

        Returns:
            List of vertices along simple path if found, None otherwise.
        """
        num_masks = 1 << self._k
        full_mask = (1 << self._k) - 1

        for _ in range(self._trials):
            colors = {u: self._rng.randint(0, self._k - 1) for u in self._nodes}
            dp: Dict[TNode, Dict[int, Optional[Tuple[TNode, int]]]] = {
                u: {1 << colors[u]: None} for u in self._nodes
            }

            for mask_size in range(1, self._k):
                for u in self._nodes:
                    for mask, parent in list(dp[u].items()):
                        if bin(mask).count("1") == mask_size:
                            for v in self._adj.get(u, []):
                                c_v = colors[v]
                                if not (mask & (1 << c_v)):
                                    new_mask = mask | (1 << c_v)
                                    if new_mask not in dp[v]:
                                        dp[v][new_mask] = (u, mask)

            for u in self._nodes:
                if full_mask in dp[u]:
                    path: List[TNode] = []
                    curr_node = u
                    curr_mask = full_mask
                    while curr_node is not None and curr_mask is not None:
                        path.append(curr_node)
                        info = dp[curr_node].get(curr_mask)
                        if info is None:
                            break
                        curr_node, curr_mask = info
                    path.reverse()
                    if len(path) == self._k:
                        return path

        return None

    def has_simple_k_path(self) -> bool:
        """
        Check existence of a simple k-path.

        Returns:
            Boolean existence flag.
        """
        return self.find_simple_k_path() is not None
