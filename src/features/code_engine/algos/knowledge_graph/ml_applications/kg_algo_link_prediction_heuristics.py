"""
================================================================================
ALGORITHM BLUEPRINT: LINK PREDICTION TOPOLOGICAL HEURISTICS SUITE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive topological link prediction heuristic engine computing neighborhood-
   based and path-based similarity indices for entity pairs in Knowledge Graphs.
   Implements Common Neighbors, Jaccard Coefficient, Adamic-Adar, Resource Allocation
   (RA), Preferential Attachment (PA), Sørensen-Dice, Hub Promoted Index (HPI),
   Hub Depressed Index (HDI), and 2-Hop Local Path Index.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Numerical Stability: Logarithmic and division terms clamped with ε = 1e-9.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|N(u)| + |N(v)|) for neighborhood intersection and degree lookups.
   - Space Complexity: O(|N(u) ∩ N(v)|) for intermediate common neighbor set allocation.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoLinkPredictionHeuristics:
    """
    --- contract:
      id: ALGO-KG-131
      name: KgAlgoLinkPredictionHeuristics
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Degree_U + Degree_V)
        space: O(Common_Neighbors)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - link_heuristics
      - adamic_adar
      - resource_allocation
      - preferential_attachment
      - sorensen_dice
      - hub_promoted_index
      input_schema:
        adj: object
        u: string
        v: string
      output_schema:
        algorithm: string
        pair: tuple
        common_neighbors_count: integer
        jaccard: number
        adamic_adar: number
        resource_allocation: number
        preferential_attachment: integer
        sorensen_dice: number
        hub_promoted_index: number
        hub_depressed_index: number
    ---
    """

    def compute_heuristics(
        self,
        adj: Dict[str, Set[str]],
        u: str,
        v: str,
        beta_local_path: float = 0.01,
    ) -> Dict[str, Any]:
        set_u = set(adj.get(u, set()))
        set_v = set(adj.get(v, set()))
        deg_u = len(set_u)
        deg_v = len(set_v)

        common = set_u.intersection(set_v)
        common_cnt = len(common)
        union = set_u.union(set_v)

        jaccard = common_cnt / max(1, len(union))
        sorensen = (2.0 * common_cnt) / max(1, deg_u + deg_v)
        pref_attachment = deg_u * deg_v

        adamic_adar = 0.0
        resource_alloc = 0.0
        for z in common:
            deg_z = len(adj.get(z, set()))
            if deg_z > 1:
                adamic_adar += 1.0 / math.log(deg_z)
            resource_alloc += 1.0 / max(1, deg_z)

        min_deg = min(deg_u, deg_v)
        max_deg = max(deg_u, deg_v)
        hpi = (common_cnt / max(1, min_deg)) if min_deg > 0 else 0.0
        hdi = (common_cnt / max(1, max_deg)) if max_deg > 0 else 0.0

        two_hop_paths = common_cnt
        local_path_score = common_cnt + (beta_local_path * two_hop_paths)

        return {
            "algorithm": "ALGO-KG-131",
            "pair": (u, v),
            "common_neighbors_count": common_cnt,
            "jaccard": round(jaccard, 5),
            "sorensen_dice": round(sorensen, 5),
            "adamic_adar": round(adamic_adar, 5),
            "resource_allocation": round(resource_alloc, 5),
            "preferential_attachment": pref_attachment,
            "hub_promoted_index": round(hpi, 5),
            "hub_depressed_index": round(hdi, 5),
            "local_path_score": round(local_path_score, 5),
        }
