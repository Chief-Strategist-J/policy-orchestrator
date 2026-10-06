r"""
================================================================================
ALGORITHM BLUEPRINT: KNOWLEDGE GRAPH MULTI-HOP RIPPLE RECOMMENDER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Knowledge Graph collaborative recommendation engine implementing multi-hop
   preference propagation (RippleNet / KGCN). Propagates user historical preferences
   outward along KG relation paths, applies relation-aware decay penalties across
   hops, prunes previously consumed items, and produces explainable recommendation
   reasoning paths linking user historical items to candidates.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Consumption Filtering: Items already in user history are strictly excluded.
   - Hop Exponential Decay: Multi-hop signals decay geometrically with factor $\gamma^h$.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Hops * |History| * Average_Degree) for preference ripple BFS.
   - Space Complexity: O(|Candidates| + Hops * Paths) for candidate score and path buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoKgRecommender:
    """
    --- contract:
      id: ALGO-KG-138
      name: KgAlgoKgRecommender
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Hops * |History| * Degree)
        space: O(|Candidates| + Paths)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - kg_recommender
      - ripplenet_propagation
      - multi_hop_reasoning
      - explainable_recommendation
      input_schema:
        user_history: array
        kg_triples: array
        max_hops: integer
      output_schema:
        algorithm: string
        recommendations: array
        total_candidates_scored: integer
    ---
    """

    def recommend(
        self,
        user_id: str,
        user_history: List[str],
        kg_triples: List[Tuple[str, str, str]],
        max_hops: int = 2,
        decay_factor: float = 0.5,
        relation_weights: Optional[Dict[str, float]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        history_set = set(user_history)
        r_weights = relation_weights or {}

        adj: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        for s, p, o in kg_triples:
            adj[s].append((p, o))
            adj[o].append((p, s))

        candidate_scores: Dict[str, float] = defaultdict(float)
        explanation_paths: Dict[str, List[str]] = {}

        current_ripple: Dict[str, float] = {item: 1.0 for item in history_set}
        ripple_origins: Dict[str, List[str]] = {item: [item] for item in history_set}

        for hop in range(1, max_hops + 1):
            next_ripple: Dict[str, float] = defaultdict(float)
            next_origins: Dict[str, List[str]] = {}

            for entity, intensity in current_ripple.items():
                curr_path = ripple_origins.get(entity, [entity])
                for rel, neighbor in adj.get(entity, []):
                    rel_weight = r_weights.get(rel, 1.0)
                    step_score = intensity * decay_factor * rel_weight

                    if neighbor not in history_set:
                        candidate_scores[neighbor] += step_score
                        if neighbor not in explanation_paths or step_score > candidate_scores[neighbor] * 0.5:
                            explanation_paths[neighbor] = curr_path + [f"--[{rel}]--> {neighbor}"]

                    if step_score > next_ripple[neighbor]:
                        next_ripple[neighbor] = step_score
                        next_origins[neighbor] = curr_path + [f"--[{rel}]--> {neighbor}"]

            current_ripple = next_ripple
            ripple_origins = next_origins
            if not current_ripple:
                break

        ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        formatted_recs = []
        for rank_idx, (item, score) in enumerate(ranked, start=1):
            path_str = " ".join(explanation_paths.get(item, [item]))
            formatted_recs.append({
                "rank": rank_idx,
                "item": item,
                "score": round(score, 4),
                "explanation_path": path_str,
            })

        return {
            "algorithm": "ALGO-KG-138",
            "user_id": user_id,
            "recommendations": formatted_recs,
            "total_candidates_scored": len(candidate_scores),
        }

    def recommend_items(
        self,
        user_items: Set[str],
        item_connections: List[Tuple[str, str]],
        top_k: int = 3,
    ) -> Dict[str, Any]:
        triples = [(u, "connected_to", v) for u, v in item_connections]
        res = self.recommend(
            user_id="anonymous_user",
            user_history=list(user_items),
            kg_triples=triples,
            max_hops=1,
            top_k=top_k,
        )
        return {
            "algorithm": "ALGO-KG-138",
            "recommendations": [r["item"] for r in res["recommendations"]],
        }
