"""
================================================================================
ALGORITHM BLUEPRINT: KNOWLEDGE GRAPH COMPLETION INFERENCE PIPELINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Production-grade Knowledge Graph Completion (KGC) inference pipeline executing
   filtered-setting link prediction for (h, r, ?) tail completion and (?, r, t)
   head completion queries. Implements candidate entity generation, ontology domain/
   range type constraint filtering, model score aggregation (translational or bilinear),
   known-fact filtering to prevent false-negative ranking degradation, and calibration
   to posterior probabilities.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Filtered Ranking Setting: All known true triples (excluding target test triple)
     are filtered from candidate rankings (standard Bordes et al. protocol).
   - Type Invariance: Candidates violating schema domain/range constraints are
     penalized or pruned prior to expensive model evaluations.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|C| * D) where |C| is candidate entity set size and D is embedding dimension.
   - Space Complexity: O(|C| + Top_K) for candidate scores and ranked result buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoKgCompletionPipeline:
    """
    --- contract:
      id: ALGO-KG-132
      name: KgAlgoKgCompletionPipeline
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Candidates * Model_Eval)
        space: O(Candidates + Top_K)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - kg_completion
      - filtered_link_prediction
      - ontology_type_filtering
      - confidence_calibration
      input_schema:
        head: string
        rel: string
        tail: optional string
        candidates: array
        known_triples: optional array
        entity_types: optional object
        relation_constraints: optional object
      output_schema:
        algorithm: string
        query: string
        ranked_completions: array
        filtered_candidate_count: integer
        metrics: optional object
    ---
    """

    def complete_tail(
        self,
        head: str,
        rel: str,
        candidates_with_scores: List[Tuple[str, float]],
        top_k: int = 3,
    ) -> Dict[str, Any]:
        sorted_cands = sorted(candidates_with_scores, key=lambda x: x[1], reverse=True)[:top_k]
        return {
            "algorithm": "ALGO-KG-132",
            "query": f"({head}, {rel}, ?)",
            "ranked_completions": [
                {"tail": c[0], "confidence": round(c[1], 4)} for c in sorted_cands
            ],
        }

    def predict_completion(
        self,
        head: Optional[str],
        relation: str,
        tail: Optional[str],
        candidate_entities: List[str],
        score_fn: Callable[[str, str, str], float],
        known_triples: Optional[Set[Tuple[str, str, str]]] = None,
        entity_types: Optional[Dict[str, List[str]]] = None,
        relation_constraints: Optional[Dict[str, Dict[str, List[str]]]] = None,
        target_ground_truth: Optional[str] = None,
        top_k: int = 10,
        temperature: float = 1.0,
    ) -> Dict[str, Any]:
        is_tail_query = head is not None and tail is None
        is_head_query = head is None and tail is not None

        if not is_tail_query and not is_head_query:
            query_str = f"({head or '?'}, {relation}, {tail or '?'})"
            return {
                "algorithm": "ALGO-KG-132",
                "query": query_str,
                "error": "Query must specify exactly one unknown entity (head or tail).",
                "ranked_completions": [],
            }

        known = known_triples or set()
        e_types = entity_types or {}
        r_constraints = relation_constraints or {}

        allowed_types: Optional[Set[str]] = None
        if relation in r_constraints:
            expected_key = "range" if is_tail_query else "domain"
            type_list = r_constraints[relation].get(expected_key)
            if type_list:
                allowed_types = set(type_list)

        filtered_candidates: List[str] = []
        for candidate in candidate_entities:
            test_triple = (head, relation, candidate) if is_tail_query else (candidate, relation, tail)
            if test_triple in known and candidate != target_ground_truth:
                continue

            if allowed_types is not None:
                cand_types = set(e_types.get(candidate, []))
                if cand_types and not (cand_types & allowed_types):
                    continue

            filtered_candidates.append(candidate)

        raw_scores: List[Tuple[str, float]] = []
        for cand in filtered_candidates:
            h = head if is_tail_query else cand
            t = cand if is_tail_query else tail
            score = score_fn(h, relation, t)
            raw_scores.append((cand, score))

        raw_scores.sort(key=lambda x: x[1], reverse=True)

        exp_scores = [math.exp(min(50.0, max(-50.0, s / max(1e-6, temperature)))) for _, s in raw_scores]
        sum_exp = sum(exp_scores) if exp_scores else 1.0
        probabilities = [round(e / sum_exp, 5) for e in exp_scores]

        ranked_completions: List[Dict[str, Any]] = []
        ground_truth_rank: Optional[int] = None

        for rank_idx, ((cand, raw_s), prob) in enumerate(zip(raw_scores, probabilities), start=1):
            if target_ground_truth and cand == target_ground_truth and ground_truth_rank is None:
                ground_truth_rank = rank_idx

            if rank_idx <= top_k:
                ranked_completions.append({
                    "rank": rank_idx,
                    "candidate": cand,
                    "raw_score": round(raw_s, 4),
                    "probability": prob,
                    "types": e_types.get(cand, []),
                })

        query_repr = f"({head}, {relation}, ?)" if is_tail_query else f"(?, {relation}, {tail})"
        metrics: Dict[str, Any] = {}
        if target_ground_truth:
            rank_val = ground_truth_rank or (len(filtered_candidates) + 1)
            metrics = {
                "target_entity": target_ground_truth,
                "filtered_rank": rank_val,
                "reciprocal_rank": round(1.0 / rank_val, 4),
                "hits_at_1": 1 if rank_val <= 1 else 0,
                "hits_at_3": 1 if rank_val <= 3 else 0,
                "hits_at_10": 1 if rank_val <= 10 else 0,
            }

        return {
            "algorithm": "ALGO-KG-132",
            "query": query_repr,
            "total_candidates": len(candidate_entities),
            "filtered_candidate_count": len(filtered_candidates),
            "ranked_completions": ranked_completions,
            "metrics": metrics if metrics else None,
        }
