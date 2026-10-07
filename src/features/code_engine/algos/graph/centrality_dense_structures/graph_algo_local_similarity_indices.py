"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LOCAL SIMILARITY INDICES (ALGO-GRAPH-SIM-115)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive local neighborhood similarity engine for link prediction and entity resolution.
   Computes Jaccard, Salton (Cosine), Sørensen-Dice, Hub-Promoted, Hub-Depressed,
   and Adamic-Adar common neighbor topological similarity coefficients.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(deg(u) + deg(v)) per query vertex pair.
   - Space Complexity: O(1) auxiliary per evaluation.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.

4. OUTPUT PARAMETERS:
   - jaccard: float - |N(u) cap N(v)| / |N(u) cup N(v)| in [0.0, 1.0].
   - salton_cosine: float - |N(u) cap N(v)| / sqrt(deg(u) * deg(v)).
   - sorensen: float - 2 * |N(u) cap N(v)| / (deg(u) + deg(v)).
   - hub_promoted: float - |N(u) cap N(v)| / min(deg(u), deg(v)).
   - hub_depressed: float - |N(u) cap N(v)| / max(deg(u), deg(v)).
   - adamic_adar: float - sum_{z in N(u) cap N(v)} 1 / log(deg(z)).

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Vertex pairs exist in graph.
   - Guardrails: Returns 0.0 similarity when neighbor sets are empty.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLocalSimilarityIndices(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SIM-115
      name: GraphAlgoLocalSimilarityIndices
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, similarity, jaccard, salton, sorensen, adamic_adar, link_prediction]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [jaccard, salton_cosine, sorensen, hub_promoted, hub_depressed, adamic_adar]
        properties:
          jaccard: {type: number}
          salton_cosine: {type: number}
          sorensen: {type: number}
          hub_promoted: {type: number}
          hub_depressed: {type: number}
          adamic_adar: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(d(u) + d(v))
        space: O(1)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Local Similarity index engine.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}

    def compute_pair_similarity(self, u: TNode, v: TNode) -> Dict[str, float]:
        """
        Compute all local neighborhood similarity indices for a specific vertex pair.

        Args:
            u: First vertex.
            v: Second vertex.

        Returns:
            Dictionary of calculated similarity metrics.
        """
        nbrs_u = self._adj.get(u, set())
        nbrs_v = self._adj.get(v, set())

        intersection = nbrs_u & nbrs_v
        union = nbrs_u | nbrs_v

        inter_size = float(len(intersection))
        union_size = float(len(union))
        deg_u = float(len(nbrs_u))
        deg_v = float(len(nbrs_v))

        jaccard = (inter_size / union_size) if union_size > 0 else 0.0
        salton = (inter_size / math.sqrt(deg_u * deg_v)) if (deg_u > 0 and deg_v > 0) else 0.0
        sorensen = (2.0 * inter_size / (deg_u + deg_v)) if (deg_u + deg_v) > 0 else 0.0
        min_deg = min(deg_u, deg_v)
        max_deg = max(deg_u, deg_v)
        hub_promoted = (inter_size / min_deg) if min_deg > 0 else 0.0
        hub_depressed = (inter_size / max_deg) if max_deg > 0 else 0.0

        adamic_adar: float = 0.0
        for z in intersection:
            deg_z = len(self._adj.get(z, set()))
            if deg_z > 1:
                adamic_adar += 1.0 / math.log(deg_z)

        return {
            "jaccard": jaccard,
            "salton_cosine": salton,
            "sorensen": sorensen,
            "hub_promoted": hub_promoted,
            "hub_depressed": hub_depressed,
            "adamic_adar": adamic_adar,
        }
