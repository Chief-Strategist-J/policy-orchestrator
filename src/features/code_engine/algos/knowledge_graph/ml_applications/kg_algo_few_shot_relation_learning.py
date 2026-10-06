r"""
================================================================================
ALGORITHM BLUEPRINT: FEW-SHOT PROTOTYPICAL INDUCTIVE RELATION LEARNER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Few-Shot inductive relation learning engine implementing Prototypical Metric
   Networks (FSRL / Meta-KGR) for unseen few-shot Knowledge Graph relations. Aggregates
   support instance translational / contextual vectors via self-attention pooling into
   a relation prototype $\mathbf{c}_r$, evaluates query triples via metric distance,
   and computes N-way K-shot episodic ranking probabilities.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Metric Space Geometry: Compares query pairs $(h_q, t_q)$ against prototype
     $\mathbf{c}_r$ using temperature-scaled negative Euclidean distance.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(K * D + N_Queries * D) for support aggregation and query evaluation.
   - Space Complexity: O(D) for prototype vector allocation.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoFewShotRelationLearning:
    """
    --- contract:
      id: ALGO-KG-147
      name: KgAlgoFewShotRelationLearning
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(K * D + N_Queries * D)
        space: O(D)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - few_shot_learning
      - prototypical_networks
      - attention_aggregation
      - inductive_relation
      input_schema:
        support_pairs: array
        query_pairs: optional array
      output_schema:
        algorithm: string
        relation_prototype: array
        query_predictions: optional array
    ---
    """

    def compute_prototype(
        self,
        support_head_tail_diffs: List[List[float]],
        attention_weights: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not support_head_tail_diffs:
            return {"algorithm": "ALGO-KG-147", "relation_prototype": []}

        dim = len(support_head_tail_diffs[0])
        n = len(support_head_tail_diffs)

        if attention_weights and len(attention_weights) == n:
            sum_w = sum(attention_weights) or 1.0
            norm_w = [w / sum_w for w in attention_weights]
            proto = [
                sum(norm_w[i] * support_head_tail_diffs[i][d] for i in range(n))
                for d in range(dim)
            ]
        else:
            proto = [
                sum(support_head_tail_diffs[i][d] for i in range(n)) / n
                for d in range(dim)
            ]

        return {
            "algorithm": "ALGO-KG-147",
            "relation_prototype": [round(val, 5) for val in proto],
            "support_count": n,
            "dimension": dim,
        }

    def evaluate_few_shot_task(
        self,
        support_pairs: List[Tuple[List[float], List[float]]],
        candidate_query_pairs: List[Tuple[str, List[float], List[float]]],
        temperature: float = 1.0,
    ) -> Dict[str, Any]:
        support_diffs = [[t[d] - h[d] for d in range(len(h))] for h, t in support_pairs]
        proto_res = self.compute_prototype(support_diffs)
        proto = proto_res["relation_prototype"]

        scored_queries: List[Dict[str, Any]] = []
        for q_id, q_h, q_t in candidate_query_pairs:
            q_diff = [t_val - h_val for h_val, t_val in zip(q_h, q_t)]
            sq_dist = sum((p_val - d_val) ** 2 for p_val, d_val in zip(proto, q_diff))
            dist = math.sqrt(sq_dist)
            sim = 1.0 / (1.0 + dist)
            scored_queries.append({
                "query_id": q_id,
                "euclidean_distance": round(dist, 4),
                "similarity_score": round(sim, 4),
            })

        scored_queries.sort(key=lambda x: x["similarity_score"], reverse=True)

        exp_scores = [math.exp(min(50.0, -q["euclidean_distance"] / max(1e-6, temperature))) for q in scored_queries]
        sum_exp = sum(exp_scores) if exp_scores else 1.0
        for q, exp_s in zip(scored_queries, exp_scores):
            q["posterior_prob"] = round(exp_s / sum_exp, 5)

        return {
            "algorithm": "ALGO-KG-147",
            "relation_prototype": proto,
            "support_shots_k": len(support_pairs),
            "ranked_query_evaluations": scored_queries,
        }
