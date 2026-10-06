r"""
================================================================================
ALGORITHM BLUEPRINT: UNCERTAINTY & DIVERSITY SAMPLING FOR ACTIVE KG CURATION
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph active learning curation engine. Identifies the
   most informative candidate triples/facts from model prediction uncertainty
   (Margin Sampling, Shannon Entropy, Least Confidence) and committee disagreement,
   prioritizing high-entropy facts for human expert annotation.

2. FORMAL MATHEMATICAL SPECIFICATION:
   - Least Confidence:
       $U_{LC}(x) = \frac{K}{K-1} (1 - \max_y P(y|x))$
   - Margin Sampling:
       $U_{Margin}(x) = 1 - (P(\hat{y}_1|x) - P(\hat{y}_2|x))$
   - Shannon Entropy:
       $H(x) = -\sum_{k=1}^K P(y_k|x) \log_2 P(y_k|x)$
   - Committee Disagreement (Vote Entropy):
       $D_{VE}(x) = -\sum_{k} \frac{V(y_k, x)}{C} \log_2 \frac{V(y_k, x)}{C}$

3. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inline Comments: Code logic is self-documenting.
   - Purity & Determinism: Pure functional state transitions.

4. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N log N) where N is pool size.
   - Space Complexity: O(B) where B is annotation budget.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoActiveLearningCuration:
    """
    --- contract:
      id: ALGO-KG-148
      name: KgAlgoActiveLearningCuration
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Pool log Pool)
        space: O(Budget)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - active_learning
      - uncertainty_sampling
      - expert_curation
      input_schema:
        predictions: object
        budget: integer
      output_schema:
        algorithm: string
        selected_for_review: array
    ---
    """
    def sample_uncertain_facts(self, pred_probabilities: Dict[str, float], budget: int = 5) -> Dict[str, Any]:
        scored = [(fact, abs(prob - 0.5)) for fact, prob in pred_probabilities.items()]
        scored.sort(key=lambda x: x[1])
        return {
            "algorithm": "ALGO-KG-148",
            "selected_for_review": [s[0] for s in scored[:budget]],
        }

    def curate_active_batch(
        self,
        candidate_facts: List[Dict[str, Any]],
        strategy: str = "entropy",
        budget: int = 10,
    ) -> Dict[str, Any]:
        scored_candidates: List[Tuple[float, Dict[str, Any]]] = []
        for cand in candidate_facts:
            probs = cand.get("class_probabilities", [])
            binary_prob = cand.get("probability", 0.5)
            if not probs:
                probs = [binary_prob, 1.0 - binary_prob]
            total_p = sum(probs)
            if total_p > 0:
                normalized = [p / total_p for p in probs]
            else:
                normalized = [1.0 / len(probs)] * len(probs)
            
            if strategy == "entropy":
                uncertainty = -sum(p * math.log2(p + 1e-12) for p in normalized if p > 0)
            elif strategy == "margin":
                sorted_p = sorted(normalized, reverse=True)
                top1 = sorted_p[0] if len(sorted_p) > 0 else 0.5
                top2 = sorted_p[1] if len(sorted_p) > 1 else 0.0
                uncertainty = 1.0 - (top1 - top2)
            elif strategy == "least_confidence":
                max_p = max(normalized) if normalized else 0.5
                k = len(normalized)
                uncertainty = (k / max(k - 1, 1)) * (1.0 - max_p)
            else:
                uncertainty = 1.0 - abs(binary_prob - 0.5) * 2.0

            scored_candidates.append((uncertainty, cand))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        selected = [c for _, c in scored_candidates[:budget]]
        return {
            "algorithm": "ALGO-KG-148",
            "strategy": strategy,
            "budget": budget,
            "selected_candidates": selected,
            "mean_uncertainty": sum(u for u, _ in scored_candidates[:budget]) / max(len(selected), 1),
        }

