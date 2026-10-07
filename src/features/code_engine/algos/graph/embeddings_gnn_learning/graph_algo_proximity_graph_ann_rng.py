"""ALGORITHM & ARCHITECTURE BLUEPRINT: PROXIMITY GRAPH CONSTRUCTION FOR ANN SEARCH (RNG & VAMANA) (ALGO-GRAPH-NAV-295)

1. OVERVIEW & OBJECTIVE
Constructs navigable proximity graphs (Relative Neighborhood Graph / RNG rule and Vamana alpha-RNG rule from DiskANN)
for Approximate Nearest Neighbor (ANN) search over high-dimensional vector spaces. Implements greedy beam-search
routing and alpha-pruning: an edge (p, c) is added only if d(p, c) < alpha * d(c', c) for all already-selected
neighbors c', providing short graph diameters, bounded out-degrees, and high routing recall.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * R) where R is maximum out-degree.
- Time Complexity: O(|V| * L * d + |V| * R^2 * d) where L is beam search size.
- Invariants:
  - Pruning heuristic strictly limits maximum vertex out-degree to parameter R.
  - Parameter alpha >= 1.0 controls trade-off between local clustering and long-range shortcuts.

3. INPUT PARAMETERS:
- vectors: Mapping[TNode, Sequence[float]] high-dimensional node coordinate embeddings.
- r_max_degree: int maximum out-degree bound per vertex.
- l_search_list_size: int beam search candidate queue capacity.
- alpha: float pruning distance scaling factor (1.0 for RNG, 1.2-1.5 for Vamana).

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'graph_adjacency': Dict[TNode, List[TNode]] pruned navigable proximity graph.
  - 'medoid_entry_point': TNode calculated centroid/medoid entry vertex.
  - 'max_degree_observed': int highest out-degree in constructed graph.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import math
import random
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoProximityGraphAnnRng(Generic[TNode]):
    """Navigable Proximity Graph (Vamana / RNG) builder for high-dimensional Approximate Nearest Neighbor search.

    ```yaml
    contract:
      id: ALGO-GRAPH-NAV-295
      name: GraphAlgoProximityGraphAnnRng
      inputs:
        - name: vectors
          type: Mapping[TNode, Sequence[float]]
          description: High-dimensional vector coordinates for all nodes.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Constructed navigable graph adjacency and entry point medoid.
      parameters:
        r_max_degree: int (default 16)
        l_search_list_size: int (default 32)
        alpha: float (default 1.2)
        seed: int (default 42)
      capability_tags:
        - ANN_SEARCH
        - VAMANA
        - DISKANN
        - PROXIMITY_GRAPH
        - RNG_PRUNING
      purity: DETERMINISTIC_WITH_SEED
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V| * L * d + |V| * R^2 * d)
        space: O(|V| * R)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        vectors: Mapping[TNode, Sequence[float]],
        r_max_degree: int = 16,
        l_search_list_size: int = 32,
        alpha: float = 1.2,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Constructs Vamana navigable proximity graph with alpha-RNG pruning."""
        rng = random.Random(seed)
        nodes = list(vectors.keys())
        n = len(nodes)
        if n == 0:
            return {"graph_adjacency": {}, "medoid_entry_point": None, "max_degree_observed": 0}

        medoid = self._find_medoid(nodes, vectors)

        adj: Dict[TNode, List[TNode]] = {}
        for u in nodes:
            sample_nbrs = rng.sample([v for v in nodes if v != u], min(r_max_degree, n - 1)) if n > 1 else []
            adj[u] = sample_nbrs

        for u in nodes:
            visited_candidates = self._greedy_search(
                start_node=medoid,
                query_vec=vectors[u],
                k=l_search_list_size,
                adj=adj,
                vectors=vectors,
            )
            adj[u] = self._robust_prune(
                target_node=u,
                candidates=visited_candidates,
                r=r_max_degree,
                alpha=alpha,
                vectors=vectors,
            )

            for v in adj[u]:
                if len(adj[v]) >= r_max_degree:
                    combined_cand = set(adj[v]).union({u})
                    adj[v] = self._robust_prune(
                        target_node=v,
                        candidates=list(combined_cand),
                        r=r_max_degree,
                        alpha=alpha,
                        vectors=vectors,
                    )
                else:
                    if u not in adj[v]:
                        adj[v].append(u)

        max_deg = max((len(nbrs) for nbrs in adj.values()), default=0)

        return {
            "graph_adjacency": adj,
            "medoid_entry_point": medoid,
            "max_degree_observed": max_deg,
        }

    def _find_medoid(
        self, nodes: List[TNode], vectors: Mapping[TNode, Sequence[float]]
    ) -> TNode:
        """Finds central medoid vertex minimizing sum of squared distances to centroid."""
        d = len(vectors[nodes[0]])
        centroid = [0.0] * d
        for u in nodes:
            for i in range(d):
                centroid[i] += vectors[u][i] / float(len(nodes))

        best_node = nodes[0]
        best_dist = 1e18
        for u in nodes:
            dist = self._dist(vectors[u], centroid)
            if dist < best_dist:
                best_dist = dist
                best_node = u
        return best_node

    def _dist(self, v1: Sequence[float], v2: Sequence[float]) -> float:
        """Calculates Euclidean distance."""
        s = 0.0
        for a, b in zip(v1, v2):
            diff = float(a) - float(b)
            s += diff * diff
        return math.sqrt(s)

    def _greedy_search(
        self,
        start_node: TNode,
        query_vec: Sequence[float],
        k: int,
        adj: Dict[TNode, List[TNode]],
        vectors: Mapping[TNode, Sequence[float]],
    ) -> List[TNode]:
        """Greedy beam search on current graph."""
        visited: Set[TNode] = {start_node}
        candidates: List[Tuple[float, TNode]] = [(self._dist(vectors[start_node], query_vec), start_node)]

        while True:
            unexpanded = [c for c in candidates if c[1] in visited]
            if not unexpanded:
                break
            best_dist, curr = min(candidates, key=lambda x: x[0])
            for nbr in adj.get(curr, []):
                if nbr not in visited:
                    visited.add(nbr)
                    d = self._dist(vectors[nbr], query_vec)
                    candidates.append((d, nbr))
                    candidates.sort(key=lambda x: x[0])
                    if len(candidates) > k:
                        candidates = candidates[:k]
            break

        return [c[1] for c in candidates]

    def _robust_prune(
        self,
        target_node: TNode,
        candidates: List[TNode],
        r: int,
        alpha: float,
        vectors: Mapping[TNode, Sequence[float]],
    ) -> List[TNode]:
        """Alpha-RNG pruning heuristic."""
        target_vec = vectors[target_node]
        cand_with_d = [
            (self._dist(vectors[c], target_vec), c) for c in set(candidates) if c != target_node
        ]
        cand_with_d.sort(key=lambda x: x[0])

        selected: List[TNode] = []
        for d_p_c, c in cand_with_d:
            if len(selected) >= r:
                break
            c_vec = vectors[c]
            keep = True
            for s in selected:
                d_s_c = self._dist(vectors[s], c_vec)
                if alpha * d_s_c <= d_p_c:
                    keep = False
                    break
            if keep:
                selected.append(c)

        return selected
