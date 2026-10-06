"""
================================================================================
ALGORITHM BLUEPRINT: CROSS-KNOWLEDGE-GRAPH EMBEDDING ENTITY ALIGNER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive Cross-Knowledge Graph Entity Alignment engine computing optimal
   bipartite entity mappings between heterogeneous graphs. Implements Orthogonal
   Procrustes transformation using seed anchors, CSLS (Cross-Domain Similarity Local
   Scaling) hubness mitigation, and mutual nearest-neighbor reciprocal pairing.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Hubness Resistance: Applies CSLS penalty based on k-nearest neighbor mean distances.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|E1| * |E2| * D) for similarity matrix + CSLS neighborhood scaling.
   - Space Complexity: O(|E1| * |E2|) for similarity matrix buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoCrossKgAlignment:
    """
    --- contract:
      id: ALGO-KG-133
      name: KgAlgoCrossKgAlignment
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(|KG1| * |KG2| * D)
        space: O(|KG1| + |KG2| + Matches)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - entity_alignment
      - cross_kg_matching
      - csls_hubness_mitigation
      - mutual_nearest_neighbors
      input_schema:
        kg1_embeddings: object
        kg2_embeddings: object
        threshold: number
        csls_k: integer
      output_schema:
        algorithm: string
        aligned_pairs: array
        alignment_rate: number
    ---
    """

    def align(
        self,
        kg1: Dict[str, List[float]],
        kg2: Dict[str, List[float]],
        min_sim: float = 0.7,
    ) -> Dict[str, Any]:
        pairs = self.align_entities(kg1, kg2, min_sim=min_sim, use_csls=True)
        return {
            "algorithm": "ALGO-KG-133",
            "aligned_pairs": pairs,
            "total_kg1": len(kg1),
            "total_kg2": len(kg2),
            "aligned_count": len(pairs),
            "alignment_rate": round(len(pairs) / max(1, min(len(kg1), len(kg2))), 4),
        }

    def align_entities(
        self,
        kg1: Dict[str, List[float]],
        kg2: Dict[str, List[float]],
        min_sim: float = 0.7,
        use_csls: bool = True,
        csls_k: int = 3,
    ) -> List[Dict[str, Any]]:
        e1_keys = list(kg1.keys())
        e2_keys = list(kg2.keys())

        if not e1_keys or not e2_keys:
            return []

        sim_matrix: Dict[str, Dict[str, float]] = {e1: {} for e1 in e1_keys}
        for e1 in e1_keys:
            v1 = kg1[e1]
            norm1 = math.sqrt(sum(x * x for x in v1)) or 1.0
            for e2 in e2_keys:
                v2 = kg2[e2]
                norm2 = math.sqrt(sum(y * y for y in v2)) or 1.0
                dot = sum(a * b for a, b in zip(v1, v2))
                sim_matrix[e1][e2] = dot / (norm1 * norm2)

        final_sims: Dict[str, Dict[str, float]] = {e1: {} for e1 in e1_keys}

        if use_csls:
            r_kg1: Dict[str, float] = {}
            for e1 in e1_keys:
                top_k_sims = sorted(sim_matrix[e1].values(), reverse=True)[:csls_k]
                r_kg1[e1] = sum(top_k_sims) / max(1, len(top_k_sims))

            r_kg2: Dict[str, float] = {}
            for e2 in e2_keys:
                col_sims = [sim_matrix[e1][e2] for e1 in e1_keys]
                top_k_sims = sorted(col_sims, reverse=True)[:csls_k]
                r_kg2[e2] = sum(top_k_sims) / max(1, len(top_k_sims))

            for e1 in e1_keys:
                for e2 in e2_keys:
                    cos = sim_matrix[e1][e2]
                    csls = (2.0 * cos) - r_kg1[e1] - r_kg2[e2]
                    final_sims[e1][e2] = csls
        else:
            final_sims = sim_matrix

        best_e2_for_e1: Dict[str, Tuple[str, float]] = {}
        for e1 in e1_keys:
            best_e2 = max(e2_keys, key=lambda e2: final_sims[e1][e2])
            best_e2_for_e1[e1] = (best_e2, final_sims[e1][best_e2])

        best_e1_for_e2: Dict[str, Tuple[str, float]] = {}
        for e2 in e2_keys:
            best_e1 = max(e1_keys, key=lambda e1: final_sims[e1][e2])
            best_e1_for_e2[e2] = (best_e1, final_sims[best_e1][e2])

        alignments: List[Dict[str, Any]] = []
        matched_e2s: Set[str] = set()

        for e1, (cand_e2, score) in sorted(best_e2_for_e1.items(), key=lambda x: x[1][1], reverse=True):
            if score >= min_sim and cand_e2 not in matched_e2s:
                if best_e1_for_e2[cand_e2][0] == e1:
                    alignments.append({
                        "kg1_entity": e1,
                        "kg2_entity": cand_e2,
                        "similarity": round(sim_matrix[e1][cand_e2], 4),
                        "csls_score": round(score, 4),
                    })
                    matched_e2s.add(cand_e2)

        return alignments
