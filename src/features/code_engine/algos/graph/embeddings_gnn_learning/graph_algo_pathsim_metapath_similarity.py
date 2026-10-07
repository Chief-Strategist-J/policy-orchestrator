"""ALGORITHM & ARCHITECTURE BLUEPRINT: PATHSIM METAPATH-BASED PEER SIMILARITY (ALGO-GRAPH-RANK-291)

1. OVERVIEW & OBJECTIVE
PathSim (Sun et al.) evaluates peer similarity between same-type entities in heterogeneous information
networks (HINs) along symmetric metapaths P = (P_L P_R^{-1}) where P_L = P_R. By evaluating commuting
matrices M_P = W_1 W_2 ... W_l, PathSim computes normalized metapath-based similarity:
s(x, y) = 2 * M_P(x, y) / (M_P(x, x) + M_P(y, y)), balancing path count connectivity with peer volume.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V_same|^2) commuting matrix representation.
- Time Complexity: O(L * |V|^3) sparse matrix multiplication.
- Invariants:
  - Symmetric similarity: PathSim(x, y | P) = PathSim(y, x | P).
  - Self-similarity equals 1.0: PathSim(x, x | P) = 1.0.
  - PathSim is strictly bounded in [0.0, 1.0].

3. INPUT PARAMETERS:
- node_types: Mapping[TNode, str] entity type tag dictionary.
- relational_adjacency: Mapping[tuple[str, str], Mapping[TNode, Collection[TNode]]] typed adjacency.
- symmetric_metapath: Sequence[str] symmetric entity type sequence (e.g. ['Author', 'Paper', 'Author']).
- node_x: TNode first target entity.
- node_y: TNode second target entity.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'pathsim_score': float normalized PathSim similarity score in [0.0, 1.0].
  - 'path_count_xy': float path instance count between x and y.
  - 'self_path_count_x': float path instance count between x and x.
  - 'self_path_count_y': float path instance count between y and y.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPathsimMetapathSimilarity(Generic[TNode]):
    """PathSim metapath-based peer similarity for symmetric metapaths in HINs.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-291
      name: GraphAlgoPathsimMetapathSimilarity
      inputs:
        - name: node_types
          type: Mapping[TNode, str]
          description: Mapping of node identifiers to entity types.
        - name: relational_adjacency
          type: Mapping[tuple[str, str], Mapping[TNode, Collection[TNode]]]
          description: Typed adjacency map.
        - name: symmetric_metapath
          type: Sequence[str]
          description: Symmetric entity type sequence (e.g. ['Author', 'Paper', 'Author']).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: PathSim similarity score and component path counts.
      parameters:
        node_x: TNode
        node_y: TNode
      capability_tags:
        - HETEROGENEOUS_GRAPH
        - PATHSIM
        - METAPATH
        - PEER_SIMILARITY
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(L * |V|^3)
        space: O(|V|^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        node_types: Mapping[TNode, str],
        relational_adjacency: Mapping[Tuple[str, str], Mapping[TNode, Collection[TNode]]],
        symmetric_metapath: Sequence[str],
        node_x: TNode,
        node_y: TNode,
    ) -> Dict[str, Any]:
        """Evaluates PathSim score between node_x and node_y along symmetric_metapath."""
        path = list(symmetric_metapath)
        if len(path) < 2 or node_x not in node_types or node_y not in node_types:
            return {
                "pathsim_score": 0.0,
                "path_count_xy": 0.0,
                "self_path_count_x": 0.0,
                "self_path_count_y": 0.0,
            }

        count_xy = self._count_metapaths(node_x, node_y, path, relational_adjacency, node_types)
        count_xx = self._count_metapaths(node_x, node_x, path, relational_adjacency, node_types)
        count_yy = self._count_metapaths(node_y, node_y, path, relational_adjacency, node_types)

        denom = count_xx + count_yy
        if denom > 0.0:
            score = (2.0 * count_xy) / denom
        else:
            score = 0.0

        return {
            "pathsim_score": max(0.0, min(1.0, score)),
            "path_count_xy": count_xy,
            "self_path_count_x": count_xx,
            "self_path_count_y": count_yy,
        }

    def _count_metapaths(
        self,
        src: TNode,
        dst: TNode,
        metapath: List[str],
        rel_adj: Mapping[Tuple[str, str], Mapping[TNode, Collection[TNode]]],
        node_types: Mapping[TNode, str],
    ) -> float:
        """Counts the total number of metapath instances between src and dst."""
        dist: Dict[TNode, float] = {src: 1.0}

        for i in range(len(metapath) - 1):
            t_src = metapath[i]
            t_dst = metapath[i + 1]
            adj = rel_adj.get((t_src, t_dst), {})
            next_dist: Dict[TNode, float] = collections.defaultdict(float)

            for u, cnt in dist.items():
                nbrs = [v for v in adj.get(u, []) if node_types.get(v) == t_dst]
                for v in nbrs:
                    next_dist[v] += cnt

            dist = next_dist
            if not dist:
                break

        return dist.get(dst, 0.0)
