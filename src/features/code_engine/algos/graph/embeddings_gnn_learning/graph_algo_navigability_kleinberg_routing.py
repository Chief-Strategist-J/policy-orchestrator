"""ALGORITHM & ARCHITECTURE BLUEPRINT: NAVIGABILITY & GREEDY SMALL-WORLD ROUTING (KLEINBERG) (ALGO-GRAPH-NAV-296)

1. OVERVIEW & OBJECTIVE
Simulates and evaluates navigability and decentralized greedy routing in Kleinberg small-world networks.
Nodes on a d-dimensional grid (e.g. 2D mesh) have local lattice connections plus long-range shortcuts added
with probability P(u -> v) proportional to d_{grid}(u, v)^{-r}. Demonstrates that decentralized greedy routing
(where each vertex forwards the message to whichever neighbor is closest to the target in grid distance)
achieves polylogarithmic O(log^2 N) delivery time if and only if clustering exponent r = d.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(N * (deg_local + q_shortcuts)) grid graph representation.
- Time Complexity: O(N_hops * deg_avg) per message routing path simulation.
- Invariants:
  - Local routing decision is strictly myopic (uses only neighbor coordinates, zero global routing tables).
  - Termination occurs when message reaches destination or enters a local minimum dead-end.

3. INPUT PARAMETERS:
- grid_size: int N x N lattice dimension (total nodes |V| = N^2).
- clustering_exponent_r: float long-range shortcut distance decay parameter r.
- num_shortcuts: int number of long-range links added per node.
- source_coord: tuple[int, int] starting lattice node (r1, c1).
- target_coord: tuple[int, int] destination lattice node (r2, c2).

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'path': List[tuple[int, int]] sequential route taken by greedy decentralized forwarding.
  - 'hop_count': int total routing steps.
  - 'reached_target': bool success flag.
  - 'manhattan_distances': List[int] remaining distance to target at each step.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Deterministic simulation with RNG seed.
"""

from __future__ import annotations

import math
import random
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoNavigabilityKleinbergRouting(Generic[TNode]):
    """Kleinberg small-world model generation and decentralized greedy routing simulator.

    ```yaml
    contract:
      id: ALGO-GRAPH-NAV-296
      name: GraphAlgoNavigabilityKleinbergRouting
      inputs:
        - name: grid_size
          type: int
          default: 20
          description: N x N 2D grid dimension.
        - name: clustering_exponent_r
          type: float
          default: 2.0
          description: Distance decay exponent r (optimal navigability at r=2 for 2D).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Routing trajectory, hop count, success status, and distance trace.
      parameters:
        num_shortcuts: int (default 1)
        source_coord: Optional[tuple[int, int]] (default None)
        target_coord: Optional[tuple[int, int]] (default None)
        seed: int (default 42)
      capability_tags:
        - SMALL_WORLD
        - KLEINBERG_ROUTING
        - NAVIGABILITY
        - DECENTRALIZED_SEARCH
      purity: DETERMINISTIC_WITH_SEED
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(N_hops * deg)
        space: O(N^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        grid_size: int = 20,
        clustering_exponent_r: float = 2.0,
        num_shortcuts: int = 1,
        source_coord: Optional[Tuple[int, int]] = None,
        target_coord: Optional[Tuple[int, int]] = None,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Generates Kleinberg network and executes decentralized greedy routing."""
        rng = random.Random(seed)
        n = grid_size
        src = source_coord if source_coord is not None else (0, 0)
        dst = target_coord if target_coord is not None else (n - 1, n - 1)

        adj: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        for r in range(n):
            for c in range(n):
                local_nbrs: List[Tuple[int, int]] = []
                if r > 0:
                    local_nbrs.append((r - 1, c))
                if r < n - 1:
                    local_nbrs.append((r + 1, c))
                if c > 0:
                    local_nbrs.append((r, c - 1))
                if c < n - 1:
                    local_nbrs.append((r, c + 1))

                candidates = []
                weights = []
                for rr in range(n):
                    for cc in range(n):
                        if (rr, cc) != (r, c) and (rr, cc) not in local_nbrs:
                            d = abs(r - rr) + abs(c - cc)
                            w = 1.0 / math.pow(float(d), clustering_exponent_r)
                            candidates.append((rr, cc))
                            weights.append(w)

                shortcuts: List[Tuple[int, int]] = []
                if candidates and num_shortcuts > 0:
                    tot_w = sum(weights)
                    probs = [w / tot_w for w in weights]
                    for _ in range(num_shortcuts):
                        r_sample = rng.random()
                        acc = 0.0
                        pick = candidates[-1]
                        for cand, p in zip(candidates, probs):
                            acc += p
                            if r_sample <= acc:
                                pick = cand
                                break
                        shortcuts.append(pick)

                adj[(r, c)] = local_nbrs + shortcuts

        curr = src
        path: List[Tuple[int, int]] = [curr]
        distances: List[int] = [abs(curr[0] - dst[0]) + abs(curr[1] - dst[1])]
        visited: Set[Tuple[int, int]] = {curr}

        max_hops = n * n
        reached = False

        while curr != dst and len(path) < max_hops:
            nbrs = adj.get(curr, [])
            best_nbr = None
            best_d = abs(curr[0] - dst[0]) + abs(curr[1] - dst[1])

            for nbr in nbrs:
                d_nbr = abs(nbr[0] - dst[0]) + abs(nbr[1] - dst[1])
                if d_nbr < best_d:
                    best_d = d_nbr
                    best_nbr = nbr

            if best_nbr is None or best_nbr in visited:
                break

            curr = best_nbr
            path.append(curr)
            visited.add(curr)
            distances.append(best_d)
            if curr == dst:
                reached = True
                break

        return {
            "path": path,
            "hop_count": len(path) - 1,
            "reached_target": reached,
            "manhattan_distances": distances,
        }
