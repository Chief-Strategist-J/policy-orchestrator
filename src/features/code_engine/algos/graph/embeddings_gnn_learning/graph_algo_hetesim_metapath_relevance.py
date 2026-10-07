"""ALGORITHM & ARCHITECTURE BLUEPRINT: HETESIM METAPATH-BASED RELEVANCE (ALGO-GRAPH-RANK-290)

1. OVERVIEW & OBJECTIVE
HeteSim (Shi et al.) measures the semantic relevance between two same-type or different-type entities
in heterogeneous information networks (HINs) along arbitrary composite metapaths P = (A_1 A_2 ... A_{l+1}).
By decomposing metapaths into dual forward/backward transition matrices and computing cosine similarity at
the middle meeting subpath, HeteSim delivers a symmetric, normalized relevance score in [0.0, 1.0].

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V_1| * |V_{mid}| + |V_2| * |V_{mid}|) for transition probability matrices.
- Time Complexity: O(L * |V|^3) sparse matrix multiplication across metapath segments.
- Invariants:
  - HeteSim relevance is bounded: 0.0 <= HeteSim(s, t | P) <= 1.0.
  - Self-relevance along symmetric metapath equals 1.0: HeteSim(s, s | P) = 1.0.

3. INPUT PARAMETERS:
- node_types: Mapping[TNode, str] entity type tag dictionary.
- relational_adjacency: Mapping[tuple[str, str], Mapping[TNode, Collection[TNode]]] relation typed adjacency.
- metapath: Sequence[str] ordered list of node types defining composite path (e.g. ['Author', 'Paper', 'Author']).
- source_node: TNode source entity node s of type metapath[0].
- target_node: TNode target entity node t of type metapath[-1].

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'relevance_score': float normalized HeteSim semantic similarity in [0.0, 1.0].
  - 'metapath': List[str] evaluated entity sequence.
  - 'intermediate_dims': List[int] node counts at each metapath hop.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHetesimMetapathRelevance(Generic[TNode]):
    """HeteSim symmetric relevance metric along arbitrary metapaths in Heterogeneous Information Networks.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-290
      name: GraphAlgoHetesimMetapathRelevance
      inputs:
        - name: node_types
          type: Mapping[TNode, str]
          description: Mapping of node identifiers to entity types.
        - name: relational_adjacency
          type: Mapping[tuple[str, str], Mapping[TNode, Collection[TNode]]]
          description: Adjacency dictionary keyed by (src_type, dst_type).
        - name: metapath
          type: Sequence[str]
          description: Sequence of entity types defining the metapath.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Computed HeteSim relevance score and intermediate statistics.
      parameters:
        source_node: TNode
        target_node: TNode
      capability_tags:
        - HETEROGENEOUS_GRAPH
        - HETESIM
        - METAPATH
        - RELEVANCE_MEASURE
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(L * |V|^3)
        space: O(|V| * |V_mid|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        node_types: Mapping[TNode, str],
        relational_adjacency: Mapping[Tuple[str, str], Mapping[TNode, Collection[TNode]]],
        metapath: Sequence[str],
        source_node: TNode,
        target_node: TNode,
    ) -> Dict[str, Any]:
        """Calculates HeteSim relevance score along composite metapath."""
        path = list(metapath)
        l_len = len(path) - 1
        if l_len <= 0 or source_node not in node_types or target_node not in node_types:
            return {"relevance_score": 0.0, "metapath": path, "intermediate_dims": []}

        mid_idx = l_len // 2
        path_left = path[: mid_idx + 1]
        path_right = list(reversed(path[mid_idx:]))

        p_left = self._compute_transition_vector(
            source_node, path_left, relational_adjacency, node_types
        )
        p_right = self._compute_transition_vector(
            target_node, path_right, relational_adjacency, node_types
        )

        all_mid_nodes = set(p_left.keys()).union(p_right.keys())
        if not all_mid_nodes:
            return {"relevance_score": 0.0, "metapath": path, "intermediate_dims": []}

        dot_prod = sum(p_left.get(u, 0.0) * p_right.get(u, 0.0) for u in all_mid_nodes)
        norm_left = math.sqrt(sum(v * v for v in p_left.values()))
        norm_right = math.sqrt(sum(v * v for v in p_right.values()))

        if norm_left > 0.0 and norm_right > 0.0:
            hetesim_score = dot_prod / (norm_left * norm_right)
        else:
            hetesim_score = 0.0

        return {
            "relevance_score": max(0.0, min(1.0, hetesim_score)),
            "metapath": path,
            "intermediate_dims": [len(p_left), len(p_right)],
        }

    def _compute_transition_vector(
        self,
        start_node: TNode,
        sub_path: List[str],
        rel_adj: Mapping[Tuple[str, str], Mapping[TNode, Collection[TNode]]],
        node_types: Mapping[TNode, str],
    ) -> Dict[TNode, float]:
        """Propagates normalized transition probabilities along a sub-path."""
        dist: Dict[TNode, float] = {start_node: 1.0}

        for i in range(len(sub_path) - 1):
            t_src = sub_path[i]
            t_dst = sub_path[i + 1]
            adj = rel_adj.get((t_src, t_dst), {})
            next_dist: Dict[TNode, float] = collections.defaultdict(float)

            for u, prob_u in dist.items():
                nbrs = [v for v in adj.get(u, []) if node_types.get(v) == t_dst]
                if nbrs:
                    step_p = prob_u / float(len(nbrs))
                    for v in nbrs:
                        next_dist[v] += step_p

            dist = next_dist
            if not dist:
                break

        return dist
