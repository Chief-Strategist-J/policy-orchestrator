"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LOCAL PPR SWEEP-CUT CLUSTERING (ALGO-GRAPH-COMM-161)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Andersen-Chung-Lang (ACL) Local Graph Clustering via Personalized PageRank Sweep Cuts.
   Computes local forward push PPR vectors starting from a seed set, sorts vertices by
   degree-normalized probability p(u) / deg(u), and performs a sweep-cut to find
   the minimum conductance cut phi(S) = cut(S, S_bar) / min(vol(S), vol(S_bar)).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1 / (alpha * eps) + |S| log |S|) sublinear in total graph size.
   - Space Complexity: O(1 / (alpha * eps)) local active vector storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - seed: TNode - Target seed vertex for local clustering.
   - alpha: float - Teleportation constant (default: 0.15).
   - epsilon: float - Push residual resolution threshold (default: 1e-4).

4. OUTPUT PARAMETERS:
   - local_cluster_nodes: List[TNode] - Vertices comprising the minimal conductance local community.
   - min_conductance: float - Minimum Cheeger conductance phi(S) achieved along sweep.
   - cluster_volume: int - Total degree volume vol(S) of the extracted cluster.

5. AGENT CONTRACT:
   - Role: Analyst and Retriever.
   - Preconditions: Seed vertex must exist.
   - Guardrails: Sweep-cut evaluates prefixes strictly up to half the graph total volume.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLocalPprClustering(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-161
      name: GraphAlgoLocalPprClustering
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, local_clustering, ppr_sweep_cut, andersen_chung_lang, conductance]
      inputs:
        type: object
        required: [adjacency, seed]
        properties:
          adjacency: {type: object}
          seed: {type: string}
          alpha: {type: number, default: 0.15}
          epsilon: {type: number, default: 0.0001}
      outputs:
        type: object
        required: [local_cluster_nodes, min_conductance, cluster_volume]
        properties:
          local_cluster_nodes: {type: array, items: {type: string}}
          min_conductance: {type: number}
          cluster_volume: {type: integer}
      parameters:
        alpha: {type: number, default: 0.15}
        epsilon: {type: number, default: 0.0001}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(1 / (alpha * eps) + |S| log |S|)
        space: O(1 / (alpha * eps))
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        alpha: float = 0.15,
        epsilon: float = 1e-4,
    ) -> None:
        """
        Initialize the Local PPR Clustering engine.

        Args:
            adjacency: Graph adjacency dictionary.
            alpha: Teleportation probability.
            epsilon: Push resolution threshold.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._alpha: float = alpha
        self._eps: float = epsilon
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def extract_local_cluster(self, seed: TNode) -> Tuple[List[TNode], float, int]:
        """
        Perform local push PPR and sweep-cut to extract the local community around seed.

        Args:
            seed: Source seed vertex.

        Returns:
            Tuple of (local_cluster_nodes_list, min_conductance_score, cluster_degree_volume).
        """
        if seed not in self._adj:
            return [seed], 0.0, 0

        p: Dict[TNode, float] = {}
        r: Dict[TNode, float] = {seed: 1.0}
        q: Deque[TNode] = deque([seed])
        in_queue: Set[TNode] = {seed}

        while q:
            u = q.popleft()
            in_queue.remove(u)
            deg_u = len(self._adj.get(u, set()))
            r_u = r.get(u, 0.0)

            if r_u < self._eps * max(1, deg_u):
                continue

            p[u] = p.get(u, 0.0) + self._alpha * r_u
            push_mass = (1.0 - self._alpha) * r_u
            r[u] = 0.0

            if deg_u > 0:
                share = push_mass / float(deg_u)
                for v in self._adj[u]:
                    r[v] = r.get(v, 0.0) + share
                    deg_v = len(self._adj.get(v, set()))
                    if r[v] >= self._eps * max(1, deg_v) and v not in in_queue:
                        q.append(v)
                        in_queue.add(v)

        degrees = {u: len(self._adj.get(u, set())) for u in self._nodes}
        total_vol = sum(degrees.values())

        p_norm = [(u, p[u] / float(degrees[u])) for u in p if degrees[u] > 0]
        p_norm.sort(key=lambda item: (-item[1], str(item[0])))

        best_s: List[TNode] = [seed]
        min_cond: float = 1.0
        best_vol: int = degrees.get(seed, 0)

        current_s: Set[TNode] = set()
        vol_s: int = 0
        cut_edges: int = 0

        for u, _ in p_norm:
            current_s.add(u)
            deg_u = degrees[u]
            vol_s += deg_u

            internal_nbrs = len(self._adj.get(u, set()) & current_s)
            external_nbrs = deg_u - internal_nbrs
            cut_edges += external_nbrs - (internal_nbrs - 1)

            vol_other = total_vol - vol_s
            denom = min(vol_s, vol_other)
            if denom > 0:
                cond = float(cut_edges) / float(denom)
                if cond < min_cond:
                    min_cond = cond
                    best_s = list(current_s)
                    best_vol = vol_s

        return sorted(best_s, key=lambda x: str(x)), min_cond, best_vol
